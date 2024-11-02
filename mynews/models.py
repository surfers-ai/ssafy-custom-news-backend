import datetime
import random
from typing import List
from django.db import models
from pgvector.django import VectorField

from mynews.enums import ArticleCategory, ArticleInteractionType
from pgvector.django import CosineDistance
from django.contrib.auth.models import User
from django.db.models import Avg


class Article(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    writer = models.CharField(max_length=255)
    write_date = models.DateTimeField()
    category = models.CharField(choices=ArticleCategory.choices)
    content = models.TextField(unique=True)
    url = models.URLField(max_length=200, unique=True)
    keywords = models.JSONField(default=list)
    embedding = VectorField(dimensions=1536)

    class Meta:
        indexes = [models.Index(fields=["id"], name="unique_article_id")]

    @classmethod
    def get_article_list(
        cls, category: ArticleCategory, page: int = 1, limit: int = 10, sort_by: str = "latest"
    ) -> tuple[List["Article"], int]:
        offset = (page - 1) * limit
        
        if category == ArticleCategory.전체:
            queryset = cls.objects
        else:
            queryset = cls.objects.filter(category=category)
        
        total_count = queryset.count()
        
        if sort_by == "latest":
            articles = queryset.order_by('-write_date')[offset:offset + limit]
        else:
            articles = queryset.order_by('?')[offset:offset + limit]
        
        return articles, total_count
    
    @classmethod
    def get_recommendation_article_list(cls, user_id: int, category: ArticleCategory, page: int = 1, limit: int = 10) -> tuple[List["Article"], int]:
        offset = (page - 1) * limit
        
        user_interactions = UserArticleInteraction.objects.filter(user_id=user_id)
        
        if not user_interactions.exists():
            return cls.get_article_list(category, page, limit)
        
        avg_embedding = user_interactions.filter(interaction_type=ArticleInteractionType.LIKE).aggregate(Avg('article__embedding'))['article__embedding__avg']

        liked_article_ids = UserArticleInteraction.objects.filter(user_id=user_id, interaction_type=ArticleInteractionType.LIKE).values_list('article_id', flat=True)
        
        if category == ArticleCategory.전체:
            queryset = cls.objects.exclude(id__in=liked_article_ids)
        else:
            queryset = cls.objects.filter(category=category).exclude(id__in=liked_article_ids)
        
        total_count = queryset.count()
        
        recommended_articles = queryset.order_by(
            CosineDistance('embedding', avg_embedding)
        )[offset:offset + limit]

        # 추천 기사 목록을 랜덤하게 섞기
        recommended_articles = list(recommended_articles)
        random.shuffle(recommended_articles)
        
        return recommended_articles, total_count
    
    @classmethod
    def get_my_favorite_category(cls, user_id: int) -> dict:
        # 사용자가 좋아요를 누른 기사들의 카테고리별 개수를 집계
        category_counts = (
            cls.objects.filter(
                userarticleinteraction__user_id=user_id,
                userarticleinteraction__interaction_type=ArticleInteractionType.LIKE
            )
            .values('category')
            .annotate(count=models.Count('category'))
            .order_by('-count')
        )

        # 딕셔너리 형태로 변환
        result = {}
        for item in category_counts:
            category_name = ArticleCategory(item['category']).name
            result[category_name] = item['count']

        return result
    
    @classmethod
    def get_my_favorite_key_word(cls, user_id: int) -> dict:
        # 사용자가 좋아요를 누른 기사들의 키워드를 모두 가져옴
        liked_articles = cls.objects.filter(
            userarticleinteraction__user_id=user_id,
            userarticleinteraction__interaction_type=ArticleInteractionType.LIKE
        )

        # 모든 키워드를 하나의 리스트로 합침
        all_keywords = []
        for article in liked_articles:
            all_keywords.extend(article.keywords)

        # 키워드별 등장 횟수를 계산
        keyword_counts = {}
        for keyword in all_keywords:
            if keyword in keyword_counts:
                keyword_counts[keyword] += 1
            else:
                keyword_counts[keyword] = 1

        # 등장 횟수가 많은 순으로 정렬하여 상위 5개 추출
        sorted_keywords = dict(sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:5])

        return sorted_keywords
    
    @classmethod
    def get_number_of_written_articles(cls, user_id: int) -> dict:
        # 현재 날짜와 7일 전 날짜를 계산
        end_date = datetime.datetime.now().date()
        start_date = end_date - datetime.timedelta(days=6)
        
        # 날짜별 기사 읽은 수를 집계 (중복 제거)
        daily_counts = (
            cls.objects.filter(
                userarticleinteraction__user_id=user_id,
                userarticleinteraction__interaction_type=ArticleInteractionType.READ,
                userarticleinteraction__interaction_date__date__range=(start_date, end_date)
            )
            .annotate(date=models.functions.TruncDate('userarticleinteraction__interaction_date'))
            .values('date', 'id')  # article id도 함께 가져옴
            .distinct()  # 같은 날짜, 같은 기사 중복 제거
            .values('date')  # 날짜별로 그룹화
            .annotate(count=models.Count('id', distinct=True))  # 중복 없이 카운트
            .order_by('date')
        )
        
        # 결과를 딕셔너리로 변환
        result = {}
        current_date = start_date
        
        # 모든 날짜에 대해 0으로 초기화
        while current_date <= end_date:
            result[current_date.strftime('%Y-%m-%d')] = 0
            current_date += datetime.timedelta(days=1)
            
        # 실제 데이터로 업데이트
        for item in daily_counts:
            date_str = item['date'].strftime('%Y-%m-%d')
            result[date_str] = item['count']
            
        return result
    
    @classmethod
    def get_favorite_articles(cls, user_id: int) -> List[dict]:
        # 사용자가 좋아요를 누른 기사들을 interaction_date 순으로 최대 10개 조회
        liked_articles = cls.objects.filter(
            userarticleinteraction__user_id=user_id,
            userarticleinteraction__interaction_type=ArticleInteractionType.LIKE
        ).order_by('-userarticleinteraction__interaction_date')[:10]

        # id, title, writer, write_date 만 조회
        return list(liked_articles.values('id', 'title', 'writer', 'write_date'))


    @classmethod
    def post_article(
        cls,
        title: str,
        writer: str,
        write_date: datetime.datetime,
        category: ArticleCategory,
        content: str,
        url: str,
        keywords: list[str],
        embedding: list[float],
    ) -> "Article":
        """
        새로운 기사를 생성하고 데이터베이스에 저장합니다.

        매개변수:
        - title: 기사 제목
        - writer: 작성자
        - write_date: 작성 날짜
        - category: 기사 카테고리
        - content: 기사 내용
        - url: 기사 URL
        - keywords: 키워드 리스트
        - embedding: 기사 임베딩 벡터

        반환값:
        - 생성된 Article 객체
        """

        article = cls.objects.create(
            title=title,
            writer=writer,
            write_date=write_date,
            category=category,
            content=content,
            url=url,
            keywords=keywords,
            embedding=embedding,
        )
        return article


