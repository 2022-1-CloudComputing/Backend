# from rest_framework.generics import GenericAPIView
# from rest_framework.mixins import RetrieveModelMixin
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated

# from api.serializer import UserSerializer

# class UserProfileApiView(RetrieveModelMixin, GenericAPIView):
#     serializer_class = UserSerializer
#     permission_classes = (IsAuthenticated, )

#     def get_object(self):
#         return self.request.user

#     def get(self, request, *args, **kwargs):
#         return self.retrieve(request, *args, **kwargs)

#     def post(self, request, *args, **kwargs):
#         return Response(self.serializer_class.data)

import hashlib
import json

import jwt
from django.contrib.auth import authenticate, login
from dropbox.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
from file.folders3 import delete_folder_file, get_s3_client, upload_folder
from file.serializers import *
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from user.auth import Cognito
from user.models import User
from user.serializers import UserSerializer


class Login(APIView):
    def post(self, request):
        # 파라미터가 전부 입력되었는지 확인
        required_keys = ["id", "pw"]
        if all(it in request.data for it in required_keys):
            if User.objects.filter(username=request.data["id"]).count() == 0:
                return Response({"message": "존재하지 않는 아이디입니다."}, status=400)

            username = request.data["id"]
            password = request.data["pw"]
            print(username, password)

            # hashcode = hashlib.md5(password.encode('utf-8')).hexdigest()
            # user = authenticate(username=username, password=request.data['id'])

            # if user is not None:
            #     login(request, user)
            # hashcode = hashlib.md5(request.data['pw'].encode('utf-8')).hexdigest()
            cog = Cognito()
            result = cog.sign_in_admin(username=username, password=password)

            return Response(result, status=200)
            # else:
            # return Response({'message': '아이디 혹은 비밀번호가 잘못되었습니다.'}, status=401)

        else:
            return Response({"message": "요구되는 파라미터를 전부 입력해주세요."}, status=400)


class Signup(APIView):
    def post(self, request):
        # 파라미터가 전부 입력되었는지 확인
        required_keys = ["id", "pw", "email", "name"]
        # print(request.data)
        if all(it in request.data for it in required_keys):
            if User.objects.filter(username=request.data["id"]).count():
                return Response({"message": "이미 존재하는 아이디입니다."}, status=400)
            if User.objects.filter(email=request.data["email"]).count():
                return Response({"message": "이미 존재하는 이메일입니다."}, status=400)

            """password hash로 하니까 대문자 소문자 적으라해서 에러남.."""
            hashcode = hashlib.md5(request.data["pw"].encode("utf-8")).hexdigest()

            # user = User.objects.create_user(
            #     username=request.data['id'],
            #     email=request.data['email'],
            #     password=hashcode,
            #     name=request.data['name']
            # )

            cog = Cognito()
            cog.sign_up(
                username=request.data["id"],
                password=request.data["pw"],
                UserAttributes=[
                    {"Name": "email", "Value": request.data["email"]},
                    {"Name": "name", "Value": request.data["name"]},
                ],
            )
            cog.confirm_sign_up(username=request.data["id"])

            # DB에 User 정보 저장
            serializers = UserSerializer(
                data={
                    "username": request.data["id"],
                    "email": request.data["email"],
                    "password": hashcode,
                    "name": request.data["name"],
                }
            )
            # print(serializers.is_valid())
            if serializers.is_valid():
                serializers.save()

            print(User.objects.filter(email=request.data["email"]))

            # DB에 User의 Root 폴더 생성
            serializers = FolderSerializer(
                data={
                    "user_id": request.data["id"],
                    "name": request.data["id"],
                    "path": "",
                }
            )  # many=True
            if not serializers.is_valid():
                return Response(serializers.errors, content_type="application/json", status=status.HTTP_400_BAD_REQUEST)
            serializers.save()

            # AWS 관리자 계정으로 S3에 회원가입하는 User의 Root 폴더 생성
            # 관리자 키로 S3 Client 생성
            s3_client = get_s3_client(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)

            # S3 User의 Root 폴더에 해당하는 Key 생성
            upload_folder(s3_client, "/".join([request.data["id"], ""]))

            return Response({"message": "회원가입이 성공하였습니다."}, status=200)

        # 파라미터가 누락된 경우
        else:
            return Response({"message": "요구되는 파라미터를 전부 입력해주세요."}, status=400)


