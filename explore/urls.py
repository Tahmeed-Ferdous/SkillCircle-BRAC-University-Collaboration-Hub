from django.urls import path
from . import views

app_name = 'explore'

urlpatterns = [
    path('', views.explore, name='explore_page'),  # Updated to use 'explore' view
]
