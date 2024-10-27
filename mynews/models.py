import datetime
from django.db import models
from pgvector.django import VectorField

from mynews.enums import ArticleCategory, ArticleInteractionType


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
    ) -> list["Article"]:
        print("category: ", category)
        if category == ArticleCategory.전체:
            return cls.objects.all()[:limit]
        else:
            return cls.objects.filter(category=category)[:limit]

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

    user = models.OneToOneField(
        "auth.User", on_delete=models.CASCADE, related_name="preferences"
    )
    user_embedding = VectorField(dimensions=1536)

    class Meta:
        indexes = [
            models.Index(fields=["user_id"], name="user_id_index"),
        ]


class UserArticleInteraction(models.Model):
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    interaction_type = models.CharField(choices=ArticleInteractionType.choices)
    interaction_date = models.DateTimeField()
