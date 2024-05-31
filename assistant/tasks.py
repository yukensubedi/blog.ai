import logging 
from celery import shared_task
from django.core.management import call_command


from django.core.mail import EmailMultiAlternatives
from django.conf import settings

from django.core.mail import send_mail

logger = logging.getLogger(__name__)


@shared_task
def update_scheduled_blogs_task():
    call_command('update_blog_status')

@shared_task
def send_email_task(subject, message, recipient_list):
    print(message)
    send_mail(subject, message, 'yukensubedi@gmail.com', recipient_list)

@shared_task
def add_numbers(a, b):
    try:
        result = a + b
        print(f"The sum of {a} and {b} is {result}")
        return result
    except Exception as e:
        return (f"Error: {e}")
