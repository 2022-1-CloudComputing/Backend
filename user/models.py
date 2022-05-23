from django.contrib.auth.models import AbstractUser  # 기본 제공 user
from django.contrib.auth.models import Group
from django.db import models


# user
class User(AbstractUser):
    name = models.CharField(max_length=100, default="noname")
