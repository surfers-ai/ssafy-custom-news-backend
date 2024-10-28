from rest_framework import serializers


class PostingRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    question = serializers.CharField()
