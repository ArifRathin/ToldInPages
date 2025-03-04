from django.db import models
from django.db.models import Sum, Avg
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
import os
from django.db import IntegrityError
from uuid import uuid4
from django.shortcuts import HttpResponse,redirect
# Create your models here.
class UserManager(BaseUserManager):


    def create_user(self, email, first_name, last_name, password=None, username=None):
            user = self.model(
                email = self.normalize_email(email),
                first_name = first_name,
                last_name = last_name,
                username = username
            )
            user.set_password(password)
            user.save(using=self._db)
            return user
    

    def create_superuser(self, email, first_name="Main", last_name="Admin", password=None, username=None):
        user = self.create_user(
            email = email,
            first_name = first_name,
            last_name = last_name,
            password = password,
            username=username
        )

        user.is_active = True
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True

        user.save(using=self._db)
        return user


def save_profile_photo(instance, filename):
    extension = filename.split('.')[:-1]
    if instance.pk:
        filename = f'{instance.pk}{uuid4().hex}.{extension}'
    else:
        filename = f'{uuid4().hex}.{extension}'
    upload_to = "profile_photos"
    return os.path.join(upload_to,filename)


class User(AbstractBaseUser):
    email = models.EmailField(unique=True, max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    username = models.CharField(max_length=255,default=None, null=True)
    profile_photo = models.ImageField(default="profile_photos/default.png", upload_to=save_profile_photo)
    security_code = models.CharField(max_length=255, default=None, null=True)
    security_code_generated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = "email"

    objects = UserManager()


    def __str__(self):
        return self.email
    

    def has_perm(self, perm, obj=True):
        return self.is_admin
    

    def has_module_perms(self, app_label):
        return True
    

    def booklets(self):
        return self.booklet_set.filter(user_id=self.id)
    

    def published_booklets(self):
        return self.booklet_set.filter(user_id=self.id, if_published=True)


    def booklet_count(self):
        return self.booklet_set.filter(user_id=self.id).count()
    

    def published_booklet_count(self):
        return self.booklet_set.filter(user_id=self.id,if_published=True).count()
    

    def booklet_read_count(self):
        return self.booklet_set.filter(user_id=self.id).aggregate(total=Sum('read'))['total']
    

    # def avg_rating(self):
    #     avg_rating = self.rating_set.filter(user_id=self.id).aggregate(avg=Avg('rating'))['avg']
    #     if avg_rating:
    #         avg_rating = round(avg_rating,2)
    #         return round(avg_rating,2)
    #     return None
    

    def follower_count(self):
        return Followers.objects.filter(followed_id = self.id).count()
    

    def following_count(self):
        return Followers.objects.filter(follower_id = self.id).count()
    

class Followers(models.Model):
    followed_id = models.BigIntegerField()
    follower_id = models.BigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)