from rest_framework import serializers

from mynews.enums import ArticleCategory


class WriteArticleRequestSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    writer = serializers.CharField(max_length=255)
    write_date = serializers.DateTimeField()
    category = serializers.ChoiceField(choices=ArticleCategory.choices)
    content = serializers.CharField()
    url = serializers.URLField(max_length=200)
    keywords = serializers.ListField(child=serializers.CharField())
    embedding = serializers.ListField(child=serializers.FloatField())
