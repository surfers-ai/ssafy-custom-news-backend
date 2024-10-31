from rest_framework import serializers

from myboard.enums import PostingCategory


class PostingListRequestSerializer(serializers.Serializer):
    category = serializers.ChoiceField(
        choices=PostingCategory.choices, required=False, default=PostingCategory.전체
    )
    limit = serializers.IntegerField(required=False, default=10)
    page = serializers.IntegerField(required=False, default=1)