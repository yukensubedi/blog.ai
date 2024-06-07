import pathlib
import textwrap
import re
import requests
import io
import markdown 
import openai
from openai import OpenAI

import google.generativeai as genai

from IPython.display import display
from IPython.display import Markdown
from django.shortcuts import render, redirect
from django.http import HttpResponse, StreamingHttpResponse, HttpResponseRedirect

from django.conf import settings
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.db import transaction

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import TemplateView, FormView, DetailView, ListView
from django.views.generic.edit import FormMixin, UpdateView, DeleteView

from django.shortcuts import get_object_or_404
from django.db import transaction

from django.core.management import call_command

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.files.base import ContentFile
from django.contrib.contenttypes.models import ContentType



import tiktoken
from . forms import *
from .models import *
from .tasks import *
from filemanager.models import *

from .shortcodes import process_shortcodes

client = OpenAI(api_key=getattr(settings, 'OPENAI_API_KEY'))
DEFAULT_GENERATION_CONFIG = {
  "temperature": 0.9,
  "top_p": 1,
  "max_output_tokens": 2048,
  "model": "gpt-3.5-turbo-0125"
}



genai.configure(api_key= getattr(settings, 'GOOGLE_API_KEY'))


def test(request):   
    template_name = 'assistant/test.html'
    print(getattr(settings, 'OPENAI_API_KEY'))
    if request.method == 'POST':
        # todo 
        # yo kura lai contact form ma lane 
        res =  request.POST.get('g-recaptcha-response')
        

        data = {
            'response': res,
            'secret': "6Lck4OMpAAAAALkRcELQfW5Z0cRo82Z_b2IMynTE"
        }
        
        resp = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result_json = resp.json()
        if not result_json.get('success'):
            return HttpResponse('You are not human ')
        
        else:
            return HttpResponse(resp)
        
    return render(request, template_name, {'site_key': settings.RECAPTCHA_SITE_KEY})

class HomeView(LoginRequiredMixin, TemplateView):
     template_name = 'assistant/index.html'

   

def regenerate(request, prompt, generation_config, title= None):
    # generation_config = request.session.get('generation_config_blog_topics', DEFAULT_GENERATION_CONFIG)
    print(generation_config)
    prompt_parts = f'Regenerate {prompt}'
    try:
        completion = client.chat.completions.create(
                        model="gpt-3.5-turbo-0125",
                        messages=[
                            {"role": "system", "content": "You are  helpful blog writing assistant."},
                            {"role": "user", "content": prompt_parts}
                        ],
                    
                        max_tokens= generation_config['max_output_tokens'],
                        temperature=generation_config['temperature'],
                        top_p=generation_config['top_p'],
                    )        
        response =  completion.choices[0].message.content
        if title:
            History.objects.create(user=request.user, title=title, body=response, prompt = prompt_parts)
        return response
    except Exception as e:
                return HttpResponse(f'{type(e).__name__}: {e}')

def generate_image(request, prompt, number_of_photos):
    response = client.images.generate(
        model="dall-e-3",
        prompt= prompt,
        n= number_of_photos,
        size="1024x1024", 
        style = "natural"
    )
    data = response.json()
    response_data = json.loads(data)

    # Extracting URLs from the response
    image_url = [image['url'] for image in response_data['data']]
    return image_url

def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613"):
    """Return the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model in {
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-16k-0613",
        "gpt-4-0314",
        "gpt-4-32k-0314",
        "gpt-4-0613",
        "gpt-4-32k-0613",
        }:
        tokens_per_message = 3
        tokens_per_name = 1
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif "gpt-3.5-turbo" in model:
        print("Warning: gpt-3.5-turbo may update over time. Returning num tokens assuming gpt-3.5-turbo-0613.")
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
    elif "gpt-4" in model:
        print("Warning: gpt-4 may update over time. Returning num tokens assuming gpt-4-0613.")
        return num_tokens_from_messages(messages, model="gpt-4-0613")
    else:
        raise NotImplementedError(
            f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."""
        )
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens

class GenerateBlogTopicsView(LoginRequiredMixin, TemplateView):
    template_name = 'assistant/blogtopics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        generation_config = self.request.session.get('generation_config_blog_topics', DEFAULT_GENERATION_CONFIG)
        context['form'] = BlogSectionForm()
        context['form2'] = GenerationConfigForm(initial=generation_config)
        return context

    def post(self, request, *args, **kwargs):
        form1 = BlogSectionForm(request.POST)
        form2 = GenerationConfigForm(request.POST)

        if form1.is_valid():
            prompt = form1.cleaned_data['prompt'].title()

            prompt_parts = f'Generate one line blog topics on {prompt}'
            self.request.session['prompt'] = prompt

            generation_config = request.session.get('generation_config_blog_topics', DEFAULT_GENERATION_CONFIG) 
            model= generation_config['model']
            print(generation_config)
            
            try: 
                message=[
                            {"role": "system", "content": "You are  helpful blog writing assistant."},
                            {"role": "user", "content": prompt_parts}
                        ]
                prompts_token = num_tokens_from_messages(message, model)
                max_tokens_for_response = generation_config['max_output_tokens'] - prompts_token - 10
                completion = client.chat.completions.create(
                        model=model,
                        messages= message,
                    
                        max_tokens= max_tokens_for_response,
                        temperature=generation_config['temperature'],
                        top_p=generation_config['top_p'],
                    )
                # print(completion.choices[0].message.content)
                completion_response = completion.choices[0].message.content
                completion_html = markdown.markdown(completion.choices[0].message.content)
               
                response_token = num_tokens_from_messages([{'role': 'assistant', 'content':completion_response }], model)
                topics_content_type = ContentType.objects.get_for_model(Topics)
                with transaction.atomic():
                    
                    topic = Topics.objects.create(
                        user=request.user,
                        prompt=prompt,
                        body=completion_html
                    )
                   
                    TokenConsumption.objects.create(
                        user=request.user,
                        input_token=prompts_token,
                        output_token=response_token,
                        model = model, 
                        content_type=topics_content_type,  
                        object_id= topic.id,
                    )
                return HttpResponse(completion_html) 

            except Exception as e:
                return HttpResponse(f'{type(e).__name__}: {e}')
            
        elif form2.is_valid():
            temperature = float(form2.cleaned_data['temperature'])
            top_p = int(form2.cleaned_data['top_p'])
            max_output_tokens = int(form2.cleaned_data['max_output_tokens'])
            model = form2.cleaned_data['model']
            generation_config = {
                'temperature': temperature,
                'top_p': top_p,
                'max_output_tokens': max_output_tokens,
                'model':model
            }
             # Save the dictionary to the session
            request.session['generation_config_blog_topics'] = generation_config
            messages.success(request, 'Generation configuration saved')
            # print(generation_config)
            return HttpResponseRedirect(reverse('generate_blog_topics'))

  

