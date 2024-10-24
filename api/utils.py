# articles/utils.py

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from api.models import Article

def vectorize_articles():
    articles = Article.objects.all()
    contents = [article.content for article in articles]
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(contents)
    feature_names = vectorizer.get_feature_names_out()

    for idx, article in enumerate(articles):
        vector = vectors[idx].toarray()[0]
        # JSONField에 저장하기 위해 딕셔너리로 변환
        vector_dict = dict(zip(feature_names, vector))
        article.vector = vector_dict
        article.save()


def recommend_articles(user, top_n=5):
    liked_articles = Article.objects.filter(userlikedarticle__user=user)
    if not liked_articles:
        return Article.objects.none()

    # 사용자가 좋아요 한 기사들의 벡터 평균을 계산
    liked_vectors = [np.array(list(article.vector.values())) for article in liked_articles]
    user_profile = np.mean(liked_vectors, axis=0)

    all_articles = Article.objects.exclude(userlikedarticle__user=user)
    recommendations = []

    for article in all_articles:
        article_vector = np.array(list(article.vector.values()))
        # 코사인 유사도 계산
        cosine_similarity = np.dot(user_profile, article_vector) / (np.linalg.norm(user_profile) * np.linalg.norm(article_vector))
        recommendations.append((cosine_similarity, article))

    # 유사도 순으로 정렬하여 상위 N개 기사 추천
    recommendations.sort(reverse=True)
    top_articles = [article for _, article in recommendations[:top_n]]
    return top_articles
