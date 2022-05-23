from django.urls import include, path

from file.views import BookmarkViewSet, FileUploadView

from . import views

urlpatterns = [
    path("users/<userId>/bookmarks", BookmarkViewSet.as_view({"get": "list"})),
    path("user/<str:userId>", views.home, name="home"),
    path("user/<str:userId>/file", FileUploadView.as_view(), name="post"),
    path("user/<str:userId>/file/<str:fileId>", FileUploadView.as_view()),
    # path("user/<str:userId>/file/<str:fileId>/preview", FileUploadView.preview, name="preview"),
]
