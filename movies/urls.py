# movies/urls.py
from django.urls import path
from . import views

app_name = 'movies'

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search_movies, name='search'),
    path('movie/<int:movie_id>/', views.movie_detail, name='detail'),
    path('movie/<int:movie_id>/rate/', views.rate_movie, name='rate'),
    path('api/recommendations/<int:movie_id>/', views.get_recommendations, name='api_recommendations'),
]