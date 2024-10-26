from rest_framework import serializers

from mynews.enums import ArticleCategory

class ArticleResponseSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    writer = serializers.CharField()
    write_date = serializers.DateTimeField()
    category = serializers.ChoiceField(choices=ArticleCategory.choices)
    content = serializers.CharField()
    key_word = serializers.ListField(child=serializers.CharField())
    url = serializers.URLField()