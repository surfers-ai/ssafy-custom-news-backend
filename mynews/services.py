class RecommendationService:
    def __init__(self):
        self.user_preferences = {}

    def add_user_preference(self, user_id, category):
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = set()
        self.user_preferences[user_id].add(category)