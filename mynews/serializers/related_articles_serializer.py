from rest_framework import serializers
from mynews.models import Article
from pgvector.django import CosineDistance

from mynews.serializers.article_serializer import ArticleSerializer


class RelatedArticlesSerializer(serializers.Serializer):
    articles = serializers.SerializerMethodField()

    def get_articles(self, obj: Article) -> list[dict]:
        # 코사인 유사도가 높은 상위 5개 기사 추출
        related_articles = Article.objects.order_by(
            CosineDistance("embedding", obj.embedding)
        )[1:6]  # 자기 자신(첫 번째 기사)는 제외
        return [ArticleSerializer(article).data for article in related_articles]
