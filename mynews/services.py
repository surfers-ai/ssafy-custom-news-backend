from django.http import JsonResponse


class RecommendationService:
    def __init__(self):
        self.user_preferences = {}
    
    def add_user_preference(self, user_id, category):
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = set()
        self.user_preferences[user_id].add(category)
    
    def get_recommendations(self, user_id, articles):
        if user_id not in self.user_preferences:
            return articles
        
        user_categories = self.user_preferences[user_id]
        recommended_articles = [
            article for article in articles
            if article.category in user_categories
        ]
        
        return recommended_articles[:10]  # 상위 10개 기사만 반환
