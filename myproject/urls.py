"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path

from myboard.views import BoardListView, PostingView, WriteCommentView, WritePostingView
from mynews.views import (
    ChatbotView,
    DashboardView,
    LikeArticleView,
    NewsListView,
    ArticleView,
    WriteArticleView,
)

urlpatterns = [
    path("health-check/", include("health_check.urls")),
    path("admin/", admin.site.urls),
    # auth
    path("auth/", include("dj_rest_auth.urls")),
    path("auth/registration/", include("dj_rest_auth.registration.urls")),
    # news
    path("news-list/", NewsListView.as_view()),
    path("news/<int:article_id>/", ArticleView.as_view()),
    path("write-article/", WriteArticleView.as_view()),
    # like article
    path("news/like/", LikeArticleView.as_view()),
    # dashboard
    path("dashboard/", DashboardView.as_view()),
    # chat with news
    path("news/chat/", ChatbotView.as_view()),

    # board
    path("board-list/", BoardListView.as_view()),
    path("board/<int:posting_id>/", PostingView.as_view()),
    path("write-posting/", WritePostingView.as_view()),
    path("write-comment/<int:posting_id>/", WriteCommentView.as_view()),
]
