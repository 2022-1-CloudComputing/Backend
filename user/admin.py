from django.contrib import admin

from user.models import User

# Register your models here.
admin.site.register(User)  # 이래야 admin 페이지에서도 확인 가능
