from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response

from myboard.models import Comment, Posting
from myboard.serializers.posting_serializer import PostingSerializer
from myboard.serializers.dto.posting_list_request_serializer import PostingListRequestSerializer
from myboard.serializers.dto.posting_response_serializer import PostingResponseSerializer
from myboard.serializers.dto.write_comment_request_serializer import WriteCommentRequestSerializer
from myboard.serializers.dto.write_posting_request_serializer import WritePostingRequestSerializer
from myproject.response import SUCCESS_RESPONSE, UNAUTHORIZED_RESPONSE


class BoardListView(APIView):
    def get(self, request: Request, *args, **kwargs):
        serializer = PostingListRequestSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        category = serializer.validated_data.get("category")
        limit = serializer.validated_data.get("limit")
        
        queryset = Posting.get_posting_list(category, limit)
        serializer = PostingSerializer(queryset, many=True)

        return SUCCESS_RESPONSE("호출 성공, 로그인 상관 X", serializer.data)
        

class PostingView(APIView):
    def get(self, request: Request, posting_id: int):
        # 비로그인 상태
        if not request.user.is_authenticated:
            return UNAUTHORIZED_RESPONSE()
        
        try:
            posting = Posting.objects.get(id=posting_id)
            serializer = PostingResponseSerializer(posting)

            return SUCCESS_RESPONSE("호출 성공", serializer.data)
        except Posting.DoesNotExist:
            return Response({"message": "게시물을 찾을 수 없습니다."}, status=404)

class WritePostingView(APIView):
    def post(self, request: Request) -> Response:
        # 비로그인 상태
        if not request.user.is_authenticated:
            return UNAUTHORIZED_RESPONSE()
        
        serializer = WritePostingRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        posting_id = Posting.post_posting(
            title=serializer.validated_data["title"],
            writer=request.user,
            category=serializer.validated_data["category"],
            content=serializer.validated_data["content"],
            keywords=serializer.validated_data["keywords"],
        )

        return SUCCESS_RESPONSE("게시물이 성공적으로 생성되었습니다.", {"posting_id": posting_id})

class WriteCommentView(APIView):
    def post(self, request: Request, posting_id: int) -> Response:
        # 비로그인 상태
        if not request.user.is_authenticated:
            return UNAUTHORIZED_RESPONSE()
        
        serializer = WriteCommentRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        Comment.post_comment(posting_id, request.user, serializer.validated_data["content"])

        return SUCCESS_RESPONSE("댓글이 성공적으로 생성되었습니다.")
