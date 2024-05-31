import os 
import uuid
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify
from userprofile.models import BaseModel


def image_upload_path(instance, filename):
    id = uuid.uuid4()
    basename, ext = os.path.splitext(filename)
    filename = f"{id}_{basename}{ext}"

    upload_dir = 'filemanager/images/'
    return os.path.join(upload_dir, filename)


class Images(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=image_upload_path, null=True, blank=True)

    def get_image_url(self, request):
        if self.image:
            image_url = settings.MEDIA_URL + str(self.image)
            return request.build_absolute_uri(image_url)
        return None