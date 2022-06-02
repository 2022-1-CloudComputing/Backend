from math import fabs
import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from user.models import User
from file.serializers import *
from user.auth import is_token_valid
from file.folders3 import *
from file.models import Bookmark, File, Folder
from file.serializers import *
from file.serializers import BookmarkSerializer, FileSerializer
from file.storages import CRUD


class BookmarkDetailView(APIView): # 하나의 북마크 삭제
    def delete(self, request, userId="", bookmarkId=""):
        try:
            bookmark = Bookmark.objects.get(id = bookmarkId)
        except Bookmark.DoesNotExist:
            return JsonResponse({"message": "Requested Bookmark does not exist."})
        
        bookmarkUserId = bookmark.user.id;
        if (int(bookmarkUserId)==int(userId)):
            bookmark.delete();
            return JsonResponse({"message": "Bookmark successfully deleted."})
        else:
            return JsonResponse({"message": "Request user is not owner of requested bookmark."})

class BookmarkView(APIView): # 사용자의 북마크 리스트 조회 또는 북마크 추가
    def get(self, request, userId=""):
        try:
            user = User.objects.get(id=userId)
        except User.DoesNotExist:
            return JsonResponse("Requested user does not exist.")
        bookmarks = Bookmark.objects.filter(user = user)
        serializer = BookmarkSerializer(bookmarks, many=True)
        return JsonResponse(serializer.data, safe=False);

    def post(self, request, userId=""):
        received_json_data = json.loads(request.body.decode("utf-8"))
        fileId = received_json_data['fileId']
        try:
            user = User.objects.get(id=userId)
        except User.DoesNotExist:
            return JsonResponse({"message":"Requested user does not exist."})
        try:
            file = File.objects.get(id = fileId);
        except File.DoesNotExist:
            return JsonResponse({"message":"Reqeusted File does not exist."})

        if (Bookmark.objects.filter(user=user, file=file).exists()):
            return JsonResponse({"message": "Bookmark already exists."})
        else:
            bookmark = Bookmark(user=user, file=file)
            bookmark.save();
            serializer = BookmarkSerializer(bookmark)
            return JsonResponse(serializer.data)

class BookmarkSimpleView(APIView): # 파일의 북마크 여부 확인 위한 간단히 북마크 리스트 조회
    def get(self, request, userId=""):
        try:
            user = User.objects.get(id=userId)
        except User.DoesNotExist:
            return JsonResponse({"message":"Requested user does not exist."})
        bookmarks = Bookmark.objects.filter(user=user)
        serializer = BookmarkSimpleSerialiser(bookmarks, many=True)
        return JsonResponse(serializer.data, safe=False)

class HomeView(APIView):
    # user가 가지고 있는 파일 다 볼 수 있음
    def get(self, request, userId):
        # if not is_token_valid(token=request.headers["IdToken"], user_id=userId):
        #     return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            user = User.objects.get(username=userId)
            files = File.objects.filter(owner=user)
            res = []
            for file in files:
                res.append(
                    {
                        "file_id": file.file_id,
                        "file_path": "/".join(file.s3_url.split("/")[1:]),
                        "title": file.title,
                        "created_at": file.created_at,
                    }
                )
            return Response({"message": "success", "file_list": res}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": "invalid requests", "error": e.__str__()}, status=status.HTTP_403_FORBIDDEN)


class FilePreviewView(APIView):
    s3_client = CRUD()

    def get(self, request, userId, fileId):
        # permission 확인
        if not is_token_valid(token=request.headers["IdToken"], user_id=userId):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        try:
            response = self.s3_client.read(request, userId, fileId)
            return response
        except Exception as e:
            return Response({"message": "invalid requests", "error": e.__str__()}, status=status.HTTP_403_FORBIDDEN)

class FileUploadView(APIView):
    s3_client = CRUD()

    def post(self, request, userId):
        # permission 확인
        if not is_token_valid(token=request.headers["IdToken"], user_id=userId):
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            return self.s3_client.upload(request, userId)

        except Exception as e:
            return Response({"message": "invalid requests", "error": e.__str__()}, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, userId, fileId):
        # permission 확인
        if not is_token_valid(token=request.headers["IdToken"], user_id=userId):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        try:
            return self.s3_client.delete(request, userId, fileId)

        except Exception as e:
            return Response({"message": "invalid requests", "error": e.__str__()}, status=status.HTTP_403_FORBIDDEN)

    def get(self, request, userId, fileId):
        # permission 확인
        if not is_token_valid(token=request.headers["IdToken"], user_id=userId):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        try:
            return self.s3_client.download(request, userId, fileId)

        except Exception as e:
            return Response({"message": "invalid requests", "error": e.__str__()}, status=status.HTTP_403_FORBIDDEN)

    def put(self, request, userId, fileId):
        # permission 확인
        if not is_token_valid(token=request.headers["IdToken"], user_id=userId):
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        try:
            return self.s3_client.update(request, userId, fileId)

        except Exception as e:
            return Response({"message": "invalid requests", "error": e.__str__()}, status=status.HTTP_403_FORBIDDEN)


# s3 폴더 생성
class FolderCreate(APIView):
    def post(self, request):
        # permission 확인
        if not is_token_valid(token=request.headers["IdToken"], user_id=request.data["id"]):

            return Response(status=status.HTTP_403_FORBIDDEN)

        # 폴더 DB에 생성
        serializers = FolderSerializer(data=request.data)

        if not serializers.is_valid():
            return Response(serializers.errors, content_type="application/json", status=status.HTTP_400_BAD_REQUEST)
        serializers.save()

        # S3 Client 생성

        print(request.headers)

        s3_client = get_s3_client(
            request.headers["AccessKeyId"], request.headers["SecretKey"], request.headers["SessionToken"],
        )

        upload_folder(s3_client, "{0}/{1}{2}".format(request.data["id"], request.data["path"], request.data["name"]))

        return Response(serializers.data, content_type="application/json", status=status.HTTP_201_CREATED)


class FolderDetail(APIView):
    # 폴더 불러오기
    def get_object(self, folder_id):
        folder = get_object_or_404(Folder, folder_id=folder_id)
        return folder

    # 폴더 정보 조회
    def get(self, request, folder_id):
        # Permission 확인
        if not is_token_valid(token=request.headers["IdToken"], user_id=request.GET["id"]):
            return Response(status=status.HTTP_403_FORBIDDEN)

        # 폴더 불러오기
        folder = self.get_object(folder_id)
        serializers = FolderSerializer(folder)
        return Response(serializers.data, content_type="application/json", status=status.HTTP_200_OK)

    # 폴더 이름 변경
    def put(self, request, folder_id=None):
        # Permission 확인
        if not is_token_valid(token=request.headers["IdToken"], user_id=request.data["id"]):
            return Response(status=status.HTTP_403_FORBIDDEN)

        # 폴더 불러오기
        folder = self.get_object(folder_id)

        # S3 내의 폴더 이름 변경
        # S3 Client 생성
        s3_client = get_s3_client(
            request.headers["AccessKeyId"], request.headers["SecretKey"], request.headers["SessionToken"],
        )
        # S3 Key 이름 변경
        rename_move_folder(
            s3_client,
            "{0}/{1}{2}/".format(folder.user_id.user_id, folder.path, folder.name),
            "{0}/{1}{2}/".format(folder.user_id.user_id, folder.path, request.data["new_name"]),
        )

        # Serializer와 매칭
        serializers = FolderNameSerializer(folder, {"name": request.data["new_name"]})
        if serializers.is_valid():
            serializers.save()
            return Response("OK", content_type="application/json", status=status.HTTP_202_ACCEPTED)
        return Response(serializers.errors, content_type="application/json", status=status.HTTP_400_BAD_REQUEST)


class FolderElements(APIView):
    # 폴더 내 구성 요소 조회
    def get(self, request, folder_id):
        # Permission 확인
        if not is_token_valid(token=request.headers["IdToken"], user_id=request.GET["id"]):
            return Response(status=status.HTTP_403_FORBIDDEN)

        # 1. 폴더 목록 조회
        folders = Folder.objects.filter(parent_id=folder_id)
        folder_serializers = FolderSerializer(folders, many=True)

        # 2. 파일 목록 조회
        files = File.objects.filter(folder_id=folder_id)
        files_serializers = FileSerializer(files, many=True)

        # 3. 결과 응답
        return Response(
            {"folders": folder_serializers.data, "files": files_serializers.data,},
            content_type="application/json",
            status=status.HTTP_202_ACCEPTED,
        )


class FolderMove(APIView):
    # 폴더 불러오기
    def get_object(self, folder_id):
        folder = get_object_or_404(Folder, folder_id=folder_id)
        return folder

    # 폴더 이동
    def post(self, request, folder_id=None):
        # Permission 확인
        if not is_token_valid(token=request.headers["IdToken"], user_id=request.data["id"]):
            return Response(status=status.HTTP_403_FORBIDDEN)

        # 폴더 불러오기
        folder = self.get_object(folder_id)
        parent = self.get_object(request.data["loc"])

        # S3 내의 폴더 Trash 폴더로 이동
        # S3 Client  생성
        s3_client = get_s3_client(
            request.headers["AccessKeyId"], request.headers["SecretKey"], request.headers["SessionToken"],
        )
        # S3 Key 이름 변경
        rename_move_folder(
            s3_client,
            "{0}/{1}{2}/".format(folder.user_id.user_id, folder.path, folder.name),
            "{0}/{1}{2}/".format(folder.user_id.user_id, "{0}{1}/".format(parent.path, parent.name), folder.name),
        )

        # Serializer와 매칭
        serializers = FolderMoveSerializer(
            folder, {"parent_id": request.data["loc"], "path": "{0}{1}/".format(parent.path, parent.name)}
        )

        if serializers.is_valid():
            serializers.save()
            return Response("OK", content_type="application/json", status=status.HTTP_202_ACCEPTED)
        return Response(serializers.errors, content_type="application/json", status=status.HTTP_400_BAD_REQUEST)