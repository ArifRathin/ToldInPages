from django.db import models
from django.db.models import Avg
from accounts.models import User
import os
from uuid import uuid4


def save_cover_photo(instance, filename):
    extension = filename.split('.')[-1]
    if instance.pk:
        filename = f'{instance.pk}{uuid4().hex}.{extension}'
    else:
        filename = f'{instance.user.id}{uuid4().hex}.{extension}'
    upload_to = 'cover_photos'
    return os.path.join(upload_to, filename)


def save_page_photo(instance, filename):
    extension = filename.split('.')[-1]
    filename = f'{uuid4().hex}.{extension}'
    upload_to = 'page_photos'
    return os.path.join(upload_to,filename)


# Models.
class Category(models.Model):
    name = models.CharField(unique=True,max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

class Booklet(models.Model):
    category = models.ForeignKey(Category,on_delete=models.CASCADE,null=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    tag_line = models.CharField(max_length=255,default=None, null=True)
    cover_photo = models.ImageField(upload_to=save_cover_photo,default=None,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    read = models.BigIntegerField(default=0)
    if_published = models.BooleanField(default=False)
    publishing_time = models.DateTimeField(auto_now=True, null=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='unique_title_constraint',
                fields=('title','user_id')
            )
        ]


    def chapter_count(self):
        return self.chapter_set.filter(booklet_id=self.id).count()
    

    def all_chapters(self):
        return self.chapter_set.filter(booklet_id=self.id).order_by('id')
    

    def page_count(self):
        return self.page_set.filter(booklet_id=self.id).count()
    

    def rated_by_readers_count(self):
        return self.rating_set.filter(booklet_id=self.id).count()
    

    def avg_rating(self):
        return self.rating_set.filter(booklet_id=self.id).aggregate(rating=Avg('rating'))['rating']
    

class Chapter(models.Model):
    booklet = models.ForeignKey(Booklet, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


    def page_count(self):
        return self.page_set.filter(chapter_id=self.id).count()


class Page(models.Model):
    booklet = models.ForeignKey(Booklet, on_delete=models.CASCADE)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, null=True, default=None)
    photo = models.ImageField(upload_to=save_page_photo,default=None,null=True)
    video_link = models.CharField(max_length=255, default=None, null=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    booklet = models.ForeignKey(Booklet, on_delete=models.CASCADE)
    rating = models.IntegerField()