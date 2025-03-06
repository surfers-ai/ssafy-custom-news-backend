from rest_framework import serializers


class NewsSearchRequestSerializer(serializers.Serializer):
    q = serializers.CharField(required=False, default="")
