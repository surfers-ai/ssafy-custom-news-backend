from rest_framework import serializers

from mynews.serializers.article_serializer import ArticleSerializer

class DashboardResponseSerializer(serializers.Serializer):
    my_favorite_category = serializers.DictField()
    my_favorite_key_word = serializers.DictField()
    number_of_written_articles = serializers.DictField()
    favorite_articles = serializers.ListField(child=serializers.DictField())
