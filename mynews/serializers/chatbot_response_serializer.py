from rest_framework import serializers


class ChatbotResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    response = serializers.CharField()
