from django.db import models

class PostingCategory(models.TextChoices):
    전체 = "전체"
    자유 = "자유"
    질문 = "질문"
    토론 = "토론"
    정보 = "정보"
