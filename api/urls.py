# articles/urls.py

from django.urls import path
from .views import ArticleList, LikeArticle, RecommendArticles

urlpatterns = [
    path('articles/', ArticleList.as_view(), name='article-list'),
    path('articles/<int:article_id>/like/', LikeArticle.as_view(), name='like-article'),
    path('articles/recommendations/', RecommendArticles.as_view(), name='recommend-articles'),
]
