from rest_framework import serializers

from mynews.enums import ArticleCategory


class NewslistRequestSerializer(serializers.Serializer):
    category = serializers.ChoiceField(
        choices=ArticleCategory.choices, required=False, default=ArticleCategory.전체
    )
    limit = serializers.IntegerField(required=False, default=10)