class Preference(models.Model):
    """
    User의 확장 모델 - 뉴스 추천을 위한 추가 정보 저장
    기본 사용자 정보(이메일, 이름 등)는 auth_user 테이블 사용
    """

    user = models.OneToOneField("auth.User", on_delete=models.CASCADE)
    user_embedding = VectorField(dimensions=1536)


class UserArticleInteraction(models.Model):
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    interaction_type = models.CharField(choices=ArticleInteractionType.choices)
    interaction_date = models.DateTimeField()

    @classmethod
    def create_like(cls, user, article) -> "UserArticleInteraction":
        """
        사용자가 기사에 좋아요를 누를 때 새로운 상호작용을 생성합니다.

        매개변수:
        - user: 좋아요를 누른 사��자 객체
        - article: 좋아요를 받은 기사 객체

        반환값:
        - 생성된 UserArticleInteraction 객체
        """
        interaction = cls.objects.create(
            user=user,
            article=article,
            interaction_type=ArticleInteractionType.LIKE,
            interaction_date=datetime.datetime.now(),
        )

        return interaction
    
    @classmethod
    def create_read(cls, user, article) -> "UserArticleInteraction":
        """
        사용자가 기사를 읽을 때 새로운 상호작용을 생성합니다.
        """
        interaction = cls.objects.create(
            user=user,
            article=article,
            interaction_type=ArticleInteractionType.READ,
            interaction_date=datetime.datetime.now(),
        )
        return interaction
    
    @classmethod
    def delete_like(cls, user, article) -> None:
        cls.objects.filter(
            user=user, article=article, interaction_type=ArticleInteractionType.LIKE
        ).delete()

    @classmethod
    def is_liked_by_user(cls, user, article) -> bool:
        """
        사용자가 특정 기사에 좋아요를 눌렀는지 확인합니다.

        매개변수:
        - user: 확인할 사용자 객체
        - article: 확인할 기사 객체

        반환값:
        - bool: 사용자가 해당 기사에 좋아요를 눌렀으면 True, 아니면 False
        """
        return cls.objects.filter(
            user=user, article=article, interaction_type=ArticleInteractionType.LIKE
        ).exists()
