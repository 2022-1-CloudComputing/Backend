from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from rest_framework import viewsets
from rest_framework.response import Response

from file.models import Bookmark, File, User
from file.serializers import BookmarkSerializer
from file.storages import CRUD


class BookmarkViewSet(viewsets.ViewSet):
    lookup_field = "userId"

    def list(self, request, userId):
        user = User.objects.get(id=userId)
        queryset = user.bookmarks.all()
        serializer = BookmarkSerializer(queryset, many=True)
        return Response(serializer.data)


class FileUploadView(View):
    s3_client = CRUD()

    def upload_file(self, request):
        if request.method == "POST" and len(request.FILES) != 0:
            file = request.FILES
            user_id = request.headers["user_id"]

            res = self.s3_client.upload(user_id, file)
            if res:
                return JsonResponse({"message": "success upload"})
            else:
                return JsonResponse({"message": "fail upload"})
        else:
            return JsonResponse({"message": "invalid requests"})

    def delete_file(self, request):
        if request.method == "DELETE":
            file = request.FILES
            user_id = request.headers["user_id"]

            res = self.s3_client.delete(user_id, file)
            if res:
                return JsonResponse({"message": "success delete"})
            else:
                return JsonResponse({"message": "fail delete"})
        else:
            return JsonResponse({"message": "invalid requests"})

    def read_file(self, request):
        if request.method == "GET":
            file = request.FILES
            user_id = request.headers["user_id"]

            res = self.s3_client.read(user_id, file)
            if res:
                return JsonResponse({"message": "success read"})
            else:
                return JsonResponse({"message": "fail read"})
        else:
            return JsonResponse({"message": "invalid requests"})

    def download_file(self, request):
        if request.method == "GET":
            file = request.FILES
            user_id = request.headers["user_id"]

            res = self.s3_client.read(user_id, file)
            if res:
                return JsonResponse({"message": "success download"})
            else:
                return JsonResponse({"message": "fail download"})
        else:
            return JsonResponse({"message": "invalid requests"})

    def update_file(self, request, content):
        if request.method == "PUT":
            file = request.FILES
            user_id = request.headers["user_id"]

            res = self.s3_client.update(user_id, file, content)
            if res:
                return JsonResponse({"message": "success update"})
            else:
                return JsonResponse({"message": "fail update"})
        else:
            return JsonResponse({"message": "invalid requests"})
