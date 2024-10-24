from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Article, UserLikedArticle
from .serializers import ArticleSerializer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from rest_framework.permissions import IsAuthenticated

class ArticleList(APIView):
    def get(self, request):
        articles = Article.objects.all()
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)

class LikeArticle(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, article_id):
        user = request.user
        article = Article.objects.get(pk=article_id)
        UserLikedArticle.objects.get_or_create(user=user, article=article)
        return Response({'status': 'article liked'}, status=status.HTTP_200_OK)

class RecommendArticles(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        liked_articles = Article.objects.filter(userlikedarticle__user=user)
        if not liked_articles.exists():
            return Response({'message': 'No liked articles'}, status=status.HTTP_200_OK)
        
        all_articles = Article.objects.all()
        tfidf = TfidfVectorizer(stop_words='')
        tfidf_matrix = tfidf.fit_transform([article.content for article in all_articles])
        cosine_similarities = linear_kernel(tfidf_matrix, tfidf_matrix)
        indices = {i: article.id for i, article in enumerate(all_articles)}
        id_indices = {article.id: i for i, article in enumerate(all_articles)}
        similar_articles = set()
        for liked_article in liked_articles:
            idx = id_indices[liked_article.id]
            sim_scores = list(enumerate(cosine_similarities[idx]))
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            for i, score in sim_scores[1:6]:
                similar_articles.add(all_articles[i])
        similar_articles = similar_articles - set(liked_articles)
        serializer = ArticleSerializer(similar_articles, many=True)
        return Response(serializer.data)
