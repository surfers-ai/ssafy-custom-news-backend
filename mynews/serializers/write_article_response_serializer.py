from rest_framework import serializers

from mynews.enums import ArticleCategory

class WriteArticleResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()