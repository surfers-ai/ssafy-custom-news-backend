from rest_framework import serializers
from myboard.models import Posting
from myboard.serializers.posting_comment_serializer import PostingCommentSerializer
from mynews.serializers.related_articles_serializer import RelatedArticlesSerializer


class PostingResponseSerializer(serializers.ModelSerializer):
    posting_comments = PostingCommentSerializer(source="*")
    related_articles = RelatedArticlesSerializer(source="*")
    writer_username = serializers.CharField(source='writer.username')

    class Meta:
        model = Posting
        exclude = ["embedding"]
