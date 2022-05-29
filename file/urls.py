
from django.urls import include, path

from file.views import BookmarkViewSet, FileUploadView, FolderCreate


urlpatterns = [
    path("users/<userId>/bookmarks", BookmarkViewSet.as_view({"get": "list"})),
    path("user/<userId>/file", FileUploadView.as_view()),
    path("user/<userId>/file/<fileId>", FileUploadView.as_view()),
    path("folder_create", FolderCreate.as_view()),
]
