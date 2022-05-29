from django.urls import include, path

from file.views import BookmarkViewSet, FileUploadView, TagSearchView, TagView, home, preview

urlpatterns = [
    path("users/<userId>/bookmarks", BookmarkViewSet.as_view({"get": "list"})),
    path("user/<str:userId>", home, name="home"),
    path("user/<str:userId>/file", FileUploadView.as_view(), name="post"),
    path("user/<str:userId>/file/<str:fileId>", FileUploadView.as_view()),
    path("user/<str:userId>/file/<str:fileId>/preview", preview, name="preview"),
    path("user/<userId>/search/tag/<tagName>", TagSearchView.as_view()),
    path("user/<userId>/file/tag/upload", TagView.as_view()),
    path("user/<userId>/file/<fileId>/tag/delete", TagView.as_view())
]
