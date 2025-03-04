from django.contrib import admin
from booklets.models import Category, Booklet, Chapter, Page
# Register your models here.
class BookletAdmin(admin.ModelAdmin):
    list_display=('category','user','title','tag_line','cover_photo','created_at','modified_at')
admin.site.register(Booklet, BookletAdmin)

class ChapterAdmin(admin.ModelAdmin):
    list_display=('booklet','name','created_at','modified_at')
admin.site.register(Chapter, ChapterAdmin)

class PageAdmin(admin.ModelAdmin):
    list_display=('booklet','chapter','photo','video_link','description','created_at','modified_at')
admin.site.register(Page,PageAdmin)

class CategoryAdmin(admin.ModelAdmin):
    list_display=('name','created_at','modified_at')
admin.site.register(Category, CategoryAdmin)