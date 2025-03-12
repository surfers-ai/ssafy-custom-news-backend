# Generated by Django 5.1.2 on 2024-11-03 16:31

import django.db.models.deletion
import pgvector.django.vector
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Article",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=200)),
                ("writer", models.CharField(max_length=255)),
                ("write_date", models.DateTimeField()),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("전체", "전체"),
                            ("IT_과학", "IT/과학"),
                            ("건강", "건강"),
                            ("경제", "경제"),
                            ("교육", "교육"),
                            ("국제", "국제"),
                            ("라이프스타일", "라이프스타일"),
                            ("문화", "문화"),
                            ("사건사고", "사건사고"),
                            ("사회일반", "사회일반"),
                            ("산업", "산업"),
                            ("스포츠", "스포츠"),
                            ("여성복지", "여성복지"),
                            ("여행레저", "여행레저"),
                            ("연예", "연예"),
                            ("정치", "정치"),
                            ("지역", "지역"),
                            ("취미", "취미"),
                        ]
                    ),
                ),
                ("content", models.TextField(unique=True)),
                ("url", models.URLField(unique=True)),
                ("keywords", models.JSONField(default=list)),
                ("embedding", pgvector.django.vector.VectorField(dimensions=1536)),
            ],
            options={
                "indexes": [models.Index(fields=["id"], name="unique_article_id")],
            },
        ),
        migrations.CreateModel(
            name="UserArticleInteraction",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "interaction_type",
                    models.CharField(choices=[("like", "Like"), ("read", "Read")]),
                ),
                ("interaction_date", models.DateTimeField()),
                (
                    "article",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="mynews.article"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
