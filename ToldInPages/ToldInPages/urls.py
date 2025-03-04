"""
URL configuration for ToldInPages project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts import views
from . import views as baseViews

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',baseViews.home, name='home'),
    path('booklets-by-category/<int:category_id>',baseViews.bookletsByCategory, name='booklets-by-category'),
    path('booklets-by-follow',baseViews.bookletsByFollow, name='booklets-by-follow'),
    path('search-suggestions',baseViews.searchSuggestions, name='search-suggestions'),
    path('internalaccount/', include('accounts.urls')),
    path('accounts/', include('allauth.urls')),
    path('booklets/', include('booklets.urls')),
    path('search-booklet-page', baseViews.searchBookletResult, name='search-booklet-page'),
    path('search-author-page', baseViews.searchAuthorResult, name='search-author-page')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)