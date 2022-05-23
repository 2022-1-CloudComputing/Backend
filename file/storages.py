
import logging

import boto3
from botocore.exceptions import ClientError
from dropbox.settings import AWS_ACCESS_KEY_ID, AWS_DEFAULT_ACL, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME


class CRUD:
    def __init__(self):
        self.s3_client = boto3.client(
            "s3", aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
        self.s3_resource = boto3.resource(
            "s3", aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
        self.bucket_name = AWS_STORAGE_BUCKET_NAME

    def upload(self, request, userId=""):
        file = request.data.get("file")  # 파일 자체
        if not file:
            raise Exception("no file included")

        file_path = request.data.get("file_path", "")  # 파일이 저장되어야 하는 주소
        file_name = request.data.get("title", file.name)  # 파일 저장 이름 지정하지 않았다면 기본값이 저장됨
        user_id = userId  #  request.user._auth_user_id

        file_path = f"{user_id}/{file_path}/{file_name}" if file_path else f"{user_id}/{file_name}"

        try:
            result = self.s3_resource.Bucket(self.bucket_name).put_object(
                Body=file,
                Key=file_path,
                ACL=AWS_DEFAULT_ACL,
                ContentType=file.content_type,
            )
        except ClientError as e:
            logging.error(e)
            return False
        return result

    def delete(self, request, userId=""):
        file_path = request.data.get("file_path", "")  # 삭제될 파일의 경로
        user_id = userId  #  request.user._auth_user_id

        file_path = f"{user_id}/{file_path}"
        try:
            result = self.s3_client.delete_object(Bucket=self.bucket_name, Key=file_path)
        except ClientError as e:
            logging.error(e)
            return False
        return result

    # def read(self, request, userId=""):
    #     try:
    #         file_path = request.GET.get("file_path", "")  # 다운받아야 하는 파일의 경로

    #         orig_file_name = file_path.split("\\")[-1]
    #         save_as = request.GET.get("save_as", file_path)

    #         bucket = self.s3_resource.Bucket(self.bucket_name)
    #         user_id = userId

    #         file = bucket.Object(file_path)
    #         ext = save_as.split(".")[-1]

    #         check_exist_path = ""
    #         for path in ["media", user_id, save_as]:
    #             if "." in path:
    #                 continue
    #             check_exist_path += f"{path}/"
    #             if not os.path.exists(check_exist_path):
    #                 os.mkdir(check_exist_path)

    #         file.download_file(Filename=f"media\{user_id}\{save_as}\preview.{ext}")
    #         if is_image(ext):
    #             source = Image.open(f"media\{user_id}\{save_as}\preview.{ext}")
    #             source.thumbnail((128, 128), Image.ANTIALIAS)  # 썸네일 생성
    #             source.save(f"media\{user_id}\{save_as}\thumbnail.{ext}", "jpeg")
    #         return True
    #     except:
    #         return False

    def download(self, request, userId=""):
        try:
            file_path = request.GET.get("file_path", "")  # 다운받아야 하는 파일의 경로
            raw_file_path = file_path.split("\\")
            root_path = "\\".join(raw_file_path[:-1])
            orig_file_name = raw_file_path[-1]
            new_file_name = request.GET.get("save_as", orig_file_name)  # 다운받을 이름 명시하지 않았다면 원래 파일 이름으로 저장
            save_as = "\\".join([root_path, new_file_name])

            bucket = self.s3_resource.Bucket(self.bucket_name)
            user_id = userId

            file = bucket.Object(file_path)
            file.download_file(Filename=f"media\\{user_id}\\{save_as}")
        except ClientError as e:
            logging.error(e)
            return False

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
