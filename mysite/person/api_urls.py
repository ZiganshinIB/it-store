from django.conf import settings
from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy
from django.shortcuts import render
from django.contrib import admin

app_name = "person"

urlpatterns = [
    # path('login/',
    #      auth_views.LoginView.as_view(
    #          template_name='registration/login.html'),
    #      name='login'),
    # path('logout/', auth_views.LogoutView.as_view(), name='logout'),

]

