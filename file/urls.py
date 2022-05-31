from django.urls import include, path

from file.views import BookmarkViewSet, FileUploadView, FolderCreate, FolderDetail, FolderElements, FolderMove


urlpatterns = [
    path("users/<userId>/bookmarks", BookmarkViewSet.as_view({"get": "list"})),
    path("user/<str:userId>", home, name="home"),
    path("user/<str:userId>/file", FileUploadView.as_view(), name="post"),
    path("user/<str:userId>/file/<str:fileId>", FileUploadView.as_view()),
    path("user/<str:userId>/file/<str:fileId>/preview", preview, name="preview"),
    path("folder_create", FolderCreate.as_view()),
    path("folder_detail/<int:folder_id>", FolderDetail.as_view()),
    path("folder_elements/<int:folder_id>/list", FolderElements.as_view()),
    path("folder_move/<int:folder_id>/move",FolderMove.as_view())
]
