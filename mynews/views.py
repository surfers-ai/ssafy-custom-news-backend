from django.http import JsonResponse
from rest_framework.request import Request
from rest_framework.views import APIView

from mynews.enums import ArticleCategory
from mynews.models import Article
from mynews.serializers.article_request_serializer import ArticleRequestSerializer
from mynews.serializers.article_response_serializer import ArticleResponseSerializer

# https://www.django-rest-framework.org/tutorial/3-class-based-views/

class NewsView(APIView):
    def get(self, request: Request) -> JsonResponse:
        serializer = ArticleRequestSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        category = serializer.validated_data.get('category', ArticleCategory.ALL)
        limit = serializer.validated_data.get('limit', 10)

        articles = Article.get_article_list(category, limit)

        return JsonResponse(
            {
                "message": "호출 성공",
                "data": ArticleResponseSerializer(articles, many=True).data
            },
            status=200,
            json_dumps_params={'ensure_ascii': False}
        )