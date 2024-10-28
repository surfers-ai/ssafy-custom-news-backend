from rest_framework import serializers

from myboard.enums import PostingCategory


class WritePostingRequestSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    category = serializers.ChoiceField(choices=PostingCategory.choices)
    content = serializers.CharField()
    keywords = serializers.ListField(child=serializers.CharField())
