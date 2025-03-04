from django.shortcuts import render, HttpResponse, redirect
from .models import User, Followers
from booklets.models import Booklet, Category, Page, Rating
from django.contrib.auth import login, logout, authenticate
from django.http import JsonResponse
from .mailManager import genSecurityCode, sendSecurityCode
from django.urls import reverse
from ToldInPages.ImageManager import getProcessedImage
from django.conf import settings
from django.contrib import messages
from django.db import IntegrityError
from django.db.models import Avg
# Create your views here.


def createSuperUser(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        retype_password = request.POST.get('retype_password')
        if password != retype_password:
            return HttpResponse("Passwords don't match")
        try:
            User.objects.create_superuser(email=email, password=password, first_name=first_name, last_name=last_name)
        except Exception as e:
            return HttpResponse(e)

    suggestions = Booklet.objects.filter(if_published=True).order_by('?')[:5]
    data={
        'suggestions':suggestions
    }
    return render(request,'front-end/create-super-user.html',data)


def signUp(request):
    if request.method == 'POST':
        if not request.POST.get('first_name'):
            return JsonResponse(['info',"First name is required"],safe=False)
        elif not request.POST.get('email'):
            return JsonResponse(['info',"Email is required"],safe=False)
        elif not request.POST.get('password'):
            return JsonResponse(['info',"Password is required"],safe=False)
        
        password=request.POST.get('password')
        retype_password=request.POST.get('retype_password')
        if password!=retype_password:
            return JsonResponse(['error',"Passwords don't match"],safe=False)
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')

        try:
            user = User.objects.create_user(email=email, first_name=first_name, last_name=last_name)
            user.is_active = False
            user.set_password(password)
            user.save()

            response = verificationManager(request, user)
            if response['status']:
                return JsonResponse(['success','verify'],safe=False)
            else:
                return JsonResponse(['error',"Something went wrong"],safe=False)
        except IntegrityError as e:
            return JsonResponse(['error',"An account with a similar email already exists."],safe=False)

    return render(request, 'sign-up.html')


def showVerifyPage(request):
    email = request.POST.get('verify-email')
    suggestions = Booklet.objects.filter(if_published=True).order_by('?')[:5]
    data = {
        'text':"Please enter the security code we have sent to your email to verify your account.",
        'email':email,
        'suggestions':suggestions 
    }
    return render(request, 'front-end/verify-account.html',data)

def verifyAccount(request):
    if request.method == 'POST':
        suggestions = Booklet.objects.filter(if_published=True).order_by('?')[:5]
        if not request.POST.get('email'):
            messages.info(request,"Email is required",extra_tags='verify-email-required')
            return redirect(request.META['HTTP_REFERER'])
        email = request.POST.get('email')
        data = {
            'text':"Please enter the security code we have sent to your email to verify your account.",
            'email':email,
            'suggestions':suggestions 
        }
        if not request.POST.get('security_code'):
            messages.info(request,"Security code is required",extra_tags='verify-security-code-required')
            return render(request, 'front-end/verify-account.html',data)
        security_code = request.POST.get('security_code')
        user = User.objects.filter(email=email).exists()
        if user:
            user = User.objects.get(email=email)
            if user.is_active:
                messages.info(request, "Account already active. Please log in to continue",extra_tags='verify-account-active')
                return render(request, 'front-end/verify-account.html',data)
            user.is_active = True
            user.save()
            user = authenticate(request, email=email, password=security_code)
            if user:
                try:
                    login(request,user)
                    return redirect('home')
                except:
                    messages.error(request, "Couldn't log in",extra_tags='verify-log-in-error')
                    return render(request, 'front-end/verify-account.html',data)
            else:
                try:
                    user.is_active = False
                    user.save()
                except:
                    messages.error(request, "Something went wrong",extra_tags='verify-error')
                    return render(request, 'front-end/verify-account.html',data)
                messages.error(request,"Authentication failed!",extra_tags='verify-auth-failed')
                return render(request, 'front-end/verify-account.html',data)
        messages.error(request,"User not found",extra_tags='verify-user-not-found')
        return render(request, 'front-end/verify-account.html',data)


def verificationManager(request,user):
    security_code = genSecurityCode(request)
    if not user.security_code_generated:
        user.security_code = user.password
        user.security_code_generated = True
    user.set_password(security_code)
    user.save()
    code_sent = sendSecurityCode(request,security_code,"Account Verification")
    if code_sent:
        suggestions = Booklet.objects.filter(if_published=True).order_by('?')[:5]
        data = {
            'text':"Please enter the security code we have sent to your email to verify your account.",
            'email':user.email,
            'suggestions':suggestions 
        }
        return {'status': True, 'data':data}
    else:
        return {'status': False, 'data':{}}


def accountVerification(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if not request.POST.get('email'):
            messages.info(request,"Email is required",extra_tags='verif-email-required')
            return redirect(request.META['HTTP_REFERER'])
        user = User.objects.filter(email=email).exists()
        if user:
            user = User.objects.get(email=email)
            response = verificationManager(request, user)
            if response['status']:
                return render(request, 'front-end/verify-account.html',response['data'])
            else:
                messages.error(request,"Something went wrong",extra_tags='verif-verification-error')
                return redirect(request.META['HTTP_REFERER'])
        else:
            messages.error(request,"User not found",extra_tags='verif-user-not-found')
            return redirect(request.META['HTTP_REFERER'])
    suggestions = Booklet.objects.filter(if_published=True).order_by('?')[:5]
    data = {
        'text':"Please enter your email below. We will send you a Security Code to verify your account.",
        'suggestions':suggestions
    }
    return render(request, 'front-end/send-security-code.html', data)


def logIn(request):
    if request.method == 'POST':
        if not request.POST.get('email'):
            return JsonResponse(['info',"Email is required to log in."],safe=False)
        email = request.POST.get('email')
        if not request.POST.get('password'):
            return JsonResponse(['info',"Password is required to log in."],safe=False)
        password = request.POST.get('password')
        next_page = request.POST.get('next-page')
        acc = User.objects.filter(email=email).exists()
        if not acc:
            return JsonResponse(['info',"Account not found"],safe=False)
        acc = User.objects.get(email=email)
        if not acc.is_active:
            return JsonResponse(['warning',"Account inactive"],safe=False)
        if acc.security_code_generated:
            try:
                security_code = acc.security_code
                acc.security_code = acc.password
                acc.password = security_code
                acc.save()
            except:
                return JsonResponse(['error',"Something went wrong"],safe=False)
        user = authenticate(request, email=email, password=password)
        if user:
            try:
                if acc.security_code_generated:
                    acc.security_code_generated = False
                    acc.security_code = None
                    acc.save()
                login(request, user)
                return JsonResponse(['success',next_page],safe=False)
            except:
                return JsonResponse(['error',"Log in failed"],safe=False)
        if acc.security_code_generated:
            try:
                curr_password = acc.password
                acc.password = acc.security_code
                acc.security_code = curr_password
                acc.save()
            except:
                return JsonResponse(['error',"Something went wrong!"],safe=False)
        return JsonResponse(['error',"Invalid email/password!"],safe=False)
    return render(request, 'login.html')


def logOut(request):
    logout(request)
    return redirect('home')


def forgotPassword(request):
    if request.method == 'POST':
        if not request.POST.get('email'):
            messages.info(request,"Email is required!",extra_tags='email-required')
            return redirect(request.META['HTTP_REFERER'])
        email = request.POST.get('email')
        email_exists = User.objects.filter(email=email).exists()
        if email_exists:
            try:
                acc = User.objects.get(email=email)
                security_code = genSecurityCode(request)
                if not acc.security_code_generated:
                    acc.security_code = acc.password
                    acc.security_code_generated = True
                acc.set_password(security_code)
                acc.save()
            except:
                messages.info(request,"Something went wrong!",extra_tags='error')
                return redirect(request.META['HTTP_REFERER'])
        else:
            messages.info(request,"This email isn't associated with any account.",extra_tags='email-not-found')
            return redirect(request.META['HTTP_REFERER'])
        code_sent = sendSecurityCode(request, security_code, "Change Password")
        if code_sent:
            suggestions = Booklet.objects.filter(if_published=True).order_by('?')[:5]
            data = {
                'email':email,
                'suggestions':suggestions
            }
            return render(request,'front-end/change-password.html',data)
        messages.info(request,"Failed!",extra_tags='failed')
        return HttpResponse("Failed")
    suggestions = Booklet.objects.filter(if_published=True).order_by('?')[:5]
    data = {
        'text':"Please enter your email below. We will send you a Security Code to change your password.",
        'url':reverse('forgot-password'),
        'suggestions':suggestions
    }
    return render(request,'front-end/send-security-code.html',data)


def changePassword(request):
    if request.method == 'POST':
        if not request.POST.get('email'):
            messages.info(request,"Email not found!",extra_tags='email-not-found')
            return redirect(request.META['HTTP_REFERER'])
        email = request.POST.get('email')
        if not request.POST.get('security_code'):
            messages.info(request,"Security code not found!",extra_tags='security-code-not-found')
            return redirect(request.META['HTTP_REFERER'])
        security_code = request.POST.get('security_code')
        acc = User.objects.filter(email=email).exists()
        if not acc:
            messages.info(request, "Account not found!", extra_tags='account-not-found')
            return redirect(request.META['HTTP_REFERER'])
        try:
            acc = User.objects.get(email=email)
            acc.is_active = True
            acc.save()
        except:
            messages.error(request,"Something went wrong",extra_tags='error')
            return redirect(request.META['HTTP_REFERER'])
        user = authenticate(request, email=email, password=security_code)
        if user:
            new_password = request.POST.get('new_password')
            retype_new_password = request.POST.get('retype_new_password')
            if new_password != retype_new_password:
                messages.info(request,"Passwords don't match!",extra_tags='password-mismatch')
                return redirect(request.META['HTTP_REFERER'])
            try:
                acc.set_password(new_password)
                acc.security_code = None
                acc.security_code_generated = False
                acc.save()
            except:
                messages.error(request,"Something went wrong!",extra_tags='error')
                return redirect(request.META['HTTP_REFERER'])
            user = authenticate(request, email=email, password=new_password)
            if user:
                login(request, user)
                return redirect('home')
            messages.info(request,"Authentication failed!",extra_tags='auth-failed')
            return redirect(request.META['HTTP_REFERER'])
        messages.info(request,"Couldn't authenticate!",extra_tags='could-not-authenticate')
        return redirect(request.META['HTTP_REFERER'])


def profile(request, user_id):
    user = User.objects.get(id=user_id)
    if_following = Followers.objects.filter(followed_id=user_id,follower_id=request.user.id).exists()
    if request.user.id == user_id:
        booklets = Booklet.objects.filter(user_id = user_id)
    else:
        booklets = Booklet.objects.filter(user_id = user_id, if_published=True)
    avg_rating = Rating.objects.filter(booklet_id__in=booklets).aggregate(avg=Avg('rating'))['avg']
    if request.user.is_authenticated and request.user.id==user_id and request.user.is_admin:
            user_count = User.objects.count()
            category_count = Category.objects.count()
            booklet_count = Booklet.objects.count()
            page_count = Page.objects.count()
            published_booklets = Booklet.objects.filter(if_published=True)
            published_page_count = Page.objects.filter(booklet_id__in=published_booklets).count()
            published_booklet_count = len(published_booklets)
            data = {
                'user':user,
                'if_following':if_following,
                'booklets':booklets,
                'avg_rating':avg_rating,
                'user_count':user_count,
                'category_count':category_count,
                'booklet_count':booklet_count,
                'page_count':page_count,
                'published_booklet_count':published_booklet_count,
                'published_page_count':published_page_count,
            }
    else:
        data = {
            'user':user,
            'if_following':if_following,
            'booklets':booklets,
            'avg_rating':avg_rating
        }
    return render(request, 'front-end/profile.html', data)


def follow(request):
    try:
        followed_id = request.GET.get('followed_id')
        if_already_following = Followers.objects.filter(followed_id=followed_id,follower_id=request.user.id).exists()
        if if_already_following:
            Followers.objects.get(followed_id=followed_id,follower_id=request.user.id).delete()
            return JsonResponse([200,'Follow'],safe=False)
        else:
            Followers.objects.create(followed_id=followed_id,follower_id=request.user.id)
            return JsonResponse([200,'Following'],safe=False)
    except Exception as e:
        return HttpResponse([500,e])
    

def updateProfile(request):
    try:
        if not request.POST.get('first_name'):
            return JsonResponse(['info',"First name is required"],safe=False)
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        user = User.objects.get(id = request.user.id)
        if len(request.FILES) > 0:
            profile_photo = request.FILES['profile_photo']
            extension = profile_photo.name.split('.')[-1]
            if extension != 'jpg' and extension != 'JPG' and extension != 'JPEG' and extension != 'jpeg' and extension != 'png' and extension != 'PNG':
                return JsonResponse(['error',"Image has to be of either JPEG/PNG format"],safe=False)
            elif profile_photo.size > settings.MAX_UPLOAD_LIMIT:
                return JsonResponse(['error',f"Image size cannot exceed {settings.MAX_UPLOAD_LIMIT/(1024*1024)} MB."],safe=False)
            profile_photo = getProcessedImage(request, profile_photo)
            user.profile_photo = profile_photo
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        return JsonResponse(['success',"Successfully updated profile"],safe=False)
    except:
        return JsonResponse(['error',"Something went wrong"],safe=False)
