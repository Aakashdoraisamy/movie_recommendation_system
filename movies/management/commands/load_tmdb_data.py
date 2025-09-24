
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_date
from movies.models import Movie
import pandas as pd
import ast
import json

class Command(BaseCommand):
    help = 'Load TMDB data from CSV files into Django models'
    
    def add_arguments(self, parser):
        parser.add_argument('--movies-csv', type=str, help='Path to movies CSV file')
        parser.add_argument('--credits-csv', type=str, help='Path to credits CSV file')
    
    def handle(self, *args, **options):
        movies_csv = options.get('movies_csv', 'tmdb_5000_movies.csv')
        credits_csv = options.get('credits_csv', 'tmdb_5000_credits.csv')
        
        try:
            # Load CSV files
            movies_df = pd.read_csv(movies_csv)
            credits_df = pd.read_csv(credits_csv)
            
            # Merge movies_df.id with credits_df.movie_id
            combined_df = movies_df.merge(credits_df, left_on='id', right_on='movie_id')
            
            self.stdout.write(f"Loading {len(combined_df)} movies...")
            
            for _, row in combined_df.iterrows():
                try:
                    # Parse complex fields
                    genres = self.safe_literal_eval(row['genres'])
                    cast = self.safe_literal_eval(row['cast'])
                    crew = self.safe_literal_eval(row['crew'])
                    keywords = self.safe_literal_eval(row.get('keywords', '[]'))
                    
                    # Extract director
                    director = ''
                    for crew_member in crew:
                        if crew_member.get('job') == 'Director':
                            director = crew_member.get('name', '')
                            break
                    
                    # Extract main cast names (ensure not None)
                    main_cast = ', '.join([str(c.get('name', '')) for c in cast if c.get('name')]) if cast else ''

                    # Extract genre names (ensure not None)
                    genre_names = ', '.join([str(g.get('name', '')) for g in genres if g.get('name')]) if genres else ''
                    
                    # Parse release date
                    release_date = None
                    if pd.notna(row.get('release_date')):
                        try:
                            release_date = parse_date(row['release_date'])
                        except:
                            pass
                    
                    # Create or update movie
                    movie, created = Movie.objects.update_or_create(
                        tmdb_id=int(row['id']),
                        defaults={
                            'title': row['title_x'],
                            'overview': row.get('overview', ''),
                            'release_date': release_date,
                            'runtime': int(row['runtime']) if pd.notna(row.get('runtime')) else None,
                            'vote_average': float(row.get('vote_average', 0)),
                            'vote_count': int(row.get('vote_count', 0)),
                            'popularity': float(row.get('popularity', 0)),
                            'genres': genres,
                            'cast': cast,
                            'crew': crew,
                            'keywords': keywords,
                            'director': director,
                            'main_cast': main_cast,
                            'genre_names': genre_names,
                        }
                    )
                    
                    if created:
                        self.stdout.write(f"✓ Created: {movie.title}")
                    else:
                        self.stdout.write(f"↻ Updated: {movie.title}")
                        
                except Exception as e:
                    self.stdout.write(f"❌ Error processing {row.get('title_x', 'Unknown')}: {str(e)}")
                    continue
            
            self.stdout.write(self.style.SUCCESS(f'Successfully loaded {Movie.objects.count()} movies'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
    
    def safe_literal_eval(self, val):
        """Safely evaluate string representations of Python literals"""
        try:
            return ast.literal_eval(val) if isinstance(val, str) else []
        except:
            return []