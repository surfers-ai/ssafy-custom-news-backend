from typing import List
from rest_framework import serializers

from myboard.models import Comment, Posting
from myboard.serializers.comment_serializer import CommentSerializer

class PostingCommentSerializer(serializers.Serializer):

    comments = serializers.SerializerMethodField()

    def get_comments(self, obj: Posting) -> List[Comment]:
        comments = Comment.objects.filter(posting_id=obj.id).select_related('writer')
        return CommentSerializer(comments, many=True).data