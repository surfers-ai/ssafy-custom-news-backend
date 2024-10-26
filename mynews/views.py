from django.http import JsonResponse
from rest_framework.request import Request
from rest_framework.views import APIView
from mynews.models import Article
from mynews.serializers.article_request_serializer import ArticleRequestSerializer
from mynews.serializers.article_response_serializer import ArticleResponseSerializer
from mynews.serializers.chatbot_request_serializer import ChatbotRequestSerializer
from mynews.serializers.write_article_request_serializer import WriteArticleRequestSerializer

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

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
                json_dumps_params={'ensure_ascii': False},
                safe=False
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

class ArticleView(APIView):
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

class WriteArticleView(APIView):
    def post(self, request: Request) -> JsonResponse:
        # 요청 데이터 유효성 검사
        serializer = WriteArticleRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return JsonResponse(
                {"message": "잘못된 요청 데이터입니다.", "errors": serializer.errors},
                status=400,
                json_dumps_params={'ensure_ascii': False}
            )

        # 유효한 데이터로 기사 생성
        try:
            article = Article.post_article(
                title=serializer.validated_data['title'],
                writer=serializer.validated_data['writer'],
                write_date=serializer.validated_data['write_date'],
                category=serializer.validated_data['category'],
                content=serializer.validated_data['content'],
                url=serializer.validated_data['url'],
                keywords=serializer.validated_data['keywords'],
                embedding=serializer.validated_data['embedding']
            )
            return JsonResponse(
                {
                    "message": "기사가 성공적으로 생성되었습니다.",
                    "data": ArticleResponseSerializer(article).data
                },
                status=201,
                json_dumps_params={'ensure_ascii': False}
            )
        except Exception as e:
            return JsonResponse(
                {"message": f"기사 생성 중 오류가 발생했습니다: {str(e)}"},
                status=500,
                json_dumps_params={'ensure_ascii': False}
            )

class ChatbotView(APIView):
    client = OpenAI()

    def post(self, request: Request) -> JsonResponse:
        serializer = ChatbotRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        article_id = serializer.validated_data['article_id']
        question = serializer.validated_data['question']

        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "너는 친절한 친구야. 너는 사용자에게 친절하게 답변해야해."},
                {"role": "user", "content": question}
            ],
        ).choices[0].message.content

        return JsonResponse(
            {
                "message": "호출 성공",
                "history": completion
            },
            status=200,
            json_dumps_params={'ensure_ascii': False}
        )