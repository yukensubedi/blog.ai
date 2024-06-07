from django.contrib import admin
from . models import *

admin.site.register(Blog)
admin.site.register(Topics )
# admin.site.register(History)
# admin.site.register(BlogSection)
admin.site.register(BlogImage)
admin.site.register(TokenConsumption)
admin.site.register(ContactForms)


class BlogSectionAdmin(admin.ModelAdmin):
    # Specify the fields to display in the list view
    list_display = ('id', 'title', 'slug')  # Add any other fields you want to display

    # Optionally, add fields to search and filter
    search_fields = ('title', 'slug')  # Add any fields you want to enable search on
    list_filter = ('title',)  # Add any fields you want to filter by

# Register the model with the custom admin class
admin.site.register(BlogSection, BlogSectionAdmin)

class HistoryAdmin(admin.ModelAdmin):
    # Specify the fields to display in the list view
    list_display = ('id', 'title', 'slug')  # Add any other fields you want to display

    # Optionally, add fields to search and filter
    search_fields = ('title', 'slug')  # Add any fields you want to enable search on
    list_filter = ('title',)  # Add any fields you want to filter by

# Register the model with the custom admin class
admin.site.register(History, HistoryAdmin)