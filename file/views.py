from math import fabs
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from file.models import Bookmark, File
from user.models import User
from file.serializers import BookmarkSerializer, BookmarkSimpleSerialiser, FileSerializer

from file.storages import CRUD

import json

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
        
class FileUploadView(APIView):
    s3_client = CRUD()

    def post(self, request, userId="", fileId=""):
        serializer = FileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            if request.method == "POST" and len(request.FILES) != 0:
                res = self.s3_client.upload(request, userId)
                if res:
                    return JsonResponse({"message": "success upload"})
                else:
                    return JsonResponse({"message": "fail upload"})
            else:
                return JsonResponse({"message": "invalid requests"})
        else:
            return JsonResponse({"message": "invalid form"})

    def delete(self, request, userId="", fileId=""):
        if request.method == "DELETE":
            res = self.s3_client.delete(request, userId)
            if res:
                return JsonResponse({"message": "success delete"})
            else:
                return JsonResponse({"message": "fail delete"})
        else:
            return JsonResponse({"message": "invalid requests"})

    # def get(self, request, userId, fileId):
    #     if request.method == "GET":
    #         res = self.s3_client.read(request)
    #         if res:
    #             return JsonResponse({"message": "success read"}, status=200)
    #         else:
    #             return JsonResponse({"message": "fail read"}, status=400)
    #     else:
    #         return JsonResponse({"message": "invalid requests"})

    def get(self, request, userId="", fileId=""):
        if request.method == "GET":
            res = self.s3_client.download(request, userId)
            if res:
                return JsonResponse({"message": "success download"})
            else:
                return JsonResponse({"message": "fail download"})
        else:
            return JsonResponse({"message": "invalid requests"})

    def put(self, request, userId="", fileId=""):
        if request.method == "PUT":
            res = self.s3_client.update(request, userId)
            if res:
                return JsonResponse({"message": "success update"})
            else:
                return JsonResponse({"message": "fail update"})
        else:
            return JsonResponse({"message": "invalid requests"})