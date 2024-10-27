from django.http import JsonResponse
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from mynews.enums import ArticleInteractionType
from mynews.models import Article, UserArticleInteraction
from mynews.serializers.dto.article_like_request_serializer import ArticleLikeSerializer
from mynews.serializers.dto.article_response_serializer import ArticleResponseSerializer
from mynews.serializers.dto.newslist_request_serializer import NewslistRequestSerializer
from mynews.serializers.article_serializer import ArticleSerializer
from mynews.serializers.dto.chatbot_request_serializer import ChatbotRequestSerializer
from mynews.serializers.dto.write_article_request_serializer import (
    WriteArticleRequestSerializer,
)

from rest_framework import status
from langchain.prompts import PromptTemplate

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

        # 비로그인 상태
        if not request.user.is_authenticated:
            queryset = Article.get_article_list(category, limit)
            serializer = ArticleSerializer(queryset, many=True)

            return Response(
                {"message": "호출 성공, 비로그인 상태", "data": serializer.data},
                status=200,
            )
        # 로그인 상태
        else:
            queryset = Article.get_recommendation_article_list(request.user.id, category, limit)
            serializer = ArticleSerializer(queryset, many=True)

            return Response(
                {"message": "호출 성공, 로그인 상태", "data": serializer.data},
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
            return Response({"message": "기사를 찾을 수 없습니다."}, status=404)


class WriteArticleView(APIView):
    def post(self, request: Request) -> JsonResponse:
        # 요청 데이터 유효성 검사
        serializer = WriteArticleRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"message": "잘못된 요청 데이터입니다.", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
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

        try:
            article = Article.objects.get(id=article_id)
            title = article.title
            content = article.content
            write_date = article.write_date
        except Article.DoesNotExist:
            return Response(
                {"message": "해당 기사를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 템플릿 정의
        rag_tempalte = """너는 친절한 뉴스 비서 <뉴비>야. 뉴비는 News(뉴스) + 비서의 합성어로, 초심사(newbie)라는 중의적인 의미도 갖고 있어.
- 친근하고 상냥한 비서처럼 행동하면서, 주어진 뉴스 기사를 바탕으로 사용자의 질문에 아주 쉽고 친절하게 답해줘야 해.
- 뉴스 기사에서 찾을 수 없는 정보는 "죄송해요, 여기 보고계신 기사에서는 찾을 수 없네요ㅎㅎ"라고 답해줘.

사용자가 지금 보고 있는 뉴스를 참고해서 답변할 수 있는 질문에는 친절하게 답해줘.

### 기사 제목: {title}

### 작성일: {write_date}

### 기사 내용:
{content}
"""

        # PromptTemplate 생성
        rag_article_prompt = PromptTemplate(
            input_variables=["title", "write_date", "content"],
            template=rag_tempalte,
        )

        # 템플릿에 변수 적용
        context = rag_article_prompt.format(
            title=title, write_date=write_date, content=content
        )

        completion = (
            self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": context},
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
        # 요청 데이터 유효성 검사
        serializer = ArticleLikeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 유효한 데이터에서 article_id 추출
        article_id = serializer.validated_data["article_id"]

        # 해당 ID의 기사 조회
        article = self.get_article(article_id)
        if not article:
            return self.article_not_found_response()

        # 사용자 인증 확인
        if not request.user.is_authenticated:
            return self.unauthorized_response()

        if UserArticleInteraction.is_liked_by_user(request.user, article):
            return self.like_already_exists_response()

        # 사용자-기사 상호작용 생성
        interaction = UserArticleInteraction.create_like(request.user, article)

        if interaction:
            # 새로운 좋아요 추가 시 응답
            return self.like_added_response()
        else:
            return self.like_already_exists_response()

    def delete(self, request: Request) -> Response:
        # 요청 데이터 유효성 검사
        serializer = ArticleLikeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 유효한 데이터에서 article_id 추출
        article_id = serializer.validated_data["article_id"]

        # 해당 ID의 기사 조회
        article = self.get_article(article_id)
        if not article:
            return self.article_not_found_response()

        # 사용자 인증 확인
        if not request.user.is_authenticated:
            return self.unauthorized_response()

        if not UserArticleInteraction.is_liked_by_user(request.user, article):
            return self.like_not_found_response()

        UserArticleInteraction.delete_like(request.user, article)
        return self.like_canceled_response()
    
    def get(self, request: Request) -> Response:
        # 해당 ID의 좋아요를 눌렀는지 확인
        if not request.user.is_authenticated:
            return self.unauthorized_response()

        serializer = ArticleLikeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        article_id = serializer.validated_data["article_id"]

        article = self.get_article(article_id)

        if not article:
            return self.article_not_found_response()

        if UserArticleInteraction.is_liked_by_user(request.user, article):
            return self.like_found_response()
        else:
            return self.like_not_found_response()

    def get_article(self, article_id):
        try:
            return Article.objects.get(id=article_id)
        except Article.DoesNotExist:
            return None

    def article_not_found_response(self):
        return Response(
            {"message": "해당 기사를 찾을 수 없습니다."},
            status=status.HTTP_404_NOT_FOUND,
        )

    def unauthorized_response(self):
        return Response(
            {"message": "로그인이 필요합니다."}, status=status.HTTP_401_UNAUTHORIZED
        )

    def like_canceled_response(self):
        return Response(
            {"message": "기사의 좋아요를 취소했습니다."}, status=status.HTTP_200_OK
        )

    def like_added_response(self):
        return Response(
            {"message": "기사에 좋아요를 눌렀습니다."}, status=status.HTTP_200_OK
        )
    
    def like_found_response(self):
        return Response(
            {"message": "좋아요를 누른 기사입니다."}, status=status.HTTP_200_OK
        )

    def like_not_found_response(self):
        return Response(
            {"message": "좋아요를 누르지 않은 기사입니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def like_already_exists_response(self):
        return Response(
            {"message": "이미 좋아요를 누른 기사입니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )
