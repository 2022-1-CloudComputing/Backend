from botocore import serialize
from django.db import models
from user.models import User


class File(models.Model):
    title = models.CharField(max_length=200, null=True)  # 파일 이름
    file = models.FileField(blank=False, upload_to="media")  # 파일 자체
    file_path = models.CharField(max_length=200, null=False)  # 파일 저장 경로
    owner = models.ForeignKey("user.User", on_delete=models.CASCADE, null=False)
    created_at = models.DateTimeField(auto_now_add=True)  # 생성 일자

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["created_at", "title"]


# File 에 외래키로 폴더 지정 필요
# parent_folder_id= models.ForeignKey('Folder', on_delete=models.CASCADE, null=True)


class Folder(models.Model):
    folder_id = models.BigAutoField(auto_created=True, primary_key=True, serialize=True)
    parent_id = models.ForeignKey("self", on_delete=models.CASCADE, null=True, db_column="parent_id")
    user_id = models.ForeignKey(
        "user.User", on_delete=models.CASCADE, db_column="user_id", to_field="username"
    )  # user.User? user는 app같은데
    name = models.CharField(max_length=255)
    path = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        db_table = "folders"

    def __str__(self):
        return self.name


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookmarks")
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name="users")