class GenerateBlogSectionView(LoginRequiredMixin, TemplateView):
    template_name = 'assistant/blogsection.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        prompt = self.kwargs.get('prompt') 
        generation_config = self.request.session.get('generation_config_blog_section', DEFAULT_GENERATION_CONFIG)
        context['form'] = BlogSectionForm(self.request.GET or None)
        context['form2'] = GenerationConfigForm(initial=generation_config)
        
        
        context['prompt'] = prompt
        return context

    def post(self, request, *args, **kwargs):
        form1 = BlogSectionForm(request.POST)
        form2 = GenerationConfigForm(request.POST)

        if form1.is_valid():
            prompt = form1.cleaned_data.get('prompt').lower().title()
      
            title = self.request.session.get('prompt', None)
            prompt_parts =  f"Expand the blog title named {title} into high-level one-line blog sections on {prompt}. "
            

            generation_config = request.session.get('generation_config_blog_section', DEFAULT_GENERATION_CONFIG)
            print(generation_config)
            try: 
                model= generation_config['model']
                section_message=[
                            {"role": "system", "content": "You are  helpful blog writing assistant."},
                            {"role": "user", "content": prompt_parts}
                        ]
                section_prompts_token = num_tokens_from_messages(section_message, model)
                max_tokens_for_section_response = generation_config['max_output_tokens'] - section_prompts_token - 10
                completion_section = client.chat.completions.create(
                        model=model,
                        messages=section_message,
                    
                        max_tokens= max_tokens_for_section_response,
                        temperature=generation_config['temperature'],
                        top_p=generation_config['top_p'],
                    )
                section_res = completion_section.choices[0].message.content
                section_response_token = num_tokens_from_messages([{'role': 'assistant', 'content':section_res }], model)
                print(section_res)
                blog_prompt_parts = f'Craft an engaging blog post centered around the topic titled "{title}". Your article will delve into each point outlined in {section_res}, offering a detailed explanation and exploration of each topic. Ensure to include a captivating introduction and a compelling conclusion to tie the article together seamlessly.'
                
                message = [
                            {"role": "system", "content": "You are  helpful blog writing assistant."},
                            {"role": "user", "content": blog_prompt_parts}
                        ]
                prompts_token = num_tokens_from_messages(message, model)
                max_tokens_for_response = generation_config['max_output_tokens'] - prompts_token - 10
                completion = client.chat.completions.create(
                        model= model,
                        messages= message,
                    
                        max_tokens= max_tokens_for_response,
                        temperature=generation_config['temperature'],
                        top_p=generation_config['top_p'],
                    )

                completion_response = completion.choices[0].message.content
                completion_html = markdown.markdown(completion.choices[0].message.content)
                response_token = num_tokens_from_messages([{'role': 'assistant', 'content':completion_response }], model)

                input_token = section_prompts_token + prompts_token
                output_token = section_response_token + response_token
                content_type = ContentType.objects.get_for_model(History)
                with transaction.atomic():
                    
                    blog_title, created = BlogSection.objects.get_or_create(
                        user=self.request.user, 
                        title=prompt
                    )
                    new_history = History.objects.create(
                        user=self.request.user, 
                        title=blog_title, 
                        body=completion_html, 
                        prompt=blog_prompt_parts, 
                        section = section_res
                    )
                    TokenConsumption.objects.create(
                        user=request.user,
                        input_token=input_token,
                        output_token=output_token, 
                        model = model, 
                        content_type=content_type,  
                        object_id= new_history.id,

                    )
                    
                return HttpResponse(completion_html) 

            except Exception as e:
                return HttpResponse(f'{type(e).__name__}: {e}')
            
        elif form2.is_valid():
            temperature = int(form2.cleaned_data['temperature'])
            top_p = int(form2.cleaned_data['top_p'])
            max_output_tokens = int(form2.cleaned_data['max_output_tokens'])
            model = form2.cleaned_data['model']

            generation_config = {
                'temperature': temperature,
                'top_p': top_p,
                'max_output_tokens': max_output_tokens,
                'model': model
            }
        
           
             # Save the dictionary to the session
            request.session['generation_config_blog_section'] = generation_config
            messages.success(request, 'Generation configuration saved')
            # print(generation_config)
            return HttpResponseRedirect(reverse('generate_blog_sections'))
   
    
