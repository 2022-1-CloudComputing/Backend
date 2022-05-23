from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from user.models import User

from file.models import Bookmark, File
from file.serializers import BookmarkSerializer, FileSerializer
from file.storages import CRUD


class BookmarkViewSet(viewsets.ViewSet):
    lookup_field = "userId"

    def list(self, request, userId: int):
        user = User.objects.get(id=userId)  # 원래 id인데 외부키 설정으로 인해 접근 오류가 뜸. 다음과 같이 수정
        queryset = user.bookmarks.all()
        serializer = BookmarkSerializer(queryset, many=True)
        return Response(serializer.data)


def home(requests, userId=""):
    user = User.objects.get(id=userId)
    file_list = user.files.all()  # 이 부분 맞춰 수정해야 함
    return {"file_list": file_list}


class FileUploadView(APIView):
    s3_client = CRUD()

    def post(self, request, userId=""):
        if request.method == "POST" and len(request.data) != 0:
            res, msg = self.s3_client.upload(request, userId)
            if res:
                return JsonResponse({"message": "success upload", "fileId": msg})
            else:
                return JsonResponse({"message": "fail upload"})
        else:
            return JsonResponse({"message": "invalid requests"})

    def delete(self, request, userId="", fileId=""):
        if request.method == "DELETE":
            res = self.s3_client.delete(request, userId, fileId)  # body에 담아야 함?
            if res:
                return JsonResponse({"message": "success delete"})
            else:
                return JsonResponse({"message": "fail delete"})
        else:
            return JsonResponse({"message": "invalid requests"})


    def get(self, request, userId="", fileId=""):
        if request.method == "GET":
            res,msg = self.s3_client.download(request, userId, fileId)
            if res:
                return JsonResponse({"message": "success download", "file_path" : msg})
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


    def preview(self, request, userId="", fileId=""):
        if request.method == "GET":
            res,msg = self.s3_client.download(request, userId, fileId)
            if res:
                return JsonResponse({"message": "success download", "file_path" : msg})
            else:
                return JsonResponse({"message": "fail download"})
        else:
            return JsonResponse({"message": "invalid requests"})