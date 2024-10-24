from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin


# Create your models here.
class Article(models.Model):
    title = models.CharField(max_length=200)
    writer = models.CharField(max_length=100)
    write_date = models.DateTimeField()
    category = models.CharField(max_length=50)
    content = models.TextField()
    key_word = models.JSONField()
    tfidf_vector = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.title

class UserLikedArticle(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    liked_at = models.DateTimeField(auto_now_add=True)


class UserManager(BaseUserManager):

    def create_user(self, email, user_name, password, **kwargs):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=email,
            user_name=user_name,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email=None, user_name=None, password=None, **extra_fields):
        superuser = self.create_user(
            email=email,
            user_name=user_name,
            password=password,
        )
        superuser.save(using=self._db)
        return superuser


class User(AbstractBaseUser, PermissionsMixin):
    
    email = models.EmailField(max_length=30, unique=True, null=False, blank=False)
    user_name = models.CharField(max_length=100, unique=True, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['user_name']

    def __str__(self):
        return self.email

    def get_username(self):
        return self.user_name