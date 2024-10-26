from django.db import models

class ArticleCategory(models.TextChoices):
    ALL = 'ALL', '전체'
    POLITICS = 'POLITICS', '정치'
    ECONOMY = 'ECONOMY', '경제'