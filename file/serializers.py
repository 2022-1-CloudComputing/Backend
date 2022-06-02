from rest_framework import serializers


from file.models import Bookmark, File, Folder, Tag


class BookmarkSerializer(serializers.ModelSerializer):
    file = FileSerializer()
    class Meta:
        model = Bookmark
        fields = "__all__"
        related_object = 'file'

class BookmarkSimpleSerialiser(serializers.ModelSerializer):
    fileId = serializers.ReadOnlyField(source='file.id')
    class Meta:
        model = Bookmark
        fields = ['fileId']

class TagSerializer(serializers.ModelSerializer):
    # user가 업로드한 파일 중 검색 tag 이름과 일치하는 file 리스트 조회
    file = FileSerializer()
    class Meta:
        model = Tag
        fields = "__all__"
        requested_object = 'file'
   
class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ["file_id", "file", "title", "owner", "file_size", "folder_id", "created_at"]


class FolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = ("folder_id", "parent_id", "user_id", "name", "path", "created_at", "modified_at")


class FolderNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = ("name",)


class FolderMoveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = (
            "parent_id",
            "path",
        )
