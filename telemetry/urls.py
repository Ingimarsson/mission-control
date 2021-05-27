"""Telemetry app URL Configuration

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
from django.urls import path, include
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.track),
    path('track/', views.track, name='track_page'),
    path('api/track/<int:id>', views.api_track),
    path('api/track/edit/<int:id>', views.api_track_edit),
    path('api/track/add', views.api_track_add),
    path('settings/track/', views.settings_track, name='settings_track_page'),
    path('api/settings_track/<int:id>', views.api_settings_track),
    path('sensors/', views.sensors, name='sensor_page'),
    path('api/sensors/upload', views.api_sensors_upload)
]
