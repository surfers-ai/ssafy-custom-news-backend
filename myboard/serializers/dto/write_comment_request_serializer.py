from rest_framework import serializers


class WriteCommentRequestSerializer(serializers.Serializer):
    content = serializers.CharField(max_length=1000)