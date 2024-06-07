from django.db import models
from django.conf import settings

from django.urls import reverse
from django.utils.text import slugify
from userprofile.models import BaseModel
from django.db import IntegrityError
from django.utils import timezone

from django_ckeditor_5.fields import CKEditor5Field
from django.contrib.auth.hashers import make_password, check_password

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


import uuid

class Topics(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    prompt = models.CharField(max_length = 1024, blank = True, null = True)
    body = CKEditor5Field('body', config_name='extends',null = True, blank = True)

    class Meta:
        get_latest_by = 'created_dt'


    def save(self, *args, **kwargs):
        if not self.slug:
            slug = slugify(self.prompt)
            base_slug = slug
            num = 1
            while True:
                if num > 1:
                    # If we've tried before, add the number to the end
                    slug = f"{base_slug}-{num}"
                slug_with_uuid = f"{slug}-{uuid.uuid4().hex[:8]}"
                try:
                    self.slug = slug_with_uuid
                    super().save(*args, **kwargs)
                    break  # Exit the loop if the save is successful
                except IntegrityError:
                    num += 1  # Try the next number

        else:
            super().save(*args, **kwargs)
        
    def __str__(self) -> str:
        return self.prompt
    

class BlogSection(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE )
    title = models.CharField(max_length = 2000, blank = True, null = True)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            slug = slugify(self.title)
            base_slug = slug
            num = 1
            while True:
                if num > 1:
                    # If we've tried before, add the number to the end
                    slug = f"{base_slug}-{num}"
                slug_with_uuid = f"{slug}-{uuid.uuid4().hex[:8]}"
                try:
                    self.slug = slug_with_uuid
                    super().save(*args, **kwargs)
                    break  # Exit the loop if the save is successful
                except IntegrityError:
                    num += 1  # Try the next number

        else:
            super().save(*args, **kwargs)
   
    def __str__(self) -> str:
        return self.title



class History(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE )
    title = models.ForeignKey(BlogSection, on_delete=models.CASCADE, null = True, blank = True) 
    slug = models.SlugField(max_length=1000, unique=True, blank=True, null=True)
    prompt = models.CharField(max_length=3000, null=True, blank=True)
   
    section = CKEditor5Field('section', config_name='extends', null=True, blank=True, default=None)
    body = CKEditor5Field('body', config_name='extends',null = True, blank = True)

    def save(self, *args, **kwargs):
        if not self.slug:
            slug = slugify(self.title.title)
            base_slug = slug
            num = 1
            while True:
                if num > 1:
                    # If we've tried before, add the number to the end
                    slug = f"{base_slug}-{num}"
                slug_with_uuid = f"{slug}-{uuid.uuid4().hex[:4]}"
                try:
                    self.slug = slug_with_uuid
                    super().save(*args, **kwargs)
                    break  # Exit the loop if the save is successful
                except IntegrityError:
                    num += 1  # Try the next number

        else:
            super().save(*args, **kwargs)
   
    
    def get_absolute_url(self):
        return reverse('details', kwargs={'slug': self.slug})
    
    def __str__(self) -> str:
        return self.title.title




class Blog(BaseModel):
    def image_upload_path(instance, filename):
        file_extension = filename.split('.')[-1]
        new_filename = f"{instance.slug}-featured.{file_extension}"
        return f'featured_images/{instance.user}/{new_filename}'
    
    STATUS_CHOICES = (
        ('published', 'Published'),
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('scheduled', 'Scheduled'),
        ('protected','Protected')
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    history = models.ForeignKey(History, on_delete=models.CASCADE, blank = True, null=True)

    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    title = models.CharField(max_length = 1024, blank = True, null = True)
    body = models.TextField(null = True, blank = True)
    status = models.CharField(max_length=20, choices = STATUS_CHOICES, default = 'draft')
    scheduled_time = models.DateTimeField(null = True, blank = True) 
    password = models.CharField(max_length=128, null = True, blank = True)
    featured_image = models.ImageField(upload_to=image_upload_path, blank = True, null = True)
    # status published draft pending scheduled protected if protected then passwrod required, scheduled if date time needed /fetaured image 
    class Meta:
        get_latest_by = 'created_dt'
    
    def set_password(self, raw_password):
        self.password = make_password(raw_password)
    
    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            slug = slugify(self.title)
            base_slug = slug
            num = 1
            while True:
                if num > 1:
                    slug = f"{base_slug}-{num}"
                slug_with_uuid = f"{slug}-{uuid.uuid4().hex[:8]}"
                try:
                    self.slug = slug_with_uuid
                    super().save(*args, **kwargs)
                    break  # Exit the loop if the save is successful
                except IntegrityError:
                    num += 1  # Try the next number

        else:
            super().save(*args, **kwargs)
   
   
    
    def __str__(self):
        return self.title 

    def update_status(self):
        """ Updates the status of the blog if it is scheduled  """
        if self.status == 'scheduled' and self.scheduled_time <= timezone.now():
            self.status = 'published'
            self.save()


class BlogImage(BaseModel):
    def blog_image_upload_path(instance, filename):
        file_extension = filename.split('.')[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        return f'BlogImages/{instance.user}/{instance.history.title}/{unique_filename}'
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    history = models.ForeignKey(History, on_delete = models.CASCADE)
    image = models.ImageField(upload_to=blog_image_upload_path, blank = True, null = True)

class TokenConsumption(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tokens')
    input_token = models.IntegerField(null=True, blank=True) #no of input token used(prompt)
    output_token = models.IntegerField(null=True, blank=True) #no of output token used(response)
    image = models.IntegerField(null = True,blank = True) #no of images generated
    model = models.CharField(max_length=255) #models used 
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank = True) 
    object_id = models.PositiveIntegerField(null=True, blank = True)
    content_object = GenericForeignKey('content_type', 'object_id')
    

    date = models.DateTimeField(null=True, blank=True,  auto_now_add=True)
    total_input_token = models.IntegerField(null=True, blank=True,default=0)
    total_output_token = models.IntegerField(null=True, blank=True,default=0)
    total_image = models.IntegerField(null=True, blank=True,default=0)

    def save(self, *args, **kwargs):
        last_token = TokenConsumption.objects.filter(user=self.user).last()
        if self.input_token:
           
            if last_token:
                last_input_token = last_token.total_input_token
                self.total_input_token = last_input_token + self.input_token
            else:
                self.total_input_token = self.input_token

        if self.output_token:
            
            if last_token:
                last_output_token = last_token.total_output_token
                self.total_output_token = last_output_token + self.output_token
            else:
                self.total_output_token = self.output_token

        if self.image:
            if last_token:
                self.total_image = last_token.total_image + self.image
            else:
                self.total_image = self.image
        if self.image is None:
            if last_token:

                self.image = 0
                self.total_image = last_token.total_image + self.image
            else:
                self.image = 0
            
        super(TokenConsumption, self).save(*args, **kwargs)




class ContactForms(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    form_html = models.TextField()
    # TODO:
    # contactform data new model
    # save the contact form content 
    # user content(store in json) contactfrom
    #create an app contact form and handle all the procees for conbtact form 
    # 

