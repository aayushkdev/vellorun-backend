# Update admin.py

from django.contrib import admin
from .models import (
    CustomUser, Place, PlaceImage, Visit, Tag, 
    Category, SuggestionType, Suggestion, UserSuggestion, PlaceSuggestion
)

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'level', 'xp', 'visible')
    search_fields = ('username', 'email')
    list_filter = ('level', 'visible')

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'category', 'visits', 'level', 'xp_reward', 'approved')
    list_filter = ('type', 'approved', 'level', 'category')
    search_fields = ('name', 'description')
    filter_horizontal = ('tags',)

@admin.register(PlaceImage)
class PlaceImageAdmin(admin.ModelAdmin):
    list_display = ('place', 'image_url')
    search_fields = ('place__name',)

@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ('user', 'place', 'visited_at')
    list_filter = ('visited_at',)
    search_fields = ('user__username', 'place__name')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'order')
    search_fields = ('name', 'description')
    list_editable = ('icon', 'order')

@admin.register(SuggestionType)
class SuggestionTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')

@admin.register(Suggestion)
class SuggestionAdmin(admin.ModelAdmin):
    list_display = ('message', 'place', 'type', 'trigger_type', 'min_user_level', 'priority', 'active')
    list_filter = ('trigger_type', 'type', 'active', 'min_user_level')
    search_fields = ('message', 'place__name')
    list_editable = ('priority', 'active')

@admin.register(UserSuggestion)
class UserSuggestionAdmin(admin.ModelAdmin):
    list_display = ('user', 'suggestion', 'is_shown', 'is_dismissed', 'is_followed', 'created_at')
    list_filter = ('is_shown', 'is_dismissed', 'is_followed', 'created_at')
    search_fields = ('user__username', 'suggestion__message')

@admin.register(PlaceSuggestion)
class PlaceSuggestionAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'category', 'status', 'suggested_by', 'created_at')
    list_filter = ('status', 'type', 'created_at')
    search_fields = ('name', 'description', 'suggested_by__username')
    list_editable = ('status',)
    readonly_fields = ('suggested_by', 'created_at')