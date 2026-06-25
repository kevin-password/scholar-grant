from django.db import models

class Book(models.Model):
    """Represents a book fetched from the Open Library API."""
    open_library_id = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True)
    cover_url = models.URLField(blank=True, help_text="Link to the book cover image")
    summary = models.TextField(blank=True)
    total_pages = models.IntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title