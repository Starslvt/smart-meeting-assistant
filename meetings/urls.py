from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload, name='upload'),
    path('meeting/<int:pk>/', views.detail, name='detail'),
    path('meeting/<int:pk>/processing/', views.processing, name='processing'),
    path('meeting/<int:pk>/process/', views.process_meeting, name='process_meeting'),
    path('meeting/<int:pk>/status/', views.check_status, name='check_status'),
]