from rest_framework import serializers


class ArticleRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    question = serializers.CharField()
