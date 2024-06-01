from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from . models import *
from django.dispatch import receiver

@receiver(post_save, sender=TokenConsumption)
def update_total_input_token(sender, instance, created, **kwargs):
    pass