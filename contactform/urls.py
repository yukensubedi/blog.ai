from django.urls import path
from .views import *


urlpatterns = [
    path('test/', test),
    path('handleform/', HandleForm.as_view(), name='handleform'),
    path('create/', CreateContactForm.as_view(), name='create_form'),
    path('list/', ListContactForm.as_view(), name='list_form'),
    path('<int:pk>/edit/', UpdateContactFormView.as_view(), name='edit_form'),
    path('<pk>/delete', ContactFormDeleteView.as_view(), name='delete_form'),
    path('<pk>/', ListContactFormContentView.as_view(), name='list_form_content'),
]