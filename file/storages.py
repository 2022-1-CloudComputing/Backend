import logging
import os

import boto3
from botocore.exceptions import ClientError
from matplotlib.image import thumbnail
from my_secrets import AWS
from PIL import Image
from user.models import User

from file.utils import is_image

from .models import File


class CRUD:
    def __init__(self):
        self.s3_client = boto3.client(
            "s3", aws_access_key_id=AWS.get("AWS_ACCESS_KEY_ID"), aws_secret_access_key=AWS.get("AWS_SECRET_ACCESS_KEY")
        )
        self.s3_resource = boto3.resource(
            "s3", aws_access_key_id=AWS.get("AWS_ACCESS_KEY_ID"), aws_secret_access_key=AWS.get("AWS_SECRET_ACCESS_KEY")
        )
        self.bucket_name = AWS.get("AWS_STORAGE_BUCKET_NAME")

    def upload(self, request, user_id):

        file = request.data.get("file")  # 파일 자체
        if not file:
            raise Exception("no file included")

        file_path = request.data.get("file_path", "")  # 파일이 저장되어야 하는 주소
        file_name = request.data.get("title", file.name)  # 파일 저장 이름 지정하지 않았다면 선택한 파일 이름 그대로 저장됨

        if "." not in file_name:
            extention = file.name.split(".")[-1]
            file_name = f"{file_name}.{extention}"

        file_path = f"{user_id}/{file_path}/{file_name}" if file_path else f"{user_id}/{file_name}"

        user = User.objects.get(id=user_id)  # user_id를 준다
        document = File.objects.create(title=file_name, file_path=file_path, owner=user)  # 파일 자체는 s3에 저장한다.

        user.files.append(document.id)

        try:
            self.s3_resource.Bucket(self.bucket_name).put_object(
                Body=file, Key=file_path, ACL=AWS.get("AWS_DEFAULT_ACL")
            )
            return True, document.id
        except ClientError as e:
            logging.error(e)
            return False, ""

    def delete(self, request, userId, fileId):
        user = User.objects.get(id=userId)

        file_info = File.objects.get(id=fileId, owner=user)
        if not file_info:
            return False

        try:
            result = self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_info.file_path,
            )
            file_info.delete()

        except ClientError as e:
            logging.error(e)
            return False

        return result

    def read(self, request, userId, fileId):

        user = User.objects.get(id=userId)
        file_info = File.objects.get(id=fileId, owner=user)
        if not file_info:
            return False, ""

        try:
            self.s3_resource.meta.client.download_file(
                Bucket=self.bucket_name, Key=file_info.file_path, Filename=f"temp/{file_info.file_path}"
            )
            thumbnail_path = f"preview/{file_info.file_path}"

            extension = thumbnail_path.split(".")[-1]
            if is_image(extension):
                source = Image.open(thumbnail_path)
                source.thumbnail((128, 128), Image.ANTIALIAS)  # 썸네일 생성
                source.save(thumbnail_path, "jpeg")
            return True, thumbnail_path
        except:
            return False

    def download(self, request, userId, fileId):
        user = User.objects.get(id=userId)
        file_info = File.objects.get(id=fileId, owner=user)
        if not file_info:
            return False, ""

        try:
            file_path = file_info.file_path
            raw_file_path = file_path.split("/")
            root_path = "/".join(raw_file_path[1:-1])
            orig_file_name = raw_file_path[-1]
            extension = orig_file_name.split(".")[-1]

            new_file_name = request.GET.get("save_as", orig_file_name)  # 다운받을 이름 명시하지 않았다면 원래 파일 이름으로 저장

            if "." not in new_file_name:
                new_file_name += f".{extension}"
            save_as = "/".join([userId, root_path, new_file_name])
            save_as = save_as.replace("//", "/")

            temp_path = "media/media/"
            for path in save_as.split("/"):
                if not os.path.exists(f"{temp_path}/{path}") and "." not in path:
                    os.mkdir(f"{temp_path}/{path}")
                    temp_path = f"{temp_path}/{path}"

            self.s3_resource.meta.client.download_file(
                Bucket=self.bucket_name, Key=file_path, Filename=f"media/media/{save_as}"
            )

            return True, f"media/media/{save_as}"
        except ClientError as e:
            logging.error(e)
            return False, ""

    def update(self, request, userId=""):
        content = request.data.get("content", {})
        user_id = userId

        if content == "rename":
            old_path = f"{user_id}\\{content.get('old_path')}"
            new_path = f"{user_id}\\{content.get('new_path')}"
            try:
                bucket = self.s3_resource.Bucket(self.bucket_name)
                for object in bucket.objects.filter(Prefix=old_path):
                    srcKey = object.key
                    if not srcKey.endswith("/"):
                        destFileKey = new_path + "/" + srcKey.split("/")[-1]
                        copysource = self.bucket_name + "/" + srcKey

                        self.s3_client.Object(self.bucket_name, destFileKey).copy_from(CopySource=copysource)
                        self.s3_client.Object(self.bucket_name, copysource).delete()
            except ClientError as e:
                logging.error(e)
                return False
            return True
        else:  # 그 외 요청 받기
            pass
