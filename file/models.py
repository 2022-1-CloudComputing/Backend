from django.db import models
from user.models import User


class Folder(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title


class File(models.Model):
    title = models.CharField(max_length=200, null=True)  # 파일 이름
    file = models.FileField(upload_to="media", null=True)  # 파일 자체는 s3에 저장
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)  # 생성 일자

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["created_at", "title"]


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookmarks")
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name="users")

class Tag(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tags")
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name="tag_featured")
    name = models.CharField(max_length=100, null=False)