class GenerateBlogView(LoginRequiredMixin, TemplateView):
    template_name = 'assistant/test2.html'
    items_per_page = 10
   
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = BlogSection.objects.filter(user = self.request.user).order_by('-id')
       
        blogs_grouped_by_date = {}
        blogs = BlogSection.objects.filter(user = self.request.user).order_by('-updated_dt')
        for blog in blogs:
            created_date = blog.updated_dt.date()  #using updated_dt because updated_dt gets updated if new blog for same title is created
            if created_date not in blogs_grouped_by_date:
                blogs_grouped_by_date[created_date] = []
            blogs_grouped_by_date[created_date].append(blog)
        context['blogs_grouped_by_date'] = blogs_grouped_by_date

        context['blogs'] = queryset
        generation_config = self.request.session.get('generation_config_blog', DEFAULT_GENERATION_CONFIG)
        context['form'] = BlogForm()
        context['form2'] = GenerationConfigForm(initial=generation_config)
        return context
    
    def post(self, request, *args, **kwargs):
        form1 = BlogForm(request.POST)
        form2 = GenerationConfigForm(request.POST)
        generation_config = self.request.session.get('generation_config_blog', DEFAULT_GENERATION_CONFIG) 

        if form1.is_valid():
            prompt = form1.cleaned_data.get('prompt').lower().title()
      
            # title = self.request.session.get('prompt', None)
            prompt_parts =  f"Expand the blog title named {prompt} into high-level one-line blog sections on {prompt}. Give two sections strictly "
            

            generation_config = request.session.get('generation_config_blog_section', DEFAULT_GENERATION_CONFIG)
            print(generation_config)
            try: 
                model=generation_config['model']
                section_message=[
                            {"role": "system", "content": "You are  helpful blog writing assistant."},
                            {"role": "user", "content": prompt_parts}
                        ]
                section_prompts_token = num_tokens_from_messages(section_message, model)
                max_tokens_for_section_response = generation_config['max_output_tokens'] - section_prompts_token - 10
                completion_section = client.chat.completions.create(
                        model=model,
                        messages=section_message,
                    
                        max_tokens= max_tokens_for_section_response,
                        temperature=generation_config['temperature'],
                        top_p=generation_config['top_p'],
                    )
                section_res = completion_section.choices[0].message.content
                section_response_token = num_tokens_from_messages([{'role': 'assistant', 'content':section_res }], model)
                print(section_res)
                blog_prompt_parts = f'Craft an engaging blog post centered around the topic titled "{prompt}". Your article will delve into each point outlined in {section_res}, offering a detailed explanation and exploration of each topic. Ensure to include a captivating introduction and a compelling conclusion to tie the article together seamlessly.'
                
                message = [
                            {"role": "system", "content": "You are  helpful blog writing assistant."},
                            {"role": "user", "content": blog_prompt_parts}
                        ]
                prompts_token = num_tokens_from_messages(message, model)
                max_tokens_for_response = generation_config['max_output_tokens'] - prompts_token - 10


                completion = client.chat.completions.create(
                        model= model,
                        messages= message,
                    
                        max_tokens= max_tokens_for_response,
                        temperature=generation_config['temperature'],
                        top_p=generation_config['top_p'],
                    )

                print(completion.choices[0].message.content)
                completion_response = completion.choices[0].message.content
                completion_html = markdown.markdown(completion.choices[0].message.content)
                response_token = num_tokens_from_messages([{'role': 'assistant', 'content':completion_response }], model)

                input_token = section_prompts_token + prompts_token
                output_token = section_response_token + response_token
                content_type = ContentType.objects.get_for_model(History)

                with transaction.atomic():
                   
                    blog_title, created = BlogSection.objects.get_or_create(
                        user=self.request.user, 
                        title=prompt
                    )
                    
                    if not created:
                        # If the object already exists, update the updated_at field
                        blog_title.updated_dt = timezone.now()
                        blog_title.save()
                    new_history = History.objects.create(
                        user=self.request.user, 
                        title=blog_title, 
                        body=completion_html,   
                        prompt=blog_prompt_parts, 
                        section = section_res
                    )
                    TokenConsumption.objects.create(
                        user=self.request.user,
                        input_token=input_token,
                        output_token=output_token,
                        model = model,
                        content_type = content_type,
                        object_id = new_history.id
                    )
                    
                return HttpResponse(completion_html) 

            except Exception as e:
                return HttpResponse(f'{type(e).__name__}: {e}')
            
            
        elif form2.is_valid():
            temperature = int(form2.cleaned_data['temperature'])
            top_p = int(form2.cleaned_data['top_p'])
            max_output_tokens = int(form2.cleaned_data['max_output_tokens'])
            model = form2.cleaned_data['model']

            generation_config = {
                'temperature': temperature,
                'top_p': top_p,
                'max_output_tokens': max_output_tokens,
                'model': model
            }
             # Save the dictionary to the session
            request.session['generation_config_blog'] = generation_config
            messages.success(request, 'Generation configuration saved successfully !!')
            return HttpResponseRedirect(reverse('generate_blog'))
        
        elif request.method == 'POST':
            action = request.POST.get('action')
            # prompt = "Generate a blog article on Internet"
            if 'prompt_parts' in self.request.session:
                prompt = self.request.session['prompt_parts']
            
                response =regenerate(request, prompt = prompt, generation_config = generation_config)
                return HttpResponse(response)
            else:
                messages.warning(request, "Cannot regenerate")
                return HttpResponseRedirect(reverse('generate_blog'))


