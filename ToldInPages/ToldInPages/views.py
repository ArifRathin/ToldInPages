from django.shortcuts import render, HttpResponse
from accounts.models import User, Followers
from booklets.models import Booklet
from django.db.models import Count
from  django.http import JsonResponse
from django.core.paginator import Paginator
from django.conf import settings
from django.db.models import Q

def home(request):
    followed_booklets = []
    if request.user.is_authenticated:
        followed_ids = Followers.objects.filter(follower_id = request.user.id).values('followed_id')
        followed_accounts_booklets = Booklet.objects.filter(user_id__in=followed_ids, if_published=True).order_by('-created_at')[:8]
        followed_booklets.append(followed_accounts_booklets)
    
    booklet_categories = Booklet.objects.values('category').annotate(total_booklets = Count('id')).order_by('-total_booklets').distinct()
    home_booklets = []
    for category in booklet_categories:
        booklets = Booklet.objects.filter(category_id=category['category'],if_published=True).order_by('-publishing_time')[:8]
        home_booklets.append(booklets)

    data = {
        'followed_booklets':followed_booklets,
        'home_booklets':home_booklets
    }
    return render(request,'index.html',data)


def bookletsByCategory(request, category_id):
    paginate = Paginator(Booklet.objects.filter(category_id=category_id, if_published=True).order_by('-publishing_time'),settings.PAGINATION_LIMIT)
    page = request.GET.get('page')
    booklets = paginate.get_page(page)
    data = {
        'type':'by_category',
        'booklets':booklets
    }
    return render(request, 'all-booklets.html',data)


def bookletsByFollow(request):
    followed_ids = Followers.objects.filter(follower_id=request.user.id).values('followed_id')
    paginate = Paginator(Booklet.objects.filter(user_id__in=followed_ids, if_published=True).order_by('-publishing_time'),settings.PAGINATION_LIMIT)
    page = request.GET.get('page')
    booklets = paginate.get_page(page)
    data = {
        'type':'by_follow',
        'booklets':booklets
    }
    return render(request, 'all-booklets.html',data)


def searchSuggestions(request):
    keywords = request.GET.get('keywords')
    if request.user.is_authenticated:
        booklets = Booklet.objects.filter((Q(if_published=True) | Q(user_id = request.user.id)) & (Q(title__icontains=keywords) | Q(tag_line__icontains=keywords))).values().distinct()[:3]
    else:
        booklets = Booklet.objects.filter(Q(if_published=True) & (Q(title__icontains=keywords) | Q(tag_line__icontains=keywords))).values().distinct()[:3]
    authors = User.objects.filter(Q(first_name__icontains=keywords) | Q(last_name__icontains=keywords)).values().distinct()[:3]
    suggestion_dict = {
        'booklets':list(booklets),
        'authors':list(authors)
    }

    return JsonResponse(suggestion_dict)


def searchBookletResult(request):
    keywords = request.GET.get('keywords')
    if request.user.is_authenticated:
        paginate = Paginator(Booklet.objects.filter((Q(if_published=True) | Q(user_id = request.user.id)) & (Q(title__icontains=keywords) | Q(tag_line__icontains=keywords))).distinct(),settings.PAGINATION_LIMIT)
    else:
        paginate = Paginator(Booklet.objects.filter(Q(if_published=True) & (Q(title__icontains=keywords) | Q(tag_line__icontains=keywords))).distinct(),settings.PAGINATION_LIMIT)
    page = request.GET.get('page')
    booklets = paginate.get_page(page)
    suggestions = Booklet.objects.filter(if_published=True).order_by('?')[:5]
    search_dict = {
        'booklets':booklets,
        'suggestions':suggestions,
        'keywords':keywords,
        'category':'booklet'
    }

    return render(request,'search-booklets-results.html',search_dict)


def searchAuthorResult(request):
    keywords = request.GET.get('keywords')
    paginate = Paginator(User.objects.filter(Q(first_name__icontains=keywords) | Q(last_name__icontains=keywords)).distinct(),settings.PAGINATION_LIMIT)
    page = request.GET.get('page')
    authors = paginate.get_page(page)
    suggestions = Booklet.objects.filter(if_published=True).order_by('?')[:5]
    search_dict = {
        'authors':authors,
        'suggestions':suggestions,
        'keywords':keywords,
        'category':'author'
    }

    return render(request,'search-authors-results.html',search_dict)
