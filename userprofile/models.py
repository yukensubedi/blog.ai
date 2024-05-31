from django.db import models
from django.conf import settings

def upload_to(instance, filename):
    return 'uploads/%s/%s' % (instance.user.username, filename)

class BaseModel(models.Model):
    created_dt = models.DateTimeField(auto_now_add=True)
    updated_dt = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return '%s' % self.id

class Profile(BaseModel):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=upload_to, default="", blank=True, null=True, verbose_name="Profile Image")
    phone = models.CharField(null=True, blank=True, max_length=20)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    address = models.TextField(blank=True, null=True, max_length=255)

    @property
    def full_name(self):
        return (self.user.first_name or self.user.username )  + " " + self.user.last_name
    
    def __str__(self):
        return self.user.email