class HistoryDetailView(LoginRequiredMixin, DetailView):
    template_name = 'assistant/details.html'
    model = History

    def generateFeaturedImage(self, request, title, body, content_type, object_id):
        model="gpt-3.5-turbo-0125"
                    
        prompt = f"Generate one ready to use prompt to create image for the blog article titled {title} with description as {body}. The prompt needs to be under 1000 words and include all the points from the blog description. Give me the straight prompts"
        message=[
                                    {"role": "system", "content": "You are  helpful blog writing assistant."},
                                    {"role": "user", "content": prompt}
                                ]
        completion = client.chat.completions.create(
                                model= model,
                                messages=message
                            
                            )
        image_prompt = completion.choices[0].message.content
        input_token = num_tokens_from_messages(message, model)
        output_token = num_tokens_from_messages([{'role': 'assistant', 'content':image_prompt }], model)
        image_url = generate_image(request, prompt = image_prompt, number_of_photos=1)
        image_count = 1
        with transaction.atomic():
                            TokenConsumption.objects.create(
                            user=request.user,
                            input_token=input_token,
                            output_token=output_token,
                            model = model, 
                            image = image_count,
                            content_type= content_type,
                            object_id = object_id,
                        )
        for url in image_url:
            return url
                            

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user 
        histories = History.objects.filter(title=self.object.id, user=user).order_by('-id')
        context['histories'] = histories
        context['histories_with_blog'] = [
            {'history': history, 'has_blog': Blog.objects.filter(user=user, title=history.title).exists(),
             'featured_image': Blog.objects.filter(user=user, title=history.title)}
            for history in histories
        ]
        context['form']= ImageUploadForm()
        
        return context
   
    def post(self, request, *args, **kwargs):
        form = ImageUploadForm(request.POST)
       
        his = self.get_object()
        # print(his.title)
        if request.method == 'POST':
            id = request.POST.get('id')
             
            history = History.objects.get(id = id)
            print(history.id)
            generation_config = DEFAULT_GENERATION_CONFIG 

            if 'Save' in request.POST or 'Update' in request.POST:
                blog_title =  Blog.objects.filter(user = self.request.user, title=history.title).first()
                # print(blog_title)
                # print(history.body)
                content_type = ContentType.objects.get_for_model(Blog)
                if blog_title:
                    if 'featured_image' in request.POST:
                        url = self.generateFeaturedImage(request, history.title, history.body,content_type, blog_title.id)
                        blog_title.body = history.body
                        blog_title.history = history
                       
                            
                        image = requests.get(url)
                        blog_title.featured_image.save(       
                                    'filename.png', ContentFile(image.content), save=True
                        )
                        blog_title.save()
                    else:
                        blog_title.body = history.body
                        blog_title.history = history
                        blog_title.save()
                    messages.success(request, 'Blog entry updated successfully')
                else:
                    if 'featured_image' in request.POST:
                            
                        with transaction.atomic():
                            new_blog =  Blog.objects.create(
                                user=self.request.user, 
                                title=history.title.title, 
                                history = history, 
                                body=history.body)
                            url = self.generateFeaturedImage(request, history.title, history.body, content_type, new_blog.id)
                           
                            image = requests.get(url)
                            new_blog.featured_image.save(       
                                    'filename.png', ContentFile(image.content), save=True
                                )
                            new_blog.save()
                    else:
                        Blog.objects.create(
                                user=self.request.user, 
                                title=history.title.title, 
                                history = history, 
                                body=history.body)
                    messages.success(request, 'Blog entry created successfully')
                return HttpResponseRedirect(reverse('details', args=[his.id]))
        
            elif 'Regenerate' in request.POST:
                prompt = history.prompt
            
                response =regenerate(request, prompt = prompt, generation_config = generation_config, title= history.title)
                messages.success(self.request, f"Content for {history.title} regenerated successfully")
                return HttpResponseRedirect(reverse('details', args=[his.id]))
                # return HttpResponse(response)
                # return HttpResponse(history.prompt)
            elif 'Image' in request.POST:
                    section = history.section
                    model = "gpt-3.5-turbo-0125"
                    content_type = ContentType.objects.get_for_model(History)
                    if section and section != None:
                        points = section.split("\n")
                        points = [point.split('. ')[1] for point in points if point.strip() != ""]
                        input_token = 0
                        output_token = 0
                        image_count= 0
                        for point in points:
                            print(point)
                            print("break")
                            prompt = f"Generate one ready to use prompt to create image for the blog article titled {history.title} for showcasing {point}. The prompt needs to be strictly under 200 words. Give me the straight prompts"
                            message = [
                                            {"role": "system", "content": "You are  helpful blog writing assistant."},
                                            {"role": "user", "content": prompt}
                                        ]
                            completion = client.chat.completions.create(
                                        model=model,
                                        messages= message
                                    )
                            image_prompt = completion.choices[0].message.content
                            prompt_token = num_tokens_from_messages(message, model)
                            response_token = num_tokens_from_messages([{'role': 'assistant', 'content':image_prompt }], model)
                            input_token += prompt_token
                            output_token += response_token
                            
                            print(image_prompt)
                            image_url = generate_image(request, prompt = image_prompt, number_of_photos=1)
                            image_generated = 1
                            image_count  += image_generated
                            for url in image_url:
                                image = requests.get(url)
                                new_image = BlogImage.objects.create(
                                        user = self.request.user,
                                        history = history
                                    )
                                new_image.image.save(       
                                            'filename.png', ContentFile(image.content), save=True
                                        )
                                new_image.save()
                        print(input_token)
                        print(image_count)
                        total_image = image_count
                        with transaction.atomic():

                        
                            TokenConsumption.objects.create(
                            user=request.user,
                            input_token=input_token,
                            output_token=output_token,
                            model = model, 
                            image = total_image,
                            content_type = content_type,
                            object_id = history.id
                        )

                        messages.success(self.request, "Images generated successfully")
                    
                    else:
                        messages.warning(self.request, "Images cannot be generated")
                    return HttpResponseRedirect(reverse('details', args=[his.id]))
            elif 'upload' in request.POST:
                if form.is_valid():
                    image = form.cleaned_data['image']
                    print(image)
                    # if not image in form.cleaned_data:
                    #     messages.warning(self.request, "Select Image to upload")
                    #     return HttpResponseRedirect(reverse('details', args=[his.id]))

                    image_n = Images.objects.get(id=image.id)
                    # url = image_n.get_image_url(request)
                    # print(url)
                    BlogImage.objects.create(
                        user = self.request.user,
                        history = history,
                        image=image_n.image
                    )
                    messages.success(self.request, "Image upload successfull" )
                
                    return HttpResponseRedirect(reverse('details', args=[his.id]))
                else:
                    messages.warning(self.request, "Images cannot be uploaded")
                    return HttpResponseRedirect(reverse('details', args=[his.id]))

   
