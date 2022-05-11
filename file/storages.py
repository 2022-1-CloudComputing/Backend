
import logging

import boto3
from botocore.exceptions import ClientError
from dropbox.settings import AWS_ACCESS_KEY_ID, AWS_DEFAULT_ACL, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME
from PIL import Image


class CRUD:
    def __init__(self):
        self.s3_client = boto3.client(
            "s3", aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
        self.s3_resource = boto3.resource(
            "s3", aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
        self.bucket_name = AWS_STORAGE_BUCKET_NAME

    def upload(self, user_id, file):
        filepath = file["filepath"]
        file = filepath.split("/")[-1].split(".")
        filename, filetype = file[0], file[1]
        r_savepath = file.get("savepath")
        r_filename = file.get("filename")

        # extra_args = {"ContentType": file.content_type}

        savepath = f"{user_id}/{r_savepath}/" if r_savepath else f"{user_id}/"
        savepath = f"{savepath}/{r_filename}.{filetype}" if r_filename else f"{savepath}/{filename}.{filetype}"
        try:
            result = self.s3_client.upload_file(
                filepath, self.bucket_name, savepath, ExtraArgs={"ACL": AWS_DEFAULT_ACL}
            )
        except ClientError as e:
            logging.error(e)
            return False
        return result

    def delete(self, user_id, file):
        fileid = f"{user_id}/{file['fileid']}"
        try:
            result = self.s3_client.delete_object(Bucket=self.bucket_name, Key=fileid)
        except ClientError as e:
            logging.error(e)
            return False
        return result

    def deletes(self, user_id, file):  # 여러 개를 한번에 delete
        fileid_list = [{"Key": f"{user_id}/{fileid}"} for fileid in file["fileids"]]
        try:
            result = self.s3_client.delete_objects(Bucket=self.bucket_name, Delete={"Objects": fileid_list})
        except ClientError as e:
            logging.error(e)
            return False
        return result

    def read(self, user_id, file):
        fileid = f"{user_id}/{file['fileid']}"
        filetype = file["filetype"]
        bucket = self.s3_resource.Bucket(self.bucket_name)
        object = bucket.Object(fileid)

        try:
            response = object.get()
        except ClientError as e:
            logging.error(e)
            return False

        file_stream = response["Body"]
        if filetype in ["jpg", "jpeg"]:
            source = Image.open(file_stream)
        else:  # 동영상이거나 파일일 경우
            source = file_stream
        return source

    def download(self, user_id, file):
        fileid = f"{user_id}/{file['fileid']}"
        filetype = file["filetype"]

        # file_path = os.path.join(IMAGE_DIR, 'macbookpro.png')
        file_path = f"downloads/{fileid}.{filetype}"
        try:
            with open(file_path, "wb") as f:
                self.s3_client.download_fileobj(self.bucket_name, fileid, f)
        except ClientError as e:
            logging.error(e)
            return False

    def update(self, user_id, file, content):
        old_fileid = f"{user_id}/{file['fileid']}"
        new_fileid = f"{user_id}/{file['new_fileid']}"

        if content.get("request") == "rename":
            try:
                self.s3_client.Object(self.bucket_name, new_fileid).copy_from(CopySource=old_fileid)
                self.s3_client.Object(self.bucket_name, old_fileid).delete()
            except ClientError as e:
                logging.error(e)
                return False
            return True
        else:  # 그 외 요청 받기
            pass