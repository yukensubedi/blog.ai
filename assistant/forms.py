from django import forms
from django.utils.translation import gettext_lazy as _
from .models import *
from filemanager.models import Images
from django_ckeditor_5.widgets import CKEditor5Widget
from .widgets import CustomCkeditor


class GenerationConfigForm(forms.Form):
   
    temperature = forms.FloatField(
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Temperature ',
                'class': 'w-full rounded-lg border border-stroke bg-transparent py-4 pl-6 pr-10 outline-none focus:border-primary focus-visible:shadow-none dark:border-form-strokedark dark:bg-form-input dark:focus:border-primary'
                }
        ),
        required=True)
   
    top_p = forms.IntegerField(
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Top p',
                'class': 'w-full rounded-lg border border-stroke bg-transparent py-4 pl-6 pr-10 outline-none focus:border-primary focus-visible:shadow-none dark:border-form-strokedark dark:bg-form-input dark:focus:border-primary'
                }
        ),
        required=True)
    max_output_tokens = forms.IntegerField(
        widget=forms.TextInput(
            attrs={
                'placeholder': ' Maxmimun Output tokens ',
                'class': 'w-full rounded-lg border border-stroke bg-transparent py-4 pl-6 pr-10 outline-none focus:border-primary focus-visible:shadow-none dark:border-form-strokedark dark:bg-form-input dark:focus:border-primary'
                }
        ),
        required=True)
    model_choices = [
        ('gpt-3.5-turbo-0125', 'gpt-3.5-turbo-0125'),
        ('gpt-3.5-turbo-instruct', ' gpt-3.5-turbo-instruct'),
        ('gpt-4','gpt-4')
        # Add more models as needed
    ]
    model = forms.ChoiceField(
        choices=model_choices,
        widget=forms.Select(
            attrs={
                'class': 'w-full rounded-lg border border-stroke bg-transparent py-4 pl-6 pr-10 outline-none focus:border-primary focus-visible:shadow-none dark:border-form-strokedark dark:bg-form-input dark:focus:border-primary'
            }
        ),
        required=True
    )

class BlogTopicForm(forms.Form):
    prompt = forms.CharField(
        
        widget=forms.TextInput(
            attrs={
                'id': 'id_prompt',
                'placeholder': 'Enter the keyword to generate blog topics ',
                'class': 'w-full rounded-lg border border-stroke bg-transparent py-4 pl-6 pr-10 outline-none focus:border-primary focus-visible:shadow-none dark:border-form-strokedark dark:bg-form-input dark:focus:border-primary'
                }
        ),
        required=True)

class BlogSectionForm(forms.Form):
    prompt = forms.CharField(
        
        widget=forms.TextInput(
            attrs={
                'id': 'id_prompt',
                'placeholder': 'Enter the blog title to generate blog sections with details ',
            
                'class': 'w-full rounded-lg border border-stroke bg-transparent py-4 pl-6 pr-10 outline-none focus:border-primary focus-visible:shadow-none dark:border-form-strokedark dark:bg-form-input dark:focus:border-primary'
                }
        ),
        required=True)

class BlogForm(forms.Form):
    prompt = forms.CharField(
        
        widget=forms.TextInput(
            attrs={
                 'id': 'id_prompt',
                'placeholder': 'Enter the blog title to generate blog ',
                'class': 'w-full rounded-lg border border-stroke bg-transparent py-4 pl-6 pr-10 outline-none focus:border-primary focus-visible:shadow-none dark:border-form-strokedark dark:bg-form-input dark:focus:border-primary'
                }
        ),
        required=True)


class HistoryUpdateForm(forms.ModelForm):
    class Meta:
        model = History
        fields = ['body']
        widgets = {
            # "text": CKEditor5Widget(
            #     attrs={"class": "django_ckeditor_5"},
            # ),
             "body": CustomCkeditor(
                # attrs={"class": "django_ckeditor_5"},
            ),
        }

class BlogUpdateForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['title','body', 'status', 'scheduled_time', 'password', 'featured_image']
        widgets = {
            "title": forms.TextInput(
                attrs={
                    'class': 'w-full rounded-lg border border-stroke bg-transparent py-4 pl-6 pr-10 outline-none focus:border-primary focus-visible:shadow-none dark:border-form-strokedark dark:bg-form-input dark:focus:border-primary',
                }
            ),
            "body": CustomCkeditor(
                # attrs={"class": "django_ckeditor_5"},
            ),
            'status': forms.Select(
                attrs={
                    'class': 'w-full rounded-lg border border-stroke bg-transparent py-4 pl-6 pr-10 outline-none focus:border-primary focus-visible:shadow-none dark:border-form-strokedark dark:bg-form-input dark:focus:border-primary',
                }
            ),
            'scheduled_time': forms.DateTimeInput(
                
                attrs={
                    
                    'placeholder': 'Choose the scheduled time',
                    'class': 'w-full rounded-lg border border-stroke bg-transparent py-4 pl-6 pr-10 outline-none focus:border-primary focus-visible:shadow-none dark:border-form-strokedark dark:bg-form-input dark:focus:border-primary',
                },
            ),
            'password': forms.PasswordInput(
                attrs={
                    'placeholder': 'Enter the password ',
                    'class': 'w-full rounded-lg border border-stroke bg-transparent py-4 pl-6 pr-10 outline-none focus:border-primary focus-visible:shadow-none dark:border-form-strokedark dark:bg-form-input dark:focus:border-primary',
                }
            )

        }

       

class PasswordForm(forms.Form):
    password = forms.CharField(
        
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Enter the password ',
                'class': 'w-full rounded-lg border border-stroke bg-transparent py-4 pl-6 pr-10 outline-none focus:border-primary focus-visible:shadow-none dark:border-form-strokedark dark:bg-form-input dark:focus:border-primary'
                }
        ),
        required=True)

class ImageUploadForm(forms.ModelForm):
    image = forms.ModelChoiceField(queryset=Images.objects.all(), required=False)
    class Meta:
        model = Images
        fields = ['image']
       

from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV3, ReCaptchaV2Checkbox

class formWithCaptcha(forms.Form):
    name = forms.CharField()
    captcha = ReCaptchaField( widget=ReCaptchaV3
    )