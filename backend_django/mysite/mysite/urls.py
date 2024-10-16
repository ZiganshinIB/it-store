"""
URL configuration for mysite project.

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
from django.template.defaulttags import url
from django.urls import path, re_path, include


from django.shortcuts import redirect
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

admin.site.site_header = "Админка IT Store"  # Заголовок на всех страницах админки
admin.site.site_title = "Админ панель"    # Заголовок в HTML
admin.site.index_title = "Работа с IT Store"   # Заголовок на главной странице админки


urlpatterns = [
    path('', lambda request: redirect('/admin/')),
    path('admin/', admin.site.urls),

    re_path(r'^auth/', include('djoser.urls.authtoken')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='docs'),
    path('api/v1/auth/', include('djoser.urls')),
    path('api/v1/tasker/', include('tasker.api_urls', namespace='api_tasker')),
    # re_path(r'^favicon.ico', RedirectView.as_view(url='/static/icon/favicon.ico', permanent=True)),
    # path('api/v1/person/', include('person.api_urls')),
]