class Logout(APIView):
    def post(self, request):
        if "Authorization" not in request.headers:
            return Response({"message": "Access Token을 전달해주세요."}, status=401)
        access_token = request.headers["Authorization"].replace("Bearer ", "")

        cog = Cognito()

        resp = cog.sign_out(access_token)
        if resp is not None:
            return Response(resp, status=400)

        return Response({"message": "로그아웃에 성공했습니다."}, status=200)


class Dropout(APIView):  # 삭제할 때 user관련 폴더 삭제 안했음 ㅠ
    def delete(self, request):
        if "Authorization" not in request.headers:
            return Response({"message": "Access Token을 전달해주세요."}, status=401)
        access_token = request.headers["Authorization"].replace("Bearer ", "")

        claims = jwt.decode(access_token, verify=False)
        user = User.objects.filter(username=claims["username"])
        if user.count() == 0:
            return Response({"message": "이미 탈퇴 처리된 계정입니다."}, status=400)
        user.delete()

        cog = Cognito()
        resp = cog.delete_user(access_token)

        if resp is not None:
            return Response(resp, status=400)

        return Response({"message": "탈퇴 처리에 성공했습니다."}, status=200)


class Duplicate(APIView):
    def get(self, request, id):
        if id is None:
            return Response({"message": "조회할 ID를 Path Parameter로 보내주세요."}, status=404)

        if User.objects.filter(username=str(id)).count() != 0:
            return Response({"message": "이미 존재하는 ID입니다."}, status=500)

        return Response({"id": id, "is_duplicate": False}, status=200)


class Info(APIView):
    def post(self, request):
        if "Authorization" not in request.headers:
            return Response({"message": "Access Token을 전달해주세요."}, status=401)
        access_token = request.headers["Authorization"].replace("Bearer ", "")

        required_keys = ["old_pw", "new_pw"]
        if all(it in request.data for it in required_keys):

            claims = jwt.decode(access_token, verify=False)
            user = User.objects.filter(username=claims["username"])[0]
            user.set_password(request.data["new_pw"])

            hashed_old_pw = hashlib.md5(request.data["old_pw"].encode("utf-8")).hexdigest()
            hashed_new_pw = hashlib.md5(request.data["new_pw"].encode("utf-8")).hexdigest()

            cog = Cognito()
            resp = cog.change_password(access_token, hashed_old_pw, hashed_new_pw)

            if resp is not None:
                return Response(resp, status=400)

            return Response({"message": "비밀번호 변경에 성공했습니다."}, status=200)

        else:
            return Response({"message": "old_pw와 new_pw를 전달해주세요."}, status=400)


class Findpw(APIView):
    def post(self, request):

        required_keys = ["id"]
        if all(it in request.data for it in required_keys):
            cog = Cognito()
            resp = cog.forgot_password(username=request.data["id"])

            return Response(resp, status=200)

        else:
            return Response({"message": "id를 전달해주세요."}, status=400)


class Resetpw(APIView):
    def post(self, request):

        required_keys = ["id", "pw", "confirmation_code"]
        if all(it in request.data for it in required_keys):
            hashcode = hashlib.md5(request.data["pw"].encode("utf-8")).hexdigest()

            user = User.objects.get(username=request.data["id"])
            user.password = hashcode
            user.save()

            cog = Cognito()
            resp = cog.confirm_forgot_password(
                username=request.data["id"],
                password=request.data["pw"],  # hashcode,
                code=request.data["confirmation_code"],
            )

            if resp is not None:
                return Response(resp, status=400)

            return Response({"message": "비밀번호 변경에 성공했습니다."}, status=200)

        else:
            return Response({"message": "id, pw, confirmation_code를 모두 전달해주세요."}, status=400)
