from django.http import JsonResponse
from rest_framework.request import Request
from rest_framework.views import APIView

from mynews.enums import ArticleCategory
from mynews.models import Article
from mynews.responses import user_not_logged_in_response
from mynews.serializers.article_request_serializer import ArticleRequestSerializer
from mynews.serializers.article_response_serializer import ArticleResponseSerializer

# https://www.django-rest-framework.org/tutorial/3-class-based-views/

class NewsListView(APIView):
    def get(self, request: Request) -> JsonResponse:
        # access_token에서 유저 이메일 추출
        user_email = request.user.email if request.user.is_authenticated else None

        # 요청 파라미터 검증
        serializer = ArticleRequestSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        # 요청 파라미터 추출
        category = serializer.validated_data.get('category')
        limit = serializer.validated_data.get('limit')

        # 기사 목록 조회
        articles = Article.get_article_list(category, limit)

        # 로그인을 안했을 경우 (랜덤으로 기사를 띄워줌)
        if user_email is None:
            return JsonResponse(
                status=200,
                data={
                    "message": "호출 성공, 비로그인 상태",
                    "data": ArticleResponseSerializer(articles, many=True).data,
                },
                json_dumps_params={'ensure_ascii': False}
            )

        # 로그인을 했을 경우 (유저 선호도에 따라 맞춤형으로 기사를 추천해줌)
        else:
            return JsonResponse(
                status=200,
                data={
                    "message": "Coming Soon!!! 추천 기사 추가 예정",
                    "data": None,
                },
                json_dumps_params={'ensure_ascii': False}
            )

        return 

class ArticleDetailView(APIView):
    def get(self, request: Request, article_id: int) -> JsonResponse:
        try:
            article = Article.objects.get(id=article_id)
            return JsonResponse(
                {
                    "message": "호출 성공",
                    "data": ArticleResponseSerializer(article).data
                },
                status=200,
                json_dumps_params={'ensure_ascii': False}
            )
        except Article.DoesNotExist:
            return JsonResponse(
                {"message": "기사를 찾을 수 없습니다."},
                status=404,
                json_dumps_params={'ensure_ascii': False}
            )