import sys

import boto3

from dropbox.settings import AWS_REGION, AWS_STORAGE_BUCKET_NAME


# S3 Client 생성
def get_s3_client(access_key_id, secret_access_key, session_token=None):
    s3_client = boto3.client(
        's3',
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key,
        aws_session_token=session_token,
        region_name=AWS_REGION
    )
    return s3_client


# S3 URL 생성
def get_s3_url(path):
    return 'https://{0}.s3.amazonaws.com/{1}'.format(
        AWS_STORAGE_BUCKET_NAME,
        path
    )


# 파일 및 폴더 삭제
def delete_folder_file(s3_client, target):
    try:
        response = s3_client.delete_object(Bucket=AWS_STORAGE_BUCKET_NAME, Key=target)
        return response
    except Exception as e:
        print('Error on line {}'.format(
            sys.exc_info()[-1].tb_lineno), type(e).__name__, e
        )
        raise Exception('Delete folder Fail', e)


# ----------------------------
# 폴더 관련 모듈
# ----------------------------
# 폴더 생성
def upload_folder(s3_client, folder):
    try:
        response = s3_client.put_object(
            Bucket=AWS_STORAGE_BUCKET_NAME,
            Key=folder,
            ACL='public-read'
        )
        return response
    except Exception as e:
        print('Error on line {}'.format(
            sys.exc_info()[-1].tb_lineno), type(e).__name__, e
        )
        raise Exception('Upload Folder Fail', e)


# 폴더 이름 변경 혹은 이동
def rename_move_folder(s3_client, target, new_key):
    try:
        s3_client.copy_object(Bucket=AWS_STORAGE_BUCKET_NAME, Key=new_key, CopySource={
            'Bucket': AWS_STORAGE_BUCKET_NAME, 'Key': target
        }, ACL='public-read')

        # 내부 컨텐츠 이동
        contents = s3_client.list_objects(
            Bucket=AWS_STORAGE_BUCKET_NAME, Prefix=target, Delimiter="/")
        if 'CommonPrefixes' in contents:
            for content in contents['CommonPrefixes']:
                old_path = content['Prefix']
                new_path = new_key + old_path.replace(contents['Prefix'], '')
                s3_client.copy_object(Bucket=AWS_STORAGE_BUCKET_NAME, Key=new_path, CopySource={
                    'Bucket': AWS_STORAGE_BUCKET_NAME, 'Key': old_path
                }, ACL='public-read')
                s3_client.delete_object(Bucket=AWS_STORAGE_BUCKET_NAME, Key=old_path)

        s3_client.delete_object(Bucket=AWS_STORAGE_BUCKET_NAME, Key=target)
    except Exception as e:
        print('Error on line {}'.format(
            sys.exc_info()[-1].tb_lineno), type(e).__name__, e
        )
        raise Exception('Rename or Move Folder Fail', e)


# 폴더 비우기
def clear_folder(s3_client, folder):
    try:
        # 내부 컨텐츠 이동
        contents = s3_client.list_objects(
            Bucket=AWS_STORAGE_BUCKET_NAME, Prefix=folder, Delimiter="/")
        for content in contents['CommonPrefixes']:
            old_path = content['Prefix']
            s3_client.delete_object(Bucket=AWS_STORAGE_BUCKET_NAME, Key=old_path)
    except Exception as e:
        print('Error on line {}'.format(
            sys.exc_info()[-1].tb_lineno), type(e).__name__, e
        )
        raise Exception('Rename or Move Folder Fail', e)