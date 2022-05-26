
from django.urls import include, path

from file.views import BookmarkDetailView, BookmarkSimpleView, BookmarkView, FileUploadView


urlpatterns = [
    path("user/<userId>/bookmark/simple", BookmarkSimpleView.as_view()),
    path("user/<userId>/bookmark/<bookmarkId>", BookmarkDetailView.as_view()),
    path("user/<userId>/bookmark", BookmarkView.as_view()),
    path("user/<userId>/file", FileUploadView.as_view()),
    path("user/<userId>/file/<fileId>", FileUploadView.as_view()),
]