class HistoryUpdateView(UpdateView):
 

    model = History
    form_class = HistoryUpdateForm
    template_name = "assistant/historyupdate.html"

    def get_success_url(self):
        history_instance = get_object_or_404(History, slug=self.kwargs['slug'])
        blog_section_id = history_instance.title.id
        return reverse('details', args=[blog_section_id])
    
    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.save()

        messages.success(self.request, "Content Updated!!!")
        
    
        return super().form_valid(form)

class BlogListView(LoginRequiredMixin, ListView):
    model = Blog
    paginate_by = 8 # if pagination is desired
    template_name = "assistant/bloglist.html"
    # allow_empty = True
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    

    def get_queryset(self):
        queryset = super(BlogListView, self).get_queryset()
        
        queryset = queryset.filter(
           user=self.request.user
        ).order_by('-id')

        return queryset

class BlogDetailView(LoginRequiredMixin, DetailView):
    template_name = 'assistant/blogdetails.html'
    model = Blog

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.status == 'protected' and self.object.user != self.request.user:
            form = PasswordForm()
            return render(request, 'assistant/protect.html', {'form': form, 'blog': self.object})
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.status == 'protected':
            form = PasswordForm(request.POST)

            if form.is_valid():
                entered_password = form.cleaned_data['password']

                if check_password(entered_password, self.object.password):
                # if entered_password == self.object.password:
                    return super().get(request, *args, **kwargs)

        messages.warning(self.request, 'Invalid Password')
        return HttpResponseRedirect(reverse('blog-details', args=[self.object.slug]))  
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        image = BlogImage.objects.filter(
            user=self.request.user, 
            history = self.object.history
        )
        shortcodes = process_shortcodes(self.request, self.object.body )
        context['body_shortcodes'] = shortcodes
        context['image'] = image
        return context



