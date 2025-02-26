from django.http import JsonResponse
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from langchain.prompts import PromptTemplate
from openai import OpenAI
from dotenv import load_dotenv

from elasticsearch import Elasticsearch

from mynews.models import Article, UserArticleInteraction
from mynews.serializers.dto.article_like_request_serializer import ArticleLikeSerializer
from mynews.serializers.dto.article_response_serializer import ArticleResponseSerializer
from mynews.serializers.dto.newslist_request_serializer import NewslistRequestSerializer
from mynews.serializers.dto.news_search_request_serializer import NewsSearchRequestSerializer
from mynews.serializers.dto.news_search_response_serializer import NewsSearchResponseSerializer
from mynews.serializers.article_serializer import ArticleSerializer
from mynews.serializers.dto.chatbot_request_serializer import ChatbotRequestSerializer
from mynews.serializers.dto.write_article_request_serializer import (
    WriteArticleRequestSerializer,
)
from mynews.serializers.dto.dashboard_response_serializer import DashboardResponseSerializer
from myproject.response import SUCCESS_RESPONSE, UNAUTHORIZED_RESPONSE

load_dotenv()

# https://www.django-rest-framework.org/tutorial/3-class-based-views/


class NewsListView(APIView):
    def get(self, request: Request, *args, **kwargs):
        serializer = NewslistRequestSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        category = serializer.validated_data.get("category")
        limit = serializer.validated_data.get("limit")
        page = serializer.validated_data.get("page")
        sort_by = serializer.validated_data.get("sort_by", "latest")

        if not request.user.is_authenticated:
            articles, total_count = Article.get_article_list(category, page, limit, sort_by)
            serializer = ArticleSerializer(articles, many=True)
            
            return SUCCESS_RESPONSE("호출 성공, 비로그인 상태", {
                "articles": serializer.data,
                "pagination": {
                    "total_count": total_count,
                    "total_pages": (total_count + limit - 1) // limit,
                    "current_page": page,
                    "limit": limit
                }
            })
        else:
            if sort_by == "recommend":
                articles, total_count = Article.get_recommendation_article_list(request.user.id, category, page, limit)
            else:
                articles, total_count = Article.get_article_list(category, page, limit, sort_by)
                
            serializer = ArticleSerializer(articles, many=True)
            
            return SUCCESS_RESPONSE("호출 성공, 로그인 상태", {
                "articles": serializer.data,
                "pagination": {
                    "total_count": total_count,
                    "total_pages": (total_count + limit - 1) // limit,
                    "current_page": page,
                    "limit": limit
                }
            })


class ArticleView(APIView):
    def get(self, request: Request, article_id: int) -> JsonResponse:
        # 비로그인 상태
        if not request.user.is_authenticated:
            return UNAUTHORIZED_RESPONSE()
        
        try:
            article = Article.objects.get(id=article_id)
            UserArticleInteraction.create_read(request.user, article)

            return SUCCESS_RESPONSE("호출 성공", ArticleResponseSerializer(article).data)
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
            return SUCCESS_RESPONSE("기사가 성공적으로 생성되었습니다.", ArticleSerializer(article).data)

        except Exception as e:
            return Response(
                {"message": f"기사 생성 중 오류가 발생했습니다: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ChatbotView(APIView):
    client = OpenAI()

    def post(self, request: Request) -> JsonResponse:
        # 비로그인 상태
        if not request.user.is_authenticated:
            return UNAUTHORIZED_RESPONSE()
        
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
        rag_tempalte = """너는 친절한 뉴스 비서 <뉴비>야. 뉴비는 News(뉴스) + 비서의 합성어로, 초보(newbie)라는 중의적인 의미도 갖고 있어.
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

        return SUCCESS_RESPONSE("호출 성공", {"response": completion})


class DashboardView(APIView):
    def get(self, request: Request) -> JsonResponse:
        # 비로그인 상태
        if not request.user.is_authenticated:
            return UNAUTHORIZED_RESPONSE()
        
        my_favorite_category = Article.get_my_favorite_category(request.user.id)
        my_favorite_key_word = Article.get_my_favorite_key_word(request.user.id)
        number_of_written_articles = Article.get_number_of_written_articles(request.user.id)
        favorite_articles = Article.get_favorite_articles(request.user.id)

        print("favorite_articles", favorite_articles)
        
        serializer = DashboardResponseSerializer(data={
            "my_favorite_category": my_favorite_category,
            "my_favorite_key_word": my_favorite_key_word,
            "number_of_written_articles": number_of_written_articles,
            "favorite_articles": favorite_articles,
        })

        serializer.is_valid(raise_exception=True)

        return SUCCESS_RESPONSE("유저의 취향을 시각화한 대시보드입니다.", serializer.data)

class LikeArticleView(APIView):
    def post(self, request: Request) -> Response:
        # 비로그인 상태
        if not request.user.is_authenticated:
            return UNAUTHORIZED_RESPONSE()
        
        # 요청 데이터 유효성 검사
        serializer = ArticleLikeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 유효한 데이터에서 article_id 추출
        article_id = serializer.validated_data["article_id"]

        # 해당 ID의 기사 조회
        article = self.get_article(article_id)
        if not article:
            return self.article_not_found_response()

        if UserArticleInteraction.is_liked_by_user(request.user, article):
            return self.like_already_exists_response()

        # 사용자-기사 상호작용 생성
        interaction = UserArticleInteraction.create_like(request.user, article)

        if interaction:  # 새로운 좋아요 추가 시 응답
            # 사용자 선호도 업데이트
            return self.like_added_response()
        else:
            return self.like_already_exists_response()

    def delete(self, request: Request) -> Response:
        # 비로그인 상태
        if not request.user.is_authenticated:
            return UNAUTHORIZED_RESPONSE()
        
        # 요청 데이터 유효성 검사
        serializer = ArticleLikeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 유효한 데이터에서 article_id 추출
        article_id = serializer.validated_data["article_id"]

        # 해당 ID의 기사 조회
        article = self.get_article(article_id)
        if not article:
            return self.article_not_found_response()


        if not UserArticleInteraction.is_liked_by_user(request.user, article):
            return self.like_not_found_response()

        UserArticleInteraction.delete_like(request.user, article)
        return self.like_canceled_response()
    
    def get(self, request: Request) -> Response:
        # 비로그인 상태
        if not request.user.is_authenticated:
            return UNAUTHORIZED_RESPONSE()

        # 쿼리 파라미터에서 article_id 추출
        article_id = request.query_params.get('article_id')
        if not article_id:
            return Response(
                {"message": "article_id는 필수 파라���터입니다."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            article_id = int(article_id)
        except ValueError:
            return Response(
                {"message": "article_id는 숫자여야 합니다."},
                status=status.HTTP_400_BAD_REQUEST
            )

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
            {"message": "좋아요를 누른 기사입니다.", "is_liked": True}, status=status.HTTP_200_OK
        )

    def like_not_found_response(self):
        return Response(
            {"message": "좋아요를 누르지 않은 기사입니다.", "is_liked": False},
            status=status.HTTP_200_OK,
        )

    def like_already_exists_response(self):
        return Response(
            {"message": "이미 좋아요를 누른 기사입니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )

class SearchNewsView(APIView):
    def get(self, request: Request) -> JsonResponse:
        
        requestSerializer = NewsSearchRequestSerializer(data=request.query_params)
        requestSerializer.is_valid(raise_exception=True)

        q = requestSerializer.validated_data.get("q")

        es = Elasticsearch("http://localhost:9200")
        search_result = es.search(index="news", query={
            "wildcard": {
                "title": f"*{q}*"
            }
        })

        # Elastic 검색 결과 중 데이터 부분만 추출해 배열로 변환
        articles = [hit['_source'] for hit in search_result['hits']['hits']]
        print(articles)
        responseSerializer = NewsSearchResponseSerializer(articles , many=True)


        return SUCCESS_RESPONSE(f"{q} 에 대한 검색 결과입니다", responseSerializer.data)