from django.urls import include, path
from file.views import BookmarkDetailView, BookmarkSimpleView, BookmarkView, FileUploadView


from file.views import (
    BookmarkViewSet,
    FilePreviewView,
    FileUploadView,
    FolderCreate,
    FolderDetail,
    FolderElements,
    FolderMove,
    HomeView,
)

urlpatterns = [
    path("user/<userId>/bookmark/simple", BookmarkSimpleView.as_view()),
    path("user/<userId>/bookmark/<bookmarkId>", BookmarkDetailView.as_view()),
    path("user/<userId>/bookmark", BookmarkView.as_view()),
    path("user/<userId>", HomeView.as_view()),
    path("user/<userId>/file", FileUploadView.as_view(), name="post"),
    path("user/<userId>/file/<fileId>", FileUploadView.as_view()),
    path("user/<userId>/file/<fileId>/preview", FilePreviewView.as_view()),
    path("folder_create", FolderCreate.as_view()),
    path("folder_detail/<int:folder_id>", FolderDetail.as_view()),
    path("folder_elements/<int:folder_id>/list", FolderElements.as_view()),
    path("folder_move/<int:folder_id>/move", FolderMove.as_view()),
]
