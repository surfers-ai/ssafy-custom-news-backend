from rest_framework import serializers


class ArticleLikeSerializer(serializers.Serializer):
    article_id = serializers.IntegerField()
