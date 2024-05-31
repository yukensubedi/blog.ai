from django import forms
from django.utils.translation import gettext_lazy as _
from .models import *
from assistant.widgets import CustomCkeditor

class ContactModelForm(forms.ModelForm):
    class Meta:
        model = ContactForm
        fields = ['form_html', 'to_sent', 'message', 'subject']
        widgets = {
            'form_html': forms.Textarea(attrs={'class': 'w-full rounded-lg border border-stroke bg-transparent py-4 pl-6 pr-10 outline-none focus:border-primary focus-visible:shadow-none dark:border-form-strokedark dark:bg-form-input dark:focus:border-primary'}),
            'to_sent': forms.Textarea(attrs={'class': 'w-full rounded-lg border border-stroke bg-transparent py-4 pl-6 pr-10 outline-none focus:border-primary focus-visible:shadow-none dark:border-form-strokedark dark:bg-form-input dark:focus:border-primary', 'placeholder':'Multiple emails can be entered. Seperate them by comma'}),
            'message': forms.Textarea(attrs={'class': 'w-full rounded-lg border border-stroke bg-transparent py-4 pl-6 pr-10 outline-none focus:border-primary focus-visible:shadow-none dark:border-form-strokedark dark:bg-form-input dark:focus:border-primary'}),
            'subject': forms.Textarea(attrs={'class': 'w-full rounded-lg border border-stroke bg-transparent py-4 pl-6 pr-10 outline-none focus:border-primary focus-visible:shadow-none dark:border-form-strokedark dark:bg-form-input dark:focus:border-primary'}),
        }