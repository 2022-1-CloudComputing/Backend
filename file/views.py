from rest_framework import viewsets
from rest_framework.response import Response
from file.models import User, Bookmark
from file.serializers import BookmarkSerializer
from django.shortcuts import get_object_or_404

class BookmarkViewSet(viewsets.ViewSet):
    lookup_field = 'userId'
    
    def list(self, request, userId):
        user = User.objects.get(id = userId)
        queryset = user.bookmarks.all()
        serializer = BookmarkSerializer(queryset, many=True)
        return Response(serializer.data)