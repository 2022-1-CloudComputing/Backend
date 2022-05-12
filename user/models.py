from django.db import models
from django.contrib.auth.models import AbstractUser  #기본 제공 user


#user
class User(AbstractUser):
    name = models.CharField(max_length=100, default="noname")