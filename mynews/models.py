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
    content = models.TextField()
    url = models.URLField(max_length=200)
    keywords = models.JSONField(default=list)
    embedding = VectorField(dimensions=1536)

    class Meta:
        indexes = [models.Index(fields=["id"], name="unique_article_id")]

    @classmethod
    def get_article_list(
        cls, category: ArticleCategory, limit: int = 10
    ) -> List["Article"]:
        print("category: ", category)
        if category == ArticleCategory.전체:
            return cls.objects.order_by('?')[:limit]
        else:
            return cls.objects.filter(category=category).order_by('?')[:limit]
        
    @classmethod
    def get_recommendation_article_list(cls, user_id: int, category: ArticleCategory, limit: int = 10) -> list["Article"]:
        # 사용자의 평균 임베딩 계산
        user_interactions = UserArticleInteraction.objects.filter(user_id=user_id)

        if not user_interactions.exists():
            return cls.get_article_list(category, limit)  # 상호작용이 없으면 카테고리별 기사 반환

        avg_embedding = user_interactions.filter(interaction_type=ArticleInteractionType.LIKE).aggregate(Avg('article__embedding'))['article__embedding__avg']

        # 코사인 유사도가 높은 상위 기사 추출
        liked_article_ids = UserArticleInteraction.objects.filter(user_id=user_id, interaction_type=ArticleInteractionType.LIKE).values_list('article_id', flat=True)
        
        if category == ArticleCategory.전체:
            recommended_articles = cls.objects.exclude(id__in=liked_article_ids).order_by(
                CosineDistance('embedding', avg_embedding)
            )[:limit]
        else:
            recommended_articles = cls.objects.filter(category=category).exclude(id__in=liked_article_ids).order_by(
                CosineDistance('embedding', avg_embedding)
            )[:limit]

        recommended_articles = list(recommended_articles)
        random.shuffle(recommended_articles)

        if len(recommended_articles) < limit:
            # 추천된 기사가 limit보다 적으면 카테고리별 기사로 채움
            additional_articles = cls.get_article_list(category, limit - len(recommended_articles))
            recommended_articles = recommended_articles + additional_articles

        return recommended_articles

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
        - user: 좋아요를 누른 사용자 객체
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
