from rest_framework import serializers
from .models import Article, UserLikedArticle, User
from dj_rest_auth.serializers import UserDetailsSerializer

class ArticleSerializer(serializers.ModelSerializer) :
    class Meta :
        model = Article     #Article 모델 사용
        fields = '__all__'  # 모든 필드 포함

class UserLikedArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLikedArticle
        fields = '__all__'



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'user_name', 'created_at', 'updated_at']
