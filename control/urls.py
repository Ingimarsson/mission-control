"""control URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='login.html')),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login')),
    path('', views.dashboard),
    path('data/', views.data),
    path('tracks/', views.tracks),
    path('accumulator/', views.accumulator),
    path('sensors/', views.sensors),
    path('data/get/<int:id>', views.data_get),
    path('api/track/<int:id>', views.api_track),
    path('api/track/edit/<int:id>', views.api_track_edit),
    path('api/track/add', views.api_track_add),
    path('api/recording/start', views.api_recording_start),
    path('api/recording/stop', views.api_recording_stop),
    path('api/sensors/upload', views.api_sensors_upload)
]
