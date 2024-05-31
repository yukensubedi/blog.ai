import json
import socket
from django.db.models.query import QuerySet
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.urls import reverse_lazy

from django.views import View
from django.core.mail import send_mail
from django.contrib import messages
from django.conf import settings
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import MultipleObjectMixin


from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView

from .models import ContactForm, ContactFormContent
from .utils import decode_data
from .forms import ContactModelForm

# Create your views here.
def test(request):
    if request.method == 'POST':
        form_data = {key: value for key, value in request.POST.items() if key != 'csrfmiddlewaretoken'} #avoiding csrrf token data in dict 
        
        form_data_json = json.dumps(form_data)
        data = json.loads(form_data_json)
        print(data)
        
    return HttpResponse(form_data_json)
       
    # return render(request, 'contactform/thankyou.html')

class HandleForm(LoginRequiredMixin, View):
    template_name = 'contactform/thankyou.html'

    def post(self, request, *args, **kwargs):
        form_data = {key: value for key, value in request.POST.items() if key != 'csrfmiddlewaretoken'}
        form_id = form_data.get('form')

        try:
            if form_id:
                form_id = decode_data(form_id)
                contactform = get_object_or_404(ContactForm, id=form_id)
            else:
                raise ValidationError(_('Form ID is missing'))
        except (ValueError, ValidationError) as e:
            messages.error(request, _('Error fetching form details'))
            return HttpResponseRedirect(request.path)

        subject_data = form_data.get('subject', _('Contact Form details'))
        subject = contactform.subject or subject_data
        message_lines = [f"{key.capitalize()}: {value}" for key, value in form_data.items() if key != 'form']

        message = (f"{contactform.message}:\n\n" if contactform.message else
                   _("Someone has submitted the contact form. Please find the details as below.:\n\n")) + "\n".join(message_lines)
        print(message)
        from_email = 'yukensubedi@gmail.com'
        recipient_list = [email.strip() for email in contactform.to_sent.split(',')]
        try:
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
        except socket.gaierror:
            hostname = "Unknown"
            ip_address = "Unknown"

        ContactFormContent.objects.create(
            user=request.user, 
            form_content=json.dumps(form_data), 
            contactform=contactform,
            ip_address=ip_address
        )

        if getattr(settings, 'FAST_MAIL_CONTACT_FORM', False):
            pass
        else:
            send_mail(subject, message, from_email, recipient_list)

        return render(request, self.template_name)
    
    
class CreateContactForm(CreateView, LoginRequiredMixin):
    """
    View to create a new contact form  
    """

    model = ContactForm
    form_class = ContactModelForm
    template_name = 'contactform/create.html'
    success_url = reverse_lazy('list_form') 


    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Contact Form Created Successfully!')

        return super().form_valid(form)

class ListContactForm(ListView, LoginRequiredMixin):
    model = ContactForm
    template_name = 'contactform/list.html'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    

    def get_queryset(self):
        queryset = super(ListContactForm, self).get_queryset()
        
        queryset = queryset.filter(
        #    user=self.request.user
        ).order_by('-id')

        return queryset
    
class UpdateContactFormView(UpdateView, LoginRequiredMixin):
    
    model = ContactForm
    form_class = ContactModelForm
    template_name = "contactform/update.html"

    def get_success_url(self):
        return reverse('list_form')
    
    def get_queryset(self):
        queryset = super(UpdateContactFormView, self).get_queryset()
        queryset = queryset.filter(
           user=self.request.user
        )
        return queryset
    
    def form_valid(self, form):
       messages.success(self.request, 'Form Updated Successfully!!')
       return super().form_valid(form)
        
        
    def form_invalid(self, form):
        return super().form_invalid(form)

class ContactFormDeleteView(LoginRequiredMixin, View):
    model = ContactForm
   
    def get(self, request, pk):
        form = get_object_or_404(self.model, id=pk)
        if form.user != request.user:
            messages.warning(request, 'You cannot delete the form.')
            return HttpResponseRedirect(reverse('list_form'))
        
        form.delete()
        messages.success(request, 'Form deleted successfully')
        return HttpResponseRedirect(reverse('list_form'))

class ListContactFormContentView(LoginRequiredMixin, ListView):
    model = ContactFormContent
    template_name = 'contactform/content_list.html'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['id'] = self.kwargs['pk']
        return context
    
    def get_queryset(self) :
        queryset = super(ListContactFormContentView, self).get_queryset()
        id = self.kwargs['pk']
        queryset = queryset.filter(
           contactform_id=id,
        contactform__user=self.request.user
        ).order_by('-id')
         
        return queryset
    

