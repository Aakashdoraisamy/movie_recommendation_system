from django.db import models
from django.contrib.auth.models import User
import json

class Movie(models.Model):
    tmdb_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=255)
    overview = models.TextField()
    release_date = models.DateField(null=True, blank=True)
    runtime = models.IntegerField(null=True, blank=True)
    vote_average = models.FloatField(default=0.0)
    vote_count = models.IntegerField(default=0)
    popularity = models.FloatField(default=0.0)
    
    # JSON fields for complex data
    genres = models.JSONField(default=list)
    cast = models.JSONField(default=list)
    crew = models.JSONField(default=list)
    keywords = models.JSONField(default=list)
    
    # Computed fields
    director = models.CharField(max_length=255, blank=True)
    main_cast = models.CharField(max_length=500, blank=True)
    genre_names = models.CharField(max_length=500, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-popularity']
        
    def __str__(self):
        return self.title
    
    def get_year(self):
        if self.release_date:
            return self.release_date.year
        return None

class UserRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 stars
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'movie')
        
    def __str__(self):
        return f"{self.user.username} - {self.movie.title}: {self.rating}/5"

class SearchLog(models.Model):
    query = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    results_count = models.IntegerField(default=0)