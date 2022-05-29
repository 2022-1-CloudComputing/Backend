from rest_framework import serializers

from file.models import Bookmark, File, Tag


class BookmarkSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="file.id")
    title = serializers.ReadOnlyField(source="file.title")

    class Meta:
        model = Bookmark
        fields = ["id", "title"]


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = "__all__"

class TagSerializer(serializers.ModelSerializer):
    # user가 업로드한 파일 중 검색 tag 이름과 일치하는 file 리스트 조회
    file = FileSerializer()
    class Meta:
        model = Tag
        fields = "__all__"
        requested_object = 'file'

