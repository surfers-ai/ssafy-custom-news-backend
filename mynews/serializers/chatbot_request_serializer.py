from rest_framework import serializers


class ChatbotRequestSerializer(serializers.Serializer):
    article_id = serializers.IntegerField()
    question = serializers.CharField()
