from django.db import models

class User(models.Model):
    name = models.CharField(max_length=100)

class File(models.Model):
    title = models.CharField(max_length=200)

class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name='bookmarks')
    file = models.ForeignKey(File, on_delete = models.CASCADE, related_name='users')
