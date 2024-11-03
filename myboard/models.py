from datetime import datetime
from typing import List
from django.db import models
from pgvector.django import VectorField
from django.contrib.auth.models import User
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

from myboard.enums import PostingCategory

class Posting(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    writer = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    write_date = models.DateTimeField()
    category = models.CharField(choices=PostingCategory.choices)
    content = models.TextField()
    keywords = models.JSONField(default=list)
    embedding = VectorField(dimensions=1536)

    @classmethod
    def get_posting_list(cls, category: PostingCategory, page: int = 1, limit: int = 10) -> tuple[List['Posting'], int]:
        offset = (page - 1) * limit
        
        if category == PostingCategory.전체:
            queryset = cls.objects
        else:
            queryset = cls.objects.filter(category=category)
        
        total_count = queryset.count()
        postings = queryset.order_by("-write_date")[offset:offset + limit]
        
        return postings, total_count
    
    @classmethod
    def post_posting(cls, title: str, writer: User, category: PostingCategory, content: str, keywords: list[str]) -> int:            
        text = title + "\n" + content + "\n" + "\n".join(keywords)
        embedding = cls.get_embedding(text)

        write_date = datetime.now()

        posting = cls.objects.create(
            title=title,
            writer=writer,
            write_date=write_date,
            category=category,
            content=content,
            keywords=keywords,
            embedding=embedding,
        )
        return posting.id


    @classmethod
    def get_embedding(cls, text: str) -> list[float]:
        client = OpenAI()
        response = client.embeddings.create(input=text, model="text-embedding-3-small")
        return response.data[0].embedding

class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    posting = models.ForeignKey(Posting, on_delete=models.CASCADE, related_name="comments")
    writer = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    write_date = models.DateTimeField()
    content = models.TextField()

    @classmethod
    def post_comment(cls, posting_id: int, writer: User, content: str) -> 'Comment':
        write_date = datetime.now()
        comment = cls.objects.create(posting_id=posting_id, writer=writer, write_date=write_date, content=content)
        return comment
