from django.contrib import admin

from .models import File, Folder, Tag

# Register your models here.
admin.site.register(File)
admin.site.register(Tag)
admin.site.register(Folder)

