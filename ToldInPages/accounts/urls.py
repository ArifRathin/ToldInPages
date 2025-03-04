from django.urls import path
from . import views

urlpatterns = [
    path('create-super-user', views.createSuperUser, name='create-super-user'),
    path('sign-up', views.signUp, name='sign-up'),
    path('show-verify-page', views.showVerifyPage, name='show-verify-page'),
    path('account-verification', views.accountVerification, name='account-verification'),
    path('verify-account', views.verifyAccount, name='verify-account'),
    path('log-in', views.logIn, name='log-in'),
    path('log-out', views.logOut, name='log-out'),
    path('profile/<int:user_id>', views.profile, name='profile'),
    path('follow', views.follow, name='follow'),
    path('update-profile', views.updateProfile, name='update-profile'),
    path('forgot-password', views.forgotPassword, name='forgot-password'),
    path('change-password', views.changePassword, name='change-password')
]