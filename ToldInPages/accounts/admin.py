from django.contrib import admin
from .models import User
# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display=('email','first_name','last_name','created_at','modified_at')
admin.site.register(User,UserAdmin)