import random
import requests
from django.core.management.base import BaseCommand
from library.models import Book

class Command(BaseCommand):
    help = 'Fetches books from the Open Library API and saves them to the database'

    def add_arguments(self, parser):
        # Make the query optional (nargs='?')
        parser.add_argument('query', nargs='?', type=str, default=None, help='Search query (optional). If empty, fetches random subjects.')

    def handle(self, *args, **kwargs):
        query = kwargs['query']
        
        # If no query is provided, pick a random subject!
        if not query:
            subjects = ['fantasy', 'science_fiction', 'history', 'biography', 'mystery', 'adventure', 'poetry', 'art', 'philosophy', 'travel', 'cooking', 'sports', 'technology', 'nature']
            query = random.choice(subjects)
            self.stdout.write(f"🎲 No query provided. Fetching random subject: '{query}'...")
            url = f"https://openlibrary.org/search.json?subject={query}&limit=15"
        else:
            self.stdout.write(f"🔍 Searching Open Library for '{query}'...")
            url = f"https://openlibrary.org/search.json?q={query}&limit=15"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            books_added = 0
            for doc in data.get('docs', []):
                cover_id = doc.get('cover_i')
                cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg" if cover_id else ""
                
                authors = doc.get('author_name', [])
                author = authors[0] if authors else "Unknown Author"
                
                # Safely grab the summary
                first_sentence = doc.get('first_sentence', [])
                if first_sentence and isinstance(first_sentence[0], dict):
                    summary = first_sentence[0].get('value', 'No summary available.')
                elif first_sentence:
                    summary = str(first_sentence[0])
                else:
                    summary = "Dive into this amazing book and explore new worlds!"
                
                book, created = Book.objects.update_or_create(
                    open_library_id=doc['key'],
                    defaults={
                        'title': doc.get('title', 'Unknown Title'),
                        'author': author,
                        'cover_url': cover_url,
                        'summary': summary,
                        'total_pages': doc.get('number_of_pages_median', 100)
                    }
                )
                if created:
                    books_added += 1
                    
            self.stdout.write(self.style.SUCCESS(f'✅ Successfully added/updated {books_added} books!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error fetching books: {e}'))