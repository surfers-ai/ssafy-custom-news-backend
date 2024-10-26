import uuid
from django.db import models

from mynews.enums import ArticleCategory, ArticleInteractionType
from myproject import settings

class Article(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=200)
    writer = models.CharField(max_length=255)
    write_date = models.DateTimeField()
    category = models.CharField(choices=ArticleCategory.choices)
    content = models.TextField()
    url = models.URLField(max_length=200)
    keywords = models.JSONField(default=list)
    embedding = models.BinaryField(default=b'\x00' * (1536 * 4))  # 1536 개의 float (4바이트) 벡터를 위한 기본값

    class Meta:
        indexes = [
            models.Index(fields=['id'], name='unique_article_id')
        ]

    @classmethod
    def get_article_list(cls, category: ArticleCategory, limit: int = 10) -> list["Article"]:
        print("category: ", category)
        if category == ArticleCategory.전체:
            return cls.objects.all()[:limit]
        else:
            return cls.objects.filter(category=category)[:limit]

class UserPreference(models.Model):
    """
    User의 확장 모델 - 뉴스 추천을 위한 추가 정보 저장
    기본 사용자 정보(이메일, 이름 등)는 auth_user 테이블 사용
    """
    user_email = models.EmailField(unique=True)
    user = models.OneToOneField(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='preferences'
    )
    user_embedding = models.BinaryField(
        default=b'\x00' * (1536 * 4),
        help_text='사용자 관심사 임베딩 벡터'
    )

class UserArticleInteraction(models.Model):
    user = models.ForeignKey(UserPreference, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    interaction_type = models.CharField(choices=ArticleInteractionType.choices)
    interaction_date = models.DateTimeField()
