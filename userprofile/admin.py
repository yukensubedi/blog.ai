from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin


from .models import Profile

class UserAdminUpdated(UserAdmin):
    def __init__(self, *args, **kwargs):
        super(UserAdminUpdated, self).__init__(*args, **kwargs)
        self.list_display = ["id"] + list(self.list_display) + ["date_joined"]
        self.list_filter = list(self.list_filter) + ["date_joined"]




   
    

# Register your models here.
admin.site.unregister(User)
admin.site.register(User, UserAdminUpdated)
admin.site.register(Profile)




