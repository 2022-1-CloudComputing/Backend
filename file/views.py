from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from user.models import User

from file.models import Bookmark, File, Tag
from file.serializers import BookmarkSerializer, FileSerializer, TagSerializer
from file.storages import CRUD

import json

class BookmarkViewSet(viewsets.ViewSet):
    lookup_field = "userId"

    def list(self, request, userId: int):
        user = User.objects.get(id=userId)  # 원래 id인데 외부키 설정으로 인해 접근 오류가 뜸. 다음과 같이 수정
        queryset = user.bookmarks.all()
        serializer = BookmarkSerializer(queryset, many=True)
        return Response(serializer.data)


def home(request, userId):
    # user가 가지고 있는 파일 다 볼 수 있음
    try:
        user = User.objects.get(id=userId)
        files = File.objects.filter(owner=user)
    except:
        return JsonResponse({"message": "fail"})

    res = [f"{userId}/{file.folder}/{file.title}" for file in files]
    return JsonResponse({"message": "success", "file_list": res})


def preview(request, userId, fileId):
    s3_client = CRUD()
    res, msg = s3_client.read(request, userId, fileId)
    if res:
        return JsonResponse({"message": "success download", "file_path": msg})
    else:
        return JsonResponse({"message": "fail download"})


class FileUploadView(APIView):
    s3_client = CRUD()

    def post(self, request, userId):
        if request.method == "POST" and len(request.data) != 0:
            res, msg = self.s3_client.upload(request, userId)
            if res:
                return JsonResponse({"message": "success upload", **msg})
            else:
                return JsonResponse({"message": "fail upload"})
        else:
            return JsonResponse({"message": "invalid requests"})

    def delete(self, request, userId, fileId):
        if request.method == "DELETE":
            res = self.s3_client.delete(request, userId, fileId)  # body에 담아야 함?
            if res:
                return JsonResponse({"message": "success delete"})
            else:
                return JsonResponse({"message": "fail delete"})
        else:
            return JsonResponse({"message": "invalid requests"})

    def get(self, request, userId, fileId):
        if request.method == "GET":
            res, msg = self.s3_client.download(request, userId, fileId)
            if res:
                return JsonResponse({"message": "success download", "file_path": msg})
            else:
                return JsonResponse({"message": "fail download"})
        else:
            return JsonResponse({"message": "invalid requests"})

    def put(self, request, userId, fileId):
        if request.method == "PUT":
            res, msg = self.s3_client.update(request, userId, fileId)
            if res:
                return JsonResponse({"message": "success update", "file_path": msg})
            else:
                return JsonResponse({"message": "fail update"})
        else:
            return JsonResponse({"message": "invalid requests"})





class TagSearchView(APIView):
    # 태그로 파일 리스트 검색
    def get(self, request, userId="", tagName=""):
        try:
            user=  User.objects.get(id=userId)
        except User.DoesNotExist:
            return JsonResponse({"message":"Requested user does not exist."})
        tags = Tag.objects.filter(user=user).filter(name=tagName)
        serializer = TagSerializer(tags, many=True)
        return JsonResponse(serializer.data, safe=False)

class TagView(APIView):
    # 태그 추가
    def post(self, request, userId=""):
        received_json_data = json.loads(request.body.decode("utf-8"))
        fileId = received_json_data['fileId']
        tagName = received_json_data['tagName']
        try:
            user = User.objects.get(id=userId)
        except User.DoesNotExist:
            return JsonResponse({"message":"Requested user does not exist."})
        try:
            file = File.objects.get(id=fileId)
        except File.DoesNotExist:
            return JsonResponse({"message":"Requested file does not exist."})
        
        if (Tag.objects.filter(user=user, name=tagName).exists()):
            return JsonResponse({"message":"Requested tag already exist."})
        else:
            tag = Tag(user=user,file=file,name=tagName)
            tag.save()
            serializer = TagSerializer(tag)
            return JsonResponse(serializer.data)

    # 태그 삭제
    def delete(self, request, userId="", fileId=""):
        received_json_data = json.loads(request.body.decode("utf-8"))
        tagName = received_json_data['tagName']
        try:
            user = User.objects.get(id=userId)
        except User.DoesNotExist:
            return JsonResponse({"message":"Requested user does not exist."})
        try:
            file = File.objects.get(id=fileId)
        except File.DoesNotExist:
            return JsonResponse({"message":"Requested file does not exist."})
        try:
            tag = Tag.objects.get(file=fileId, name=tagName)
        except Tag.DoesNotExist:
            return JsonResponse({"message":"Requested tag does not exist."})
        tagUserId = tag.user.id
        if (int(tagUserId)==int(userId)):
            tag.delete()
            return JsonResponse({"message": "Tag successfully deleted."})
        else:
            return JsonResponse({"message": "Request user is not owner of requested tag."})
