from django.shortcuts import render,HttpResponse,redirect
from .models import Category, Booklet, Chapter, Page, Rating
from django.db import IntegrityError
from django.db.models import Avg
from django.http import JsonResponse
from django.conf import settings
from ToldInPages.ImageManager import getProcessedImage
from django.contrib import messages
from accounts.models import User
import os
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
# Create your views here.


@login_required(login_url='home')
def allCategories(request):
    if request.user.is_admin:
        categories = Category.objects.all().order_by('-created_at')
        suggestions = Booklet.objects.filter(if_published=True).order_by('?')[:5]
        data = {
            'categories':categories,
            'suggestions':suggestions
        }
        return render(request,'front-end/categories.html',data)
    return HttpResponse('Only admin can manage the category list')


@login_required(login_url='home')
def createCategory(request):
    if request.method == 'POST':
        if request.user.is_admin:
            name = request.POST.get('name')
            name = name.capitalize()
            try:
                Category.objects.create(name=name)
                messages.success(request,"Successfully created category",extra_tags='create-category')
                return redirect('all-categories')
            except IntegrityError as e:
                messages.info(request,"A category with the similar name already exists",extra_tags='create-category-unique')
                return redirect('create-category')
            except:
                messages.error(request,"Something went wrong",extra_tags='create-category-error')
                return redirect('create-category')
    suggestions = Booklet.objects.filter(if_published=True).order_by('?')[:5]
    data = {
        'suggestions':suggestions
    }
    return render(request,'front-end/create-category.html',data)        


@login_required(login_url='home')
def showEditCategory(request,category_id):
    category = Category.objects.get(id=category_id)
    suggestions = Booklet.objects.filter(if_published=True).order_by('?')[:5]
    data={
        'category':category,
        'suggestions':suggestions
    }
    return render(request,'front-end/edit-category.html',data)


@login_required(login_url='home')
def editCategory(request):
    if request.method == 'POST':
        category_id = request.POST.get('category_id')
        name = request.POST.get('name')
        try:
            category = Category.objects.get(id=category_id)
            category.name = name
            category.save()
            messages.success(request, "Successfully edited category",extra_tags='edit-category')
            return redirect('all-categories')
        except IntegrityError as e:
            messages.info(request, "A category with the similar name already exists",extra_tags='edit-category-unique')
            return redirect('show-edit-category',category.id)
        except:
            messages.error(request, "Something went wrong",extra_tags='edit-category-error')
            return redirect('show-edit-category',category.id)
        

@login_required(login_url='home')
def deleteCategory(request,category_id):
    try:
        category = Category.objects.get(id=category_id)
        category.delete()
        messages.success(request,"Successfully deleted the category",extra_tags='delete-category')
    except:
        messages.error(request,"Something went wrong",extra_tags='delete-category-error')
    return redirect(request.META['HTTP_REFERER'])


def allBooklets(request,user_id):
    user_exists = User.objects.filter(id=user_id).exists()
    if user_exists:
        user = User.objects.get(id=user_id)
    if request.user.id == user_id:
        paginate = Paginator(Booklet.objects.filter(user=request.user).order_by('-created_at'),settings.PAGINATION_LIMIT)
        page = request.GET.get('page')
        all_booklets = paginate.get_page(page)
    else:
        paginate = Paginator(Booklet.objects.filter(user_id=user_id,if_published=True).order_by('-created_at'),settings.PAGINATION_LIMIT)
        page = request.GET.get('page')
        all_booklets = paginate.get_page(page)
    suggestions = Booklet.objects.filter(if_published=True).order_by('?')[:5]
    data={
        'all_booklets':all_booklets,
        'user':user,
        'suggestions':suggestions
    }
    return render(request, 'front-end/my-booklets.html', data)
    return render(request, 'all-booklets.html', data)


def allChapters(request, booklet_id):
    booklet = Booklet.objects.get(id=booklet_id)
    if booklet:
        suggestions = Booklet.objects.filter(if_published=True).order_by('?')[:5]
        data={
            'booklet':booklet,
            'suggestions':suggestions
        }
        return render(request, 'front-end/my-chapters.html', data)
        return render(request, 'all-chapters.html', data)
    else:
        return HttpResponse("Booklet not found!")
    

def allPages(request,booklet_id,chapter_id):
    booklet = Booklet.objects.get(id=booklet_id)
    booklet_name = None
    booklet_cover_photo = None
    booklet_name = booklet.title
    booklet_cover_photo = booklet.cover_photo
    chapter_name = None
    if chapter_id != 0:
        chapter = Chapter.objects.get(id=chapter_id,booklet_id=booklet_id)
        if chapter:
            chapter_name = chapter.name
        else:
            HttpResponse("Chapter not found!")
        pages_with_chapters = Page.objects.filter(booklet_id=booklet_id,chapter_id=chapter_id).order_by('created_at')
    else:
        chapters = Page.objects.filter(booklet_id=booklet_id).values('chapter_id')
        pages_with_chapters = Page.objects.filter(chapter_id__in=chapters).order_by('chapter','created_at')
    suggestions = Booklet.objects.filter(if_published=True).order_by('?')[:5]
    data={
        'pages_with_chapters':pages_with_chapters,
        'booklet_name':booklet_name,
        'booklet_cover_photo':booklet_cover_photo,
        'chapter_name':chapter_name,
        'suggestions':suggestions,
        'booklet_id':booklet_id,
        'chapter_id':chapter_id,
        'user_id':booklet.user_id
    }
    return render(request,'front-end/my-pages.html',data)
    return render(request,'all-pages.html',data)

@login_required(login_url='home')
def createBooklet(request):
    if request.method == 'POST':
        try:
            if not request.POST.get('title'):
                return JsonResponse([0,"Title is required!"], safe=False)
            elif not request.POST.get('category_id'):
                return JsonResponse([0,"Category is required!"], safe=False)
            elif len(request.FILES)==0:
                return JsonResponse([0,"Cover photo is required!"], safe=False)
            elif len(request.POST.get('title'))>50:
                return JsonResponse([0,"Title cannot exceed 50 characters!"], safe=False)
            elif len(request.POST.get('tag_line'))>50:
                return JsonResponse([0,"Tag line cannot exceed 80 characters!"], safe=False)
            
            title = request.POST.get('title')
            tag_line = request.POST.get('tag_line')
            category_id = request.POST.get('category_id')
            cover_photo = request.FILES['cover_photo']

            extension = cover_photo.name.split('.')[-1]
            if extension != 'jpg' and extension != 'JPG' and extension != 'JPEG' and extension != 'jpeg' and extension != 'png' and extension != 'PNG':
                return JsonResponse([0,"Image has to be of jpg/png format"], safe=False)
            elif cover_photo.size > settings.MAX_UPLOAD_LIMIT:
                return JsonResponse([0,"Image size cannot exceed 5MB."], safe=False)
            cover_photo = getProcessedImage(request, cover_photo)
            booklet = Booklet.objects.create(user=request.user,title=title,tag_line=tag_line,cover_photo=cover_photo,category_id=category_id)
        except IntegrityError as err:
            return JsonResponse([0,"You have already created a booklet of the similar name"], safe=False)
        else:
            booklet.save()

        return JsonResponse([200,"Successfully Created Booklet"], safe=False)
    
    booklets = Booklet.objects.filter(user=request.user)
    categories = Category.objects.all()
    suggestions = Booklet.objects.filter(if_published=True).order_by('?')[:5]
    data = {
        'booklets':booklets,
        'categories':categories,
        'suggestions':suggestions
    }
    return render(request,'front-end/create-booklet.html',data)

@login_required(login_url='home')
def createChapter(request):
    if request.method == 'POST':
        booklet_id = request.POST.get('booklet_id')
        booklet = Booklet.objects.get(id=booklet_id,user=request.user)
        if booklet.chapter_count()>=10:
            messages.info(request, "At most 10 chapters can be created for a booklet.", extra_tags='chapter-limit')
            return redirect('all-booklets', request.user.id)
        if booklet:
            name = request.POST.get('name')
            chapter = Chapter.objects.create(booklet_id=booklet_id, name=name)
            chapter.save()
            messages.success(request, "New chapter created", extra_tags='chapter-created')
            return redirect('all-chapters',booklet_id)
        else:
            return HttpResponse("No booklet found!")

@login_required(login_url='home')
def showCreateChapter(request,booklet_id):
    booklet = Booklet.objects.get(id=booklet_id)
    if booklet.chapter_count()>=10:
        messages.info(request, "At most 10 chapters can be created for a booklet.", extra_tags='chapter-limit')
        return redirect('all-booklets', request.user.id)
    if booklet.user.id == request.user.id:
        suggestions = Booklet.objects.filter(if_published=True).order_by('?')[:5]
        data={
            'booklet':booklet,
            'suggestions':suggestions
        }
        return render(request, 'front-end/create-chapter.html', data)
    else:
        return HttpResponse("You are not authorized to add chapters to this booklet")

@login_required(login_url='home')
def showCreatePage(request, chapter_id):
    chapter = Chapter.objects.get(id=chapter_id)
    if not chapter:
        return HttpResponse("Chapter not found")
    if chapter.booklet.user.id == request.user.id:
        if chapter.page_count() >= 4:
            messages.info(request, "Max. of 4 pages are allowed in a chapter.", extra_tags='page-limit')
            return redirect('all-pages', chapter.booklet_id, chapter.id)
        suggestions = Booklet.objects.filter(if_published=True).order_by('?')[:5]
        data = {
            'chapter':chapter,
            'suggestions':suggestions
        }
        return render(request,'front-end/create-page.html',data)
    else:
        return HttpResponse("You are not authorized to add chapters to this booklet")
    
@login_required(login_url='home')
def createPage(request):
    if request.method == 'POST':
        if not request.POST.get('chapter_id'):
            return JsonResponse([0,"No chapter found"],safe=False)
        if not request.POST.get('description'):
            return JsonResponse([0,"Description is required!"],safe=False)
        
        chapter_id=request.POST.get('chapter_id')
        chapter = Chapter.objects.get(id=chapter_id)
        if not chapter:
            return JsonResponse([0,"No chapter found!"],safe=False)
        if chapter.booklet.user_id != request.user.id:
            return JsonResponse([0,"You are not allowed to add pages to this chapter!"],safe=False)
        if chapter.page_count() >= 4:
            return JsonResponse([0, "Max. of 4 pages are allowed in a chapter."],safe=False)
        
        description = request.POST.get('description')

        photo = None
        if len(request.FILES) > 0:
            photo = request.FILES.get('photo')
            extension = photo.name.split('.')[-1]
            if extension != 'jpg' and extension != 'JPG' and extension != 'JPEG' and extension != 'jpeg' and extension != 'png' and extension != 'PNG':
                return JsonResponse([0, "Image has to be of jpg/png format"], safe=False)
            elif photo.size > settings.MAX_UPLOAD_LIMIT:
                return JsonResponse([0, f"Image size cannot exceed {settings.MAX_UPLOAD_LIMIT/(1024*1024)}MB."], safe=False)
            photo = getProcessedImage(request,photo)
            try:
                page=Page.objects.create(booklet_id=chapter.booklet_id,chapter_id=chapter_id,photo=photo,description=description)
                page.save()
                return JsonResponse([200, 'success'], safe=False)
            except:
                return JsonResponse([0,"Something went wrong!"], safe=False)
        else:
            try:
                page=Page.objects.create(booklet_id=chapter.booklet_id,chapter_id=chapter_id,description=description)
                page.save()
                return JsonResponse([200, 'success'], safe=False)
            except Exception as e:
                return JsonResponse([0,e], safe=False)

@login_required(login_url='home')
def showEditBooklet(request,booklet_id):
    booklet = Booklet.objects.get(id=booklet_id, user=request.user)
    if booklet:
        categories = Category.objects.all()
        suggestions = Booklet.objects.filter(if_published=True).order_by('?')[:5]
        data = {
            'booklet':booklet,
            'categories':categories,
            'suggestions':suggestions
        }
        return render(request,'front-end/edit-booklet.html', data)
    else:
        return HttpResponse("You are not authorized to edit this booklet!")
    
@login_required(login_url='home')
def editBooklet(request):
    if request.method == 'POST':
        booklet_id = request.POST.get('booklet_id')
        booklet = Booklet.objects.get(id=booklet_id,user=request.user)
        if booklet:
            booklet.title = request.POST.get('title')
            booklet.tag_line = request.POST.get('tag_line')
            booklet.category_id = request.POST.get('category_id')
            if len(request.FILES) > 0:
                cover_photo = request.FILES.get('cover_photo')
                extension = cover_photo.name.split('.')[-1]
                if extension != 'jpg' and extension != 'JPG' and extension != 'JPEG' and extension != 'jpeg' and extension != 'png' and extension != 'PNG':
                    return JsonResponse([0,"Image has to be of jpg/png format"], safe=False)
                elif cover_photo.size > settings.MAX_UPLOAD_LIMIT:
                    return JsonResponse([0,f"Image size cannot exceed {settings.MAX_UPLOAD_LIMIT/(1024*1024)}MB."], safe=False)
                cover_photo = getProcessedImage(request, cover_photo)
                try:
                    os.remove(booklet.cover_photo.path)
                except:
                    return JsonResponse([0,"Something went wrong!"],safe=False)
                booklet.cover_photo = cover_photo
            booklet.save()
            return JsonResponse([200, "Successful"], safe=False)
        return HttpResponse("You are not authorized to edit this booklet.")
    
@login_required(login_url='home')
def showEditChapter(request,chapter_id):
    chapter = Chapter.objects.get(id=chapter_id)
    if chapter.booklet.user.id==request.user.id:
        suggestions = Booklet.objects.filter(if_published=True).order_by('?')[:5]
        data={
            'chapter':chapter,
            'suggestions':suggestions
        }
        return render(request,'front-end/edit-chapter.html',data)
    else:
        return HttpResponse("You are not authorized to edit this chapter!")
    
@login_required(login_url='home')
def editChapter(request):
    if request.method == 'POST':
        chapter_id = request.POST.get('chapter_id')
        chapter = Chapter.objects.get(id=chapter_id)
        if chapter.booklet.user.id == request.user.id:
            chapter.name=request.POST.get('name')
            chapter.save()
            return redirect('all-chapters',chapter.booklet_id)
        else:
            return HttpResponse('You are not authorized to update this chapter!')
        
@login_required(login_url='home')
def showEditPage(request,page_id):
    page=Page.objects.get(id=page_id)
    if page.booklet.user.id==request.user.id:
        suggestions = Booklet.objects.filter(if_published=True).order_by('?')[:5]
        data={
            'page':page,
            'suggestions':suggestions
        }
        return render(request,'front-end/edit-page.html',data)
    else:
        return HttpResponse('You are not authorized to update this page!')
    
@login_required(login_url='home')
def editPage(request):
    if request.method == 'POST':
        if not request.POST.get('page_id'):
            return JsonResponse([0,"No page found!"],safe=False)
        page_id=request.POST.get('page_id')
        page=Page.objects.get(id=page_id)
        if not page:
            return JsonResponse([0,"Page not found!"],safe=False)
        if page.booklet.user.id == request.user.id:
            if not request.POST.get('description'):
                return JsonResponse([0,"Description is required!"],safe=False)
            page.description = request.POST.get('description')
            if len(request.FILES) > 0:
                photo = request.FILES.get('photo')
                try:
                    extension = photo.name.split('.')[-1]
                    if extension != 'jpg' and extension != 'JPG' and extension != 'JPEG' and extension != 'jpeg' and extension != 'png' and extension != 'PNG':
                        return JsonResponse([0,"Image has to be of jpg/png format"], safe=False)
                    elif photo.size > settings.MAX_UPLOAD_LIMIT:
                        return JsonResponse([0,f"Image size cannot exceed {settings.MAX_UPLOAD_LIMIT}MB."], safe=False)
                    photo = getProcessedImage(request, photo)
                    try:
                        os.remove(page.photo.path)
                    except:
                        JsonResponse([0,"Something went wrong"],safe=False)
                    page.photo = photo
                except:
                    return JsonResponse([0,"Something went wrong"],safe=False)
            try:
                page.save()
                messages.success(request,"Successfully edited the page!",extra_tags='page-edit')
                return JsonResponse([200,"Success"],safe=False)
            except:
                return JsonResponse([0,"Something went wrong"],safe=False)
        else:
            return JsonResponse([0,"You are not authorized to edit the page!"],safe=False)
        
@login_required(login_url='home')
def deleteBooklet(request,booklet_id):
    booklet = Booklet.objects.get(id=booklet_id,user_id=request.user.id)
    if booklet:
        try:
            os.remove(booklet.cover_photo.path)
        except:
            return HttpResponse("Couldn't delete!")
        booklet.delete()
        return redirect(request.META['HTTP_REFERER'])
    else:
        return HttpResponse("You are not authorized to delete this booklet!")
    
@login_required(login_url='home')
def deleteChapter(request,chapter_id):
    chapter = Chapter.objects.get(id=chapter_id)
    if chapter.booklet.user.id == request.user.id:
        chapter.delete()
        return redirect(request.META['HTTP_REFERER'])
    else:
        return HttpResponse("You are not authorized to delete this chapter!")
    
@login_required(login_url='home')
def deletePage(request,page_id):
    page = Page.objects.get(id=page_id)
    if page.chapter.booklet.user.id == request.user.id:
        try:
            os.remove(page.photo.path)
        except Exception as e:
            return HttpResponse("Couldn't delete!")
        page.delete()
        return redirect(request.META['HTTP_REFERER'])
    else:
        return HttpResponse("You are not authorized to delete this page!")
    

def showBookCover(request,booklet_id):
    booklet = Booklet.objects.get(id=booklet_id)
    my_rating_exists = Rating.objects.filter(booklet_id=booklet_id,user_id=request.user.id).exists()
    my_rating = 0
    if my_rating_exists:
        my_rating = Rating.objects.get(booklet_id = booklet_id, user_id = request.user.id).rating
    if booklet.user.id != request.user.id:
        booklet.read += 1
        booklet.save()
    # if booklet.user.id != request.user.id:
    avg_rating = Rating.objects.filter(booklet_id = booklet_id).aggregate(Avg('rating'))['rating__avg']
    if avg_rating:
        avg_rating = round(avg_rating,2)
    data = {
        'booklet':booklet,
        'my_rating':round(my_rating,2),
        'rating_max':list(range(1,6)),
        'avg_rating':avg_rating
    }
    return render(request,'front-end/book-cover.html',data)


def getPageChapters(booklet_id):
    chapters = Page.objects.filter(booklet_id=booklet_id).values('chapter_id').distinct('chapter_id').order_by('chapter_id')
    return chapters


def getPageData(chapters,page_no):
    page = Page.objects.filter(chapter_id__in=chapters).order_by('chapter_id','created_at')[page_no-1:page_no].get()
    return page


def loadPageInReader(request,booklet_id,page_no):
    chapters = getPageChapters(booklet_id)
    page = getPageData(chapters,page_no)
    suggestions = Booklet.objects.filter(if_published=True).order_by('?')[:5]
    data={
        'page':page,
        'page_no':page_no,
        'next_page':page_no+1,
        'prev_page':page_no-1,
        'suggestions':suggestions
    }
    return render(request,'front-end/reader.html',data)


def loadChapterwisePageInReader(request,page_id,page_no):
    page = Page.objects.get(id=page_id)
    prev_chapter_pages = Page.objects.filter(chapter_id__lt=page.chapter_id,booklet_id=page.booklet_id).count()
    same_chapter_pages = Page.objects.filter(id__lt=page_id,chapter_id=page.chapter_id).count()
    page_no = prev_chapter_pages+same_chapter_pages+1
    suggestions = Booklet.objects.filter(if_published=True).order_by('?')[:5]
    data = {
        'page':page,
        'page_no':page_no,
        'next_page':page_no+1,
        'prev_page':page_no-1,
        'suggestions':suggestions
    } 
    return render(request,'front-end/reader.html',data)


def goToChapter(request,booklet_id,chapter_no):
    chapters = getPageChapters(booklet_id)
    if chapters.count()>1:
        prev_chapters = chapters[:chapter_no-1]
        prev_total_pages = Page.objects.filter(chapter_id__in=prev_chapters).count()
        page_no = prev_total_pages+1
    else:
        page_no=1
    page = getPageData(chapters,page_no)
    suggestions = Booklet.objects.filter(if_published=True).order_by('?')[:5]
    data={
        'page':page,
        'page_no':page_no,
        'next_page':page_no+1,
        'prev_page':page_no-1,
        'suggestions':suggestions
    }
    return render(request,'front-end/reader.html',data)

@login_required(login_url='home')
def publishBooklet(request, booklet_id):
    try:
        booklet = Booklet.objects.get(id=booklet_id)
        if booklet and booklet.user.id != request.user.id:
            return HttpResponse("Booklet not available")
        booklet.if_published = not booklet.if_published
        booklet.save()

        return redirect('show-book-cover',booklet.id)
    except:
        return HttpResponse("Something went wrong!")

@login_required(login_url='home')
def rateBooklet(request):
    try:
        booklet_id = request.GET.get('booklet_id')
        user_id = request.user.id
        rating_value = request.GET.get('rating')
        rating_exists = Rating.objects.filter(booklet_id=booklet_id,user_id=user_id).exists()
        if rating_exists:
            if rating_exists:
                rating = Rating.objects.get(booklet_id=booklet_id,user_id=user_id)
                rating.rating = rating_value
                rating.save()
            else:
                return HttpResponse("Error")
        else:
            rating=Rating.objects.create(user_id=user_id,booklet_id=booklet_id,rating=rating_value)
        avg_rating = Rating.objects.filter(booklet_id=booklet_id).aggregate(Avg('rating'))
        if avg_rating:
            avg_rating = round(avg_rating['rating__avg'],2)
        else:
            avg_rating = 0
        return JsonResponse([rating_value,avg_rating],safe=False)
    except Exception as e:
        return HttpResponse(e)