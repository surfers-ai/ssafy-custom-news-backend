from rest_framework import serializers

from myboard.models import Posting
from myboard.serializers.posting_comment_serializer import PostingCommentSerializer


class PostingSerializer(serializers.ModelSerializer):

    posting_comments = PostingCommentSerializer(source="*")

    class Meta:
        model = Posting
        exclude = ["embedding"]