class BlogUpdateView(LoginRequiredMixin, UpdateView):
    
    model = Blog
    form_class = BlogUpdateForm
    template_name = "assistant/blogupdate.html"

    def get_success_url(self):
        blog = self.get_object()
        return reverse('list')
    
    def get_queryset(self):
        queryset = super(BlogUpdateView, self).get_queryset()
        
        queryset = queryset.filter(
           user=self.request.user
        )

        return queryset
    
    def form_valid(self, form):
        
        obj = form.save(commit=False)

        if 'save_body' in self.request.POST:
            body = form.cleaned_data['body']
            if not obj.body == body:    
                obj.body = body
            obj.save()
            messages.success(self.request, f'Blog Updated Successfully !!')
            return super().form_valid(form)
       
        elif 'save_settings' in self.request.POST: 
            status = form.cleaned_data['status']
            
            if status == 'protected':
                password = form.cleaned_data['password']
                if not password:
                    form.add_error(None, "Password is required for 'protected' status.")
                    return self.form_invalid(form)
                else:
                
                    obj.set_password(password)
                    print('The object psw is ',obj.password)
                

            elif status == 'scheduled':
                scheduled_time = form.cleaned_data['scheduled_time']
                if not scheduled_time:
                    form.add_error(None, 'Scheduling Time and Date needs to be entered')
                    return self.form_invalid(form)
                elif scheduled_time < timezone.now():
                    form.add_error(None, 'Please choose a valid time and date for scheduling')
                    return self.form_invalid(form)
                else:
                    obj.scheduled_time = scheduled_time

            obj.status = status
        
            # form.save()
            obj.save()

            messages.success(self.request, 'Settings Updated Successfully')
            return HttpResponseRedirect(reverse('blog-edit', args=[obj.slug]))
        
        
    def form_invalid(self, form):
        return super().form_invalid(form)


   
   
class BlogDeleteView(LoginRequiredMixin, DeleteView):
    model = Blog
    template_name = "assistant/delete_confirmation.html"
   
    

    def get_success_url(self):
        return reverse('list')

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(self.request, f'Blog {obj.title} deleted successfully')
        return super(BlogDeleteView, self).delete(request, *args, **kwargs)

class TokenHistory(LoginRequiredMixin, ListView):
    model = TokenConsumption
    paginate_by = 7 # if pagination is desired
    template_name = "assistant/tokenhistory.html"
    # allow_empty = True
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        token_consumption = TokenConsumption.objects.filter(user=self.request.user).order_by('-created_dt').first()
        if token_consumption:
            latest_total_input_tokens = token_consumption.total_input_token
            latest_total_output_tokens = token_consumption.total_output_token
            latest_total_images = token_consumption.total_image
        else:
            latest_total_input_tokens = None
            latest_total_output_tokens = None
            latest_total_images = None
        context['latest_total_input_tokens'] = latest_total_input_tokens
        context['latest_total_output_tokens'] = latest_total_output_tokens
        context['latest_total_images'] = latest_total_images


        # context['total_input_token'] = TokenConsumption.object.lates
        return context
    

    def get_queryset(self):
        queryset = super(TokenHistory, self).get_queryset()
        
        queryset = queryset.filter(
           user=self.request.user
        ).order_by('-id')

        return queryset



class TestGenerateBlogTopicsView(View):
    def generate_blog_topic(self, request):
        generation_config = DEFAULT_GENERATION_CONFIG
        # safety_settings = process_safety_settings()
        model = genai.GenerativeModel(model_name="gemini-pro",
                                generation_config=generation_config,
                                safety_settings=safety_settings)
       
        if request.method == "POST":
            prompt = request.POST.get('topic_field')

        prompt_parts = [
            f'Generate one line blog topics on {prompt}'
                    ]

        try:
            
            def generate_chunks(model, prompt_parts):
                response = model.generate_content(prompt_parts, stream=True)
                res = None
                for chunk in response:
                    res = chunk.candidates[0].content.parts[0].text
                    print(res)
                    yield res
            stream_response = StreamingHttpResponse(generate_chunks(model, prompt_parts), content_type='text/event-stream')
            stream_response['Cache-Control'] = 'no-cache' 
            return stream_response
        except Exception as e:
            return HttpResponse(f'{type(e).__name__}: {e}')
    
    def post(self, request):
        return self.generate_blog_topic(request)

    def get(self, request):
        model = genai.GenerativeModel(model_name="gemini-pro",
                                generation_config=DEFAULT_GENERATION_CONFIG)
        form = BlogForm()
        gemini_chat = model.start_chat(history=[])
        response1 = gemini_chat.send_message("Generate a blog description for implemenattion of technology for blog titled Finance ")
        print(response1.text)
        print('Breakkk')
        response2 = gemini_chat.send_message('What about the security risks ?')
        print(response2.text)
        print(gemini_chat.history)
        return render(request, 'assistant/test.html', {'form': form})


class Regenrate(LoginRequiredMixin, View):    
    # template_name = 'assistant/blog.html'
    def get(self, request, *args, **kwargs):
            # prompt = self.request.session.get('prompt', None)
            prompt = self.request.session.get('prompt_parts')
            prompt_parts = f'Regenerate {prompt}'

            # prompt_parts = [
            #     f'Generate one line blog topics on {prompt}'
            # ]

            generation_config = request.session.get('generation_config_blog_topics', DEFAULT_GENERATION_CONFIG) 
            print(generation_config)
            safety_settings = process_safety_settings()
            model = genai.GenerativeModel(model_name="gemini-pro",
                                        generation_config=generation_config,
                                        safety_settings=safety_settings)

            try:
                def generate_chunks(model, prompt_parts):
                    response = model.generate_content(prompt_parts, stream=True)
                    print(response)
                    complete_res = ''
                    for chunk in response:
                        res = chunk.candidates[0].content.parts[0].text
                        res_html = markdown.markdown(res)
                        print(res)
                        complete_res +=res_html
                        yield res_html
                    print(complete_res)
                stream_response = StreamingHttpResponse(generate_chunks(model, prompt_parts), content_type='text/event-stream')
                print(stream_response)
                stream_response['Cache-Control'] = 'no-cache' 
                return stream_response


                

                
            except Exception as e:
                return HttpResponse(f'{type(e).__name__}: {e}')

import json

def openai(request):
    response = client.images.generate(
        model="dall-e-3",
        prompt="Create an image depicting the blog article titled human body",
        n=1,
        size='1024x1024'
    )
    # image_url = [data["url"] for data in response.data]
    # image_url = response.data[0].url
    # image_url = 'https://lh3.googleusercontent.com/uMDnEAGWcwJQ_vX_6GgVCvZLx6LBt5QvlirWy2bsNaodnQWBnIgJmQ0pIswfpNZPKMg6jNtGo5_JJZ4R8No4GfSRVrgaBpw3K9Ix_A'
    # res = requests.get(image_url)
    # image_content = ContentFile(res.content)
    # json_response = response.json()
    # response_data = json.loads(json_response)

    # # Extracting URLs from the response
    # urls = [image['url'] for image in response_data['data']]

    # for url in urls:
    #     print(url)
    
    return HttpResponse(response)

    
