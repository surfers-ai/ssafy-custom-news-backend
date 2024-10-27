from django.http import JsonResponse
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, mixins
from mynews.models import Article
from mynews.serializers.article_like_request_serializer import ArticleLikeSerializer
from mynews.serializers.article_response_serializer import ArticleResponseSerializer
from mynews.serializers.newslist_request_serializer import NewslistRequestSerializer
from mynews.serializers.article_serializer import ArticleSerializer
from mynews.serializers.chatbot_request_serializer import ChatbotRequestSerializer
from mynews.serializers.write_article_request_serializer import (
    WriteArticleRequestSerializer,
)

from rest_framework import status

from mynews.mocking import dashboard_mock

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# https://www.django-rest-framework.org/tutorial/3-class-based-views/


class NewsListView(APIView):
    def get(self, request: Request, *args, **kwargs):
        serializer = NewslistRequestSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        category = serializer.validated_data.get("category")
        limit = serializer.validated_data.get("limit")

        queryset = Article.get_article_list(category, limit)

        user_email = request.user.email if request.user.is_authenticated else None

        # 비로그인 상태
        if user_email is None:
            serializer = ArticleSerializer(queryset, many=True)
            return Response(
                {"message": "호출 성공, 비로그인 상태", "data": serializer.data},
                status=200,
            )
        # 로그인 상태
        else:
            return Response(
                {"message": "곧 출시 예정!!! 추천 기사 추가 예정", "data": None},
                status=200,
            )


class ArticleView(APIView):
    def get(self, request: Request, article_id: int) -> JsonResponse:
        try:
            print("article_id", article_id)
            print("!")
            article = Article.objects.get(id=article_id)

            return Response(
                {
                    "message": "호출 성공",
                    "data": ArticleResponseSerializer(article).data,
                },
                status=200,
            )
        except Article.DoesNotExist:
            return Response(
                {"message": "기사를 찾을 수 없습니다."},
                status=404
            )


class WriteArticleView(APIView):
    def post(self, request: Request) -> JsonResponse:
        # 요청 데이터 유효성 검사
        serializer = WriteArticleRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"message": "잘못된 요청 데이터입니다.", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 유효한 데이터로 기사 생성
        try:
            article = Article.post_article(
                title=serializer.validated_data["title"],
                writer=serializer.validated_data["writer"],
                write_date=serializer.validated_data["write_date"],
                category=serializer.validated_data["category"],
                content=serializer.validated_data["content"],
                url=serializer.validated_data["url"],
                keywords=serializer.validated_data["keywords"],
                embedding=serializer.validated_data["embedding"],
            )
            return JsonResponse(
                {
                    "message": "기사가 성공적으로 생성되었습니다.",
                    "data": ArticleSerializer(article).data,
                },
                status=201,
                json_dumps_params={"ensure_ascii": False},
            )

        except Exception as e:
            return Response(
                {"message": f"기사 생성 중 오류가 발생했습니다: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ChatbotView(APIView):
    client = OpenAI()

    def post(self, request: Request) -> JsonResponse:
        serializer = ChatbotRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        article_id = serializer.validated_data["article_id"]
        question = serializer.validated_data["question"]

        print(article_id, question)

        completion = (
            self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "너는 친절한 친구야. 너는 사용자에게 친절하게 답변해야해.",
                    },
                    {"role": "user", "content": question},
                ],
            )
            .choices[0]
            .message.content
        )

        return Response(
            {"message": "호출 성공", "history": completion},
            status=status.HTTP_200_OK,
        )


class DashboardView(APIView):
    def get(self, request: Request) -> JsonResponse:
        return JsonResponse(
            {"message": "호출 성공", "data": dashboard_mock}, status=200
        )


class LikeArticleView(APIView):
    def post(self, request: Request) -> Response:
        serializer = ArticleLikeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        article_id = serializer.validated_data["article_id"]

        # TODO: 좋아요 로직 구현
        print(article_id)

        return Response(
            {
                "message": "기사에 좋아요를 눌렀습니다."
            },
            status=status.HTTP_200_OK,
        )
