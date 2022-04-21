from django.urls import path, include
from file.views import BookmarkViewSet

urlpatterns = [
    path('users/<userId>/bookmarks', BookmarkViewSet.as_view({'get':'list'}))
]
