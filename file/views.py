from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from file.models import Bookmark, File
from user.models import User
from file.serializers import BookmarkSerializer, BookmarkUserSerializer, FileSerializer

from file.storages import CRUD

import json

class BookmarkViewSet(viewsets.ViewSet):
    lookup_field = "userId"

    def list(self, request, userId):
        user = User.objects.get(id=userId)
        queryset = user.bookmarks.all()
        serializer = BookmarkSerializer(queryset, many=True)
        return Response(serializer.data)

class BookmarkDetailView(APIView): # 하나의 북마크 조회
    def delete(self, request, userId="", bookmarkId=""):
        bookmark = Bookmark.objects.get(id = bookmarkId)
        bookmarkUserId = bookmark.user.id;
        print(userId, bookmarkUserId, int(userId)==int(bookmarkUserId))
        if (int(bookmarkUserId)==int(userId)):
            bookmark.delete();
            return JsonResponse({"message": "bookmark successfully deleted."})
        else:
            return JsonResponse({"message": "Request user is not owner of requested bookmark."})

    def get(self, userId = "", bookmarkId=""):
        print(userId, bookmarkId, "me!!")
        bookmark = Bookmark.objects.filter(id = bookmarkId)
        print(bookmark)
        serialzer = BookmarkUserSerializer(bookmark)
        return JsonResponse(serialzer.data)

class BookmarkView(APIView): # 사용자의 북마크 리스트 조회 또는 북마크 추가
    def get(self, request, userId=""): # 완료
        print("its wrong url!!")
        user = User.objects.get(id = userId)
        bookmarks = Bookmark.objects.filter(user = user)
        serializer = BookmarkSerializer(bookmarks, many=True)
        return JsonResponse(serializer.data, safe=False);

    def post(self, request, userId=""): # 완료
        received_json_data = json.loads(request.body.decode("utf-8"))
        fileId = received_json_data['fileId']
        user = User.objects.get(id=userId)
        file = File.objects.get(id=fileId)
        bookmark = Bookmark(user=user, file=file)
        bookmark.save();
        serializer = BookmarkSerializer(bookmark)
        return JsonResponse(serializer.data)
        


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