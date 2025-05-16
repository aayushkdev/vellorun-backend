# api/management/commands/load_initial_data.py
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Load initial categories and suggestions'

    def handle(self, *args, **kwargs):
        from api.models import Category, SuggestionType, Suggestion, Place

        # Step 3: Add Categories
        categories = [
            {"name": "Food", "icon": "🍕", "description": "Places to eat and drink", "order": 1},
            {"name": "Campus Building", "icon": "🏛️", "description": "Academic and administrative buildings", "order": 2},
            {"name": "Shops", "icon": "🛍️", "description": "Places to shop", "order": 3},
            {"name": "Hangout spots", "icon": "🧘", "description": "Places to relax and socialize", "order": 4},
            {"name": "Study Spots", "icon": "📚", "description": "Quiet places to study", "order": 5},
            {"name": "Sports", "icon": "🏐", "description": "Sports facilities and recreation areas", "order": 6},
        ]

        for cat in categories:
            Category.objects.get_or_create(name=cat["name"], defaults={
                "icon": cat["icon"],
                "description": cat["description"],
                "order": cat["order"]
            })

        # Step 4: Add SuggestionTypes
        suggestion_types = [
            {"name": "New Place", "description": "Suggests places newly added to the map"},
            {"name": "Level Up", "description": "Suggests places newly unlocked after leveling up"},
            {"name": "Exploration", "description": "Suggests random places to explore"},
            {"name": "Category", "description": "Suggests places from a specific category"},
        ]

        for st in suggestion_types:
            SuggestionType.objects.get_or_create(name=st["name"], defaults={
                "description": st["description"]
            })

        self.stdout.write(self.style.SUCCESS("✅ Initial categories and suggestion types loaded."))
