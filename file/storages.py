import logging
import os

import boto3
from botocore.exceptions import ClientError
from my_secrets import AWS
from PIL import Image
from user.models import User

from file.utils import is_image

from .models import File, Folder


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

        file_path = request.data.get("file_path", "")
        file_path = file_path.replace("\\", "/")
        try:
            folder = Folder.objects.get(title=file_path)
        except:  # Folder 객체 중복 방지
            folder = Folder.objects.create(title=file_path)

        file_name = request.data.get("title", file.name)  # 파일 저장 이름 지정하지 않았다면 선택한 파일 이름 그대로 저장됨

        if "." not in file_name:
            extention = file.name.split(".")[-1]
            file_name = f"{file_name}.{extention}"
        else:
            extention = file_name.split(".")[-1]

        user = User.objects.get(id=user_id)  # user_id를 준다
        document = File.objects.create(title=file_name, folder=folder, owner=user)  # 파일 자체는 s3에 저장한다.

        # user.files.append({"file_id": document.id, "folder_id": folder.id})

        try:
            self.s3_resource.Bucket(self.bucket_name).put_object(
                Body=file, Key=f"{user_id}/{document.id}.{extention}", ACL=AWS.get("AWS_DEFAULT_ACL")
            )
            return True, {"file_id": document.id, "folder_id": folder.id}
        except ClientError as e:
            logging.error(e)
            return False, ""

    def delete(self, request, userId, fileId):
        user = User.objects.get(id=userId)

        try:
            file_info = File.objects.get(id=fileId, owner=user)
        except:
            return False

        extension = file_info.title.split(".")[-1]
        try:
            result = self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=f"{userId}/{fileId}.{extension}",
            )
            file_info.delete()  # 객체도 삭제

        except ClientError as e:
            logging.error(e)
            return False

        return result

    def download(self, request, userId, fileId):
        user = User.objects.get(id=userId)
        try:
            file_info = File.objects.get(id=fileId, owner=user)
        except:
            return False, ""

        try:
            file_path = file_info.folder.__str__()
            extension = file_info.title.split(".")[-1]

            new_file_name = request.GET.get("save_as", file_info.title)  # 다운받을 이름 명시하지 않았다면 원래 파일 이름으로 저장

            if "." not in new_file_name:
                new_file_name += f".{extension}"
            save_as = "/".join([userId, file_path, new_file_name])
            save_as = save_as.replace("\\", "/")

            temp_path = "media/media"
            for path in save_as.split("/"):
                if not os.path.exists(f"{temp_path}/{path}"):
                    if "." in path:
                        break
                    os.mkdir(f"{temp_path}/{path}")
                temp_path = f"{temp_path}/{path}"

            self.s3_resource.meta.client.download_file(
                Bucket=self.bucket_name, Key=f"{userId}/{fileId}.{extension}", Filename=f"media/media/{save_as}"
            )

            return True, f"media/media/{save_as}"
        except ClientError as e:
            logging.error(e)
            return False, ""

    def update(self, request, userId, fileId):

        user = User.objects.get(id=userId)
        try:
            file_info = File.objects.get(id=fileId, owner=user)
        except:
            return False, ""

        new_folder = request.data.get("folder", {}) or file_info.folder
        try:
            folder = Folder.objects.get(title=new_folder)
        except:
            folder = Folder.objects.create(title=new_folder)

        extension = file_info.title.split(".")[-1]
        title = request.data.get("title", "") or file_info.title

        if "." not in title:
            title += f".{extension}"

        File.objects.update(folder=folder, title=title)

        new_path = f"{userId}/{folder.__str__() }/{title}"
        return True, new_path

    def read(self, request, userId, fileId):

        user = User.objects.get(id=userId)
        try:
            file_info = File.objects.get(id=fileId, owner=user)
        except:
            return False, ""

        extension = file_info.title.split(".")[-1]
        thumbnail_path = f"{userId}/preview_{fileId}.{extension}"

        if os.path.exists(f"media/media/{userId}/preview_{fileId}.jpeg"):
            print("already exists")
            return True, f"media/media/{userId}/preview_{fileId}.jpeg"

        temp_path = "media/media"
        for path in thumbnail_path.split("/"):
            if not os.path.exists(f"{temp_path}/{path}"):
                if "." in path:
                    break
                os.mkdir(f"{temp_path}/{path}")
            temp_path = f"{temp_path}/{path}"

        try:
            self.s3_resource.meta.client.download_file(
                Bucket=self.bucket_name, Key=f"{userId}/{fileId}.{extension}", Filename=f"media/media/{thumbnail_path}"
            )

            if is_image(extension):
                source = Image.open(f"media/media/{thumbnail_path}")
                source.thumbnail((20, 20), Image.ANTIALIAS)  # 썸네일 생성
                save_path = f"media/media/{thumbnail_path}".replace(f".{extension}", ".jpeg")
                source.save(save_path, "jpeg")
                # 원본 파일 삭제
                os.remove(f"media/media/{thumbnail_path}")
            return True, thumbnail_path
        except:
            return False
