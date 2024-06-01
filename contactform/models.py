from django.db import models
from userprofile.models import BaseModel
from django.conf import settings

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _


class ContactForm(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    form_html = models.TextField()
    to_sent = models.CharField(max_length=2000)
    message = models.TextField(null=True, blank=True)
    subject = models.TextField(null=True, blank=True)
    
    def clean(self):
        email_addresses = self.to_sent.split(',')
        
        for email in email_addresses:
            email = email.strip()
            if email:  
                try:
                    validate_email(email)
                except ValidationError:
                    raise ValidationError(
                        _('Invalid email address: %(value)s'),
                        params={'value': email},
                      )
        if '<form' in self.form_html or '</form>' in self.form_html:
            raise ValidationError(
                _('Exclude <form> tag'),
                code='invalid',
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super(ContactForm, self).save(*args, **kwargs)


class ContactFormContent(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    contactform = models.ForeignKey(ContactForm, on_delete=models.CASCADE)
    form_content = models.JSONField()
    ip_address = models.CharField(max_length=256, null=True, blank=True)
