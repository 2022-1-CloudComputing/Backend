from multiprocessing import context
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from requests import request
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from file.folders3 import *

from file.models import Bookmark, File, Folder
from user.models import User
from file.serializers import *
from file.storages import CRUD
from user.auth import is_token_valid



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




# s3 폴더 생성
class FolderCreate(APIView):

    def post(self, request):
        # permission 확인
        if not is_token_valid(token=request.headers['IdToken'], user_id=request.data['id']):
            return Response(status=status.HTTP_403_FORBIDDEN)

        # 폴더 DB에 생성
        serializers = FolderSerializer(data=request.data)

        if not serializers.is_valid():
            return Response(serializers.errors, content_type="application/json", status=status.HTTP_400_BAD_REQUEST)
        serializers.save()

        # S3 Client 생성

        print(request.headers)

        s3_client = get_s3_client(
            request.headers['AccessKeyId'],
            request.headers['SecretKey'],
            request.headers['SessionToken'],
        )
        

        upload_folder(s3_client, '{0}/{1}{2}'.format(
            request.data['id'], request.data['path'],request.data['name']
        ))

        return Response(serializers.data, content_type="application/json", status=status.HTTP_201_CREATED)
        



