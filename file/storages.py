import os

from botocore.exceptions import ClientError
from dropbox.settings import (AWS_DEFAULT_ACL, AWS_REGION, AWS_STORAGE_BUCKET_NAME,
                              MEDIA_URL)
from PIL import Image
from rest_framework import status
from rest_framework.response import Response
from user.models import User

from file.folders3 import get_s3_client, get_s3_resource
from file.utils import is_image

from .models import File, Folder


class CRUD:
    def __init__(self):
        self.bucket_name = AWS_STORAGE_BUCKET_NAME

    def upload(self, request, user_id):
        file_obj = request.data.get("file")  # 파일 자체
        if not file_obj:
            raise Exception("no file included")
        file_path = request.data.get("file_path", "")
        file_path = file_path.replace("\\", "/")

        file_name = request.data.get("title")  # 파일 저장 이름 지정하지 않았다면 선택한 파일 이름 그대로 저장됨

        if not file_name:
            file_name = file_obj.name
        if "." not in file_name:
            extention = file_obj.name.split(".")[-1]
            file_name = f"{file_name}.{extention}"
        else:
            extention = file_name.split(".")[-1]
        try:
            file_size = int(request.data.get("file_size"))
        except:
            raise Exception("file size not included")

        raw_folder = file_path.split("/")
        if len(raw_folder) <= 1:  # 폴더 경로가 없을 경우
            folder_path = ""
            folder_name = user_id
        else:  # 폴더 경로가 있을 경우
            folder_name = raw_folder[-2] + "/" if raw_folder[-2] else ""
            folder_path = "/".join(raw_folder[:-2])
            folder_path = folder_path + "/" if folder_path else ""

        try:
            folder = Folder.objects.get(user_id=user_id, path=folder_path, name=folder_name)
        except Folder.DoesNotExist as e:
            raise Folder.DoesNotExist(e)

        if user_id == folder_name:
            s3_url = f"{folder_name}/{file_name}"
        else:
            t_user_id = f"{user_id}/"
            s3_url = f"{t_user_id}{folder_path}{folder_name}{file_name}"

        user = User.objects.get(username=user_id)  # user_id를 준다

        file = File.objects.create(title=file_name, owner=user, folder_id=folder, file_size=file_size, s3_url=s3_url)

        s3_resource = get_s3_resource(
            request.headers["AccessKeyId"], request.headers["SecretKey"], request.headers["SessionToken"],
        )
        try:
            s3_resource.Bucket(self.bucket_name).put_object(Body=file_obj, Key=s3_url, ACL=AWS_DEFAULT_ACL)
        except ClientError as e:
            return Response(
                {"message": "fail upload", "error": e.__str__()}, status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        return Response(
            {
                "message": "success upload",
                "file_id": file.file_id,
                "file_name": file_name,
                "file_path": "/".join(s3_url.split("/")[1:-1]),
                "s3_url": s3_url,
                "file_size": file.file_size,
                "created_at": file.created_at,
                "folder_id" : file.folder_id.folder_id
            },
            status=status.HTTP_201_CREATED,
        )

    def delete(self, request, userId, fileId):
        user = User.objects.get(username=userId)
        try:
            file = File.objects.get(file_id=fileId, owner=user)
        except Exception as e:
            raise Exception("file not exists")

        folder = Folder.objects.get(folder_id=file.folder_id.folder_id)
        folder_path = folder.path
        folder_name = folder.name

        if not folder_path and not folder_name:
            s3_url = f"{userId}/{file.title}"
        elif folder_name == userId:
            s3_url = f"{userId}/{folder_path}{file.title}"
        else:
            s3_url = f"{userId}/{folder_path}{folder_name}{file.title}"

        try:
            s3_client = get_s3_client(
                request.headers["AccessKeyId"], request.headers["SecretKey"], request.headers["SessionToken"],
            )
            s3_client.delete_object(Bucket=self.bucket_name, Key=s3_url)
        except ClientError as e:
            return Response(
                {"message": "fail delete", "error": e.__str__()}, status=status.HTTP_503_SERVICE_UNAVAILABLE
            )


        file.delete()  # 객체도 삭제
        return Response({"message": "success delete"}, status=status.HTTP_200_OK)

    def download(self, request, userId, fileId):
        user = User.objects.get(username=userId)
        temp_path = MEDIA_URL
        print(temp_path)

        try:
            file_info = File.objects.get(file_id=int(fileId), owner=user)
        except Exception as e:
            raise Exception("file not exists")
        file_name = file_info.title
        if not os.path.exists(temp_path):
            os.mkdir(temp_path)
        extension = file_name.split(".")[-1]
        s3_url = file_info.s3_url

        new_file_name = request.GET.get("save_as", file_info.title)  # 다운받을 이름 명시하지 않았다면 원래 파일 이름으로 저장

        if "." not in new_file_name:
            new_file_name += f".{extension}"
        save_as = "/".join([userId, "Downloads", new_file_name])
        save_as = save_as.replace("\\", "/")

        for path in save_as.split("/"):
            if not os.path.exists(f"{temp_path}/{path}"):
                if "." in path:
                    break
                os.mkdir(f"{temp_path}/{path}")
            temp_path = f"{temp_path}/{path}"

        s3_client = get_s3_client(
            request.headers["AccessKeyId"], request.headers["SecretKey"], request.headers["SessionToken"],
        )
        try:
            s3_client.download_file(Bucket=self.bucket_name, Key=s3_url, Filename=f"{MEDIA_URL}{save_as}")
        except ClientError as e:
            return Response({"message": "fail download", "error": e}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        return Response(
            {
                "message": "success download",
                "file_name": file_name,
                "s3_url": s3_url,
                "file_path": f"{MEDIA_URL}{save_as}",
                "file_size": file_info.file_size,
                "created_at": file_info.created_at,
            },
            status=status.HTTP_201_CREATED,
        )

    # def share(self, request, userId, fileId):
    #     user = User.objects.get(username=userId)

    #     try:
    #         file = File.objects.get(file_id=fileId, owner=user)
    #     except Exception as e:
    #         raise Exception("file not exists")


    #     return Response({
    #         "file_url": "https://{0}.s3.{1}.amazonaws.com/{2}".format(AWS_STORAGE_BUCKET_NAME, AWS_REGION,file.title)
    #     })

    def update(self, request, userId, fileId):
        user = User.objects.get(username=userId)
        try:
            file_info = File.objects.get(file_id=int(fileId), owner=user)
        except Exception as e:
            raise Exception("file not exists")
        before_s3_url = file_info.s3_url
        new_s3_url = before_s3_url
        is_change = False

        new_title = request.data.get("title")
        if new_title is not None:
            extension = file_info.title.split(".")[-1]
            if "." not in new_title:
                new_title += f".{extension}"
            new_s3_url = "/".join(file_info.s3_url.split("/")[:-1]) + f"/{new_title}"
            is_change = True
        else:
            new_title = file_info.title

        new_folder = request.data.get("folder")
        if new_folder is not None:
            raw_folder = new_folder.split("/")
            if len(raw_folder) <= 1:  # 폴더 경로가 없을 경우
                folder_path = ""
                folder_name = ""
            else:  # 폴더 경로가 있을 경우
                folder_name = raw_folder[-2] + "/" if raw_folder[-2] else ""
                folder_path = "/".join(raw_folder[:-2])
                folder_path = folder_path + "/" if folder_path else ""

            new_s3_url = f"{userId}/{folder_path}{folder_name}{new_title}"
            is_change = True
        else:
            new_folder = "/".join(file_info.s3_url.split("/")[1:-1]) + f"/{new_title}"

        if is_change:
            s3_client = get_s3_client(
                request.headers["AccessKeyId"], request.headers["SecretKey"], request.headers["SessionToken"],
            )
            try:
                s3_client.copy_object(
                    Bucket=AWS_STORAGE_BUCKET_NAME,
                    Key=new_s3_url,
                    CopySource={"Bucket": AWS_STORAGE_BUCKET_NAME, "Key": before_s3_url},
                    ACL=AWS_DEFAULT_ACL,
                )

                # 테스트할 때는 삭제되면 귀찮으니까 주석
                s3_client.delete_object(Bucket=AWS_STORAGE_BUCKET_NAME, Key=before_s3_url)

            except ClientError as e:
                return Response(
                    {"message": "fail update. maybe already updated", "error": e.__str__()},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )

            # 파일 업데이트
            File.objects.filter(file_id=int(fileId), owner=user).update(title=new_title, s3_url=new_s3_url)

            return Response(
                {"message": "success update", "file_name": new_title, "s3_url": new_s3_url}, status=status.HTTP_200_OK,
            )
        else:
            return Response({"message": "nothing update"}, status=status.HTTP_202_ACCEPTED,)

    def read(self, request, userId, fileId):
        user = User.objects.get(username=userId)
        try:
            file_info = File.objects.get(file_id=int(fileId), owner=user)
        except Exception as e:
            raise Exception("file not exists")
        file_name = file_info.title
        extension = file_name.split(".")[-1].lower()

        if not is_image(extension):
            return Response({"message": "this is not image file. cannot preview"}, status=status.HTTP_400_BAD_REQUEST)

        temp_path = MEDIA_URL

        s3_path = file_info.s3_url

        save_as = "/".join([userId, "preview", file_name])
        save_as = save_as.replace("\\", "/")

        for path in save_as.split("/"):
            if not os.path.exists(f"{temp_path}/{path}"):
                if "." in path:
                    break
                os.mkdir(f"{temp_path}/{path}")
            temp_path = f"{temp_path}/{path}"

        thumbnail_path = f"{MEDIA_URL}{save_as}"
        s3_client = get_s3_client(
            request.headers["AccessKeyId"], request.headers["SecretKey"], request.headers["SessionToken"],
        )
        try:
            s3_client.download_file(Bucket=self.bucket_name, Key=s3_path, Filename=f"{MEDIA_URL}{save_as}")

        except ClientError as e:
            return Response(
                {"message": "fail download", "error": e.__str__()}, status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        source = Image.open(thumbnail_path)
        source.thumbnail((200, 200), Image.ANTIALIAS)  # 썸네일 생성
        source.save(thumbnail_path)

        return Response(
            {
                "message": "thumbnail created",
                "file_name": file_name,
                "s3_url": s3_path,
                "file_path": f"{MEDIA_URL}{save_as}",
            },
            status=status.HTTP_201_CREATED,
        )
