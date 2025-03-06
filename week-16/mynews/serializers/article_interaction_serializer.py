from rest_framework import serializers

from mynews.enums import ArticleInteractionType
from mynews.models import Article, UserArticleInteraction


class UserArticleInteractionSerializer(serializers.Serializer):
    likes = serializers.SerializerMethodField()
    read = serializers.SerializerMethodField()

    def get_likes(self, obj: Article) -> int:
        return UserArticleInteraction.objects.filter(
            article_id=obj.id, interaction_type=ArticleInteractionType.LIKE
        ).count()

    def get_read(self, obj: Article) -> int:
        return UserArticleInteraction.objects.filter(
            article_id=obj.id, interaction_type=ArticleInteractionType.READ
        ).count()
