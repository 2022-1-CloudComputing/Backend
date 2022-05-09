from rest_framework import serializers
#from file.models import Bookmark
"""
class BookmarkSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='file.id')
    title = serializers.ReadOnlyField(source='file.title')
    
    class Meta:
        model = Bookmark
        fields = ['id', 'title']
"""