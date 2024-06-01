from django.forms import Widget
from django.template.loader import render_to_string
from django import forms

class CustomCkeditor(Widget):
    template_name = 'assistant/ckeditor.html'
    def render(self, name, value, attrs=None, renderer=None):
        context = {'name': name, 'value': value, 'attrs': attrs}
        return render_to_string(self.template_name, context)

