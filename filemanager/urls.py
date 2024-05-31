from django.urls import path 
from . import views

urlpatterns = [ 
    path('url/<int:id>/', views.image_url, name='url'),
    path('gallery/', views.ImageListView.as_view(), name='gallery'),
    path('get_images/', views.get_images, name='get_images'),
    path('upload_image/', views.upload_image, name='upload_image'),
]