from rest_framework import serializers

from myboard.models import Comment

class CommentSerializer(serializers.ModelSerializer):
    writer_name = serializers.CharField(source='writer.username', read_only=True)
    class Meta:
        model = Comment
        fields = ["id", "writer_name", "write_date", "content"]
