from rest_framework import serializers

from myboard.models import Posting
from myboard.serializers.posting_comment_serializer import PostingCommentSerializer


class PostingSerializer(serializers.ModelSerializer):

    writer = serializers.CharField(source="writer.username", read_only=True)
    posting_comments = PostingCommentSerializer(source="*")

    class Meta:
        model = Posting
        exclude = ["embedding"]
