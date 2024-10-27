from rest_framework import serializers
from mynews.models import Article
from mynews.serializers.related_articles_serializer import RelatedArticlesSerializer


class ArticleResponseSerializer(serializers.ModelSerializer):
    related_articles = RelatedArticlesSerializer(source="*")

    class Meta:
        model = Article
        exclude = ["embedding"]
