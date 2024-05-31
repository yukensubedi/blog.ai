from django.urls import path, re_path, include
from account.urls import urlpatterns as accountUrls
from . import views 

urlpatterns = [
    re_path(r'^login/', views.LoginView.as_view(), name='user_login'),
    re_path(r'^signup/', views.SignupView.as_view(), name='user_signup'),
]+ accountUrls