from django.contrib import admin

from .models import Category, Location, Post

admin.site.empty_value_display = 'Не задано'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_published', 'created_at')
    list_filter = ('is_published',)
    search_fields = ('title',)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_published', 'created_at')
    list_filter = ('is_published',)
    search_fields = ('name',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'author', 'pub_date', 'is_published', 'created_at'
    )
    list_filter = ('is_published', 'category', 'location', 'author')
    search_fields = ('title', 'text', 'author__username')
    date_hierarchy = 'pub_date'
