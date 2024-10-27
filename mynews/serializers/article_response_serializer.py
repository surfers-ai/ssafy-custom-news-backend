from rest_framework import serializers

from mynews.models import Article
from mynews.serializers.article_interaction_serializer import UserArticleInteractionSerializer

class ArticleResponseSerializer(serializers.ModelSerializer):

    article_interaction = UserArticleInteractionSerializer(source='*')
    
    class Meta:
        model = Article
        exclude = ['embedding']