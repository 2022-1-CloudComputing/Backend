from rest_framework import serializers

from file.models import Bookmark, File, Folder


class BookmarkSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source="file.id")
    title = serializers.ReadOnlyField(source="file.title")

    class Meta:
        model = Bookmark
        fields = ["id", "title"]


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

