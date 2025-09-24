from django.shortcuts import render, get_object_or_404
from .models import Movie, UserRating, SearchLog
from django.http import JsonResponse
from django.db.models import Q, Avg
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.contrib import messages
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import os

class MovieRecommendationService:
    def __init__(self):
        self.similarity_matrix = None
        self.movie_features = None
        self.vectorizer = None
        self.load_or_create_model()
    
    def load_or_create_model(self):
        """Load pre-computed similarity matrix or create new one"""
        model_path = 'movie_similarity_model.pkl'
        
        if os.path.exists(model_path):
            try:
                with open(model_path, 'rb') as f:
                    data = pickle.load(f)
                    self.similarity_matrix = data['similarity_matrix']
                    self.movie_features = data['movie_features']
                    self.vectorizer = data['vectorizer']
                print("Loaded pre-computed similarity matrix")
                return
            except:
                pass
        
        # Create new model
        self.create_similarity_matrix()
    
    def create_similarity_matrix(self):
        """Create similarity matrix from movie data"""
        movies = Movie.objects.all()
        if not movies.exists():
            return
        
        # Prepare features
        movie_data = []
        for movie in movies:
            # Combine features
            genres = ' '.join([g.get('name', '') for g in movie.genres])
            cast = ' '.join([c.get('name', '') for c in movie.cast[:5]])
            keywords = ' '.join([k.get('name', '') for k in movie.keywords[:10]])
            overview = movie.overview or ''
            
            combined_features = f"{genres} {cast} {keywords} {overview}"
            movie_data.append({
                'id': movie.id,
                'features': combined_features
            })
        
        if not movie_data:
            return
        
        df = pd.DataFrame(movie_data)
        
        # Create TF-IDF matrix
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            max_features=3000,
            ngram_range=(1, 2)
        )
        
        tfidf_matrix = self.vectorizer.fit_transform(df['features'])
        self.similarity_matrix = cosine_similarity(tfidf_matrix)
        self.movie_features = df
        
        # Save the model
        try:
            with open('movie_similarity_model.pkl', 'wb') as f:
                pickle.dump({
                    'similarity_matrix': self.similarity_matrix,
                    'movie_features': self.movie_features,
                    'vectorizer': self.vectorizer
                }, f)
            print("Similarity matrix created and saved")
        except:
            print("Could not save similarity matrix")
    
    def get_content_recommendations(self, movie_id, n_recommendations=10):
        """Get content-based recommendations"""
        if self.similarity_matrix is None or self.movie_features is None:
            return []
        
        try:
            movie_idx = self.movie_features[self.movie_features['id'] == movie_id].index[0]
        except IndexError:
            return []
        
        # Get similarity scores
        similarity_scores = list(enumerate(self.similarity_matrix[movie_idx]))
        similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
        
        # Get top similar movies (excluding the input movie)
        recommended_indices = [i for i, score in similarity_scores[1:n_recommendations+1]]
        recommended_movie_ids = [self.movie_features.iloc[i]['id'] for i in recommended_indices]
        
        return Movie.objects.filter(id__in=recommended_movie_ids)

# Initialize the recommendation service
recommendation_service = MovieRecommendationService()

def home(request):
    """Home page with popular movies"""
    popular_movies = Movie.objects.all()[:20]
    recent_movies = Movie.objects.filter(release_date__isnull=False).order_by('-release_date')[:10]
    top_rated = Movie.objects.filter(vote_count__gte=100).order_by('-vote_average')[:10]
    
    context = {
        'popular_movies': popular_movies,
        'recent_movies': recent_movies,
        'top_rated': top_rated,
    }
    return render(request, 'movies/home.html', context)

def search_movies(request):
    """Search movies by title, genre, or cast"""
    query = request.GET.get('q', '')
    movies = Movie.objects.none()
    
    if query:
        movies = Movie.objects.filter(
            Q(title__icontains=query) |
            Q(overview__icontains=query) |
            Q(genre_names__icontains=query) |
            Q(main_cast__icontains=query) |
            Q(director__icontains=query)
        ).distinct()
        
        # Log the search
        SearchLog.objects.create(
            query=query,
            user=request.user if request.user.is_authenticated else None,
            results_count=movies.count()
        )
    
    # Pagination
    paginator = Paginator(movies, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'query': query,
        'page_obj': page_obj,
        'total_results': movies.count()
    }
    return render(request, 'movies/search.html', context)

def movie_detail(request, movie_id):
    """Movie detail page with recommendations"""
    movie = get_object_or_404(Movie, id=movie_id)
    
    # Get content-based recommendations
    recommendations = recommendation_service.get_content_recommendations(movie_id, 8)
    
    # Get user rating if authenticated
    user_rating = None
    if request.user.is_authenticated:
        try:
            user_rating = UserRating.objects.get(user=request.user, movie=movie)
        except UserRating.DoesNotExist:
            pass
    
    context = {
        'movie': movie,
        'recommendations': recommendations,
        'user_rating': user_rating,
    }
    return render(request, 'movies/detail.html', context)

@login_required
@require_http_methods(["POST"])
def rate_movie(request, movie_id):
    """Rate a movie (AJAX endpoint)"""
    movie = get_object_or_404(Movie, id=movie_id)
    rating_value = int(request.POST.get('rating', 0))
    
    if rating_value < 1 or rating_value > 5:
        return JsonResponse({'error': 'Invalid rating'}, status=400)
    
    rating, created = UserRating.objects.update_or_create(
        user=request.user,
        movie=movie,
        defaults={'rating': rating_value}
    )
    
    action = 'created' if created else 'updated'
    return JsonResponse({
        'success': True,
        'action': action,
        'rating': rating_value
    })

def get_recommendations(request, movie_id):
    """API endpoint for getting recommendations"""
    movie = get_object_or_404(Movie, id=movie_id)
    recommendations = recommendation_service.get_content_recommendations(movie_id, 10)
    
    data = []
    for rec_movie in recommendations:
        data.append({
            'id': rec_movie.id,
            'title': rec_movie.title,
            'year': rec_movie.get_year(),
            'vote_average': rec_movie.vote_average,
            'genres': [g.get('name', '') for g in rec_movie.genres[:3]],
            'poster_url': f"https://image.tmdb.org/t/p/w500{rec_movie.poster_path}" if hasattr(rec_movie, 'poster_path') else None
        })
    
    return JsonResponse({
        'movie': movie.title,
        'recommendations': data
    })