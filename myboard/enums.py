from django.db import models

class PostingCategory(models.TextChoices):
    전체 = "전체"
    자유게시판 = "자유게시판"
    취업정보 = "취업정보"
    자소서공유 = "자소서공유"
