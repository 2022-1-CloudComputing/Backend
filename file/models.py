from django.db import models


class User(models.Model):
    name = models.CharField(max_length=100)


class File(models.Model):
    title = models.CharField(max_length=200, null=True)  # 파일 이름
    file = models.FileField(blank=False, upload_to="media")  # 파일 자체
    file_path = models.CharField(max_length=200, null=False)  # 파일 저장 경로
    owner = models.ForeignKey("auth.User", on_delete=models.CASCADE, null=False)
    created_at = models.DateTimeField(auto_now_add=True)  # 생성 일자

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["created_at", "title"]


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookmarks")
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name="users")
