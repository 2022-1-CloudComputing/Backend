from rest_framework import serializers

from file.models import Bookmark, File


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
