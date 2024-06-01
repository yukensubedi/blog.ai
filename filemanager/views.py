from django.shortcuts import render
from .models import Images
from django.views.generic import ListView

from django.http import HttpResponseRedirect, HttpResponse, JsonResponse


def image_url(request, id):
    images = Images.objects.get(id=id)
    image_url= images.get_image_url(request)
    return HttpResponseRedirect(image_url)

def get_images(request):
    images = Images.objects.all()
    image_urls = [image.get_image_url(request) for image in images]
    return JsonResponse({'image_urls': image_urls})


def upload_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image = request.FILES['image']
        instance = Images.objects.create(user=request.user, image=image)
        
        return JsonResponse({'url': instance.get_image_url(request)})
    return JsonResponse({'error': 'Invalid request'}, status=400)


class ImageListView(ListView):
    model = Images
    
    template_name = "filemanager/test.html"

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
                         

    def get_queryset(self):
        queryset = super(ImageListView, self).get_queryset()
        
        queryset = queryset.filter(
           user=self.request.user
        ).order_by('-id')

        return queryset

