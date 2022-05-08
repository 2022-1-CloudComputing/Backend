from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from file.models import Bookmark, File, User
from file.serializers import BookmarkSerializer, FileSerializer
from file.storages import CRUD


class BookmarkViewSet(viewsets.ViewSet):
    lookup_field = "userId"

    def list(self, request, userId):
        user = User.objects.get(id=userId)
        queryset = user.bookmarks.all()
        serializer = BookmarkSerializer(queryset, many=True)
        return Response(serializer.data)


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
