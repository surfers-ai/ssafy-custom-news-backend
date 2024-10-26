from django.db import models

from mynews.enums import ArticleCategory

class Article(models.Model):
    title = models.CharField(max_length=200)
    writer = models.CharField()
    write_date = models.DateTimeField()
    category = models.CharField(choices=ArticleCategory.choices)
    content = models.TextField()
    key_word = models.JSONField(default=list)
    url = models.URLField()

    @classmethod
    def get_article_list(cls, category: ArticleCategory, limit: int = 10) -> list["Article"]:
        if category == ArticleCategory.ALL:
            return cls.objects.all()[:limit]
        else:
            return cls.objects.filter(category=category)[:limit]
