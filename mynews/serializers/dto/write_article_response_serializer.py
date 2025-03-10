from rest_framework import serializers

from mynews.models import Article


class WriteArticleResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ["id"]
