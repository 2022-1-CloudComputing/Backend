from django.db import models
from ..user.models import User


class File(models.Model):
    title = models.CharField(max_length=200)
    file = models.FileField(null=True, upload_to="file")
    created_at = models.DateTimeField(auto_now_add=True)

class Folder(models.Model):
    title = models.CharField(max_length=100)



class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookmarks")
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name="users")
