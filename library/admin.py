from django.contrib import admin
from .models import Book

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    # FIX: Changed 'total_pages' to 'pages' and added 'genre'
    list_display = ('title', 'author', 'pages', 'genre')
    search_fields = ('title', 'author')