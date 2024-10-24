from django.contrib import admin

from api.models import Article, UserLikedArticle

# Register your models here.
admin.site.register(Article)
admin.site.register(UserLikedArticle)