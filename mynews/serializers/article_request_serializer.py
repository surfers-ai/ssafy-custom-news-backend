from rest_framework import serializers

from mynews.enums import ArticleCategory

class ArticleRequestSerializer(serializers.Serializer):
    category = serializers.ChoiceField(choices=ArticleCategory.choices, required=False)
    limit = serializers.IntegerField(default=10, required=False)
