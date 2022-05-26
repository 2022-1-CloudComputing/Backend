from rest_framework import serializers

from file.models import Bookmark, File

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = "__all__"


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