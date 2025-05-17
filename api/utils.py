from django.contrib.auth import get_user_model
from rest_framework import permissions
def check_and_level_up(user):
    if user.xp%10 == 0:
        user.level += 1
    user.save()


    
# Updated utils.py



class IsSuperUserOrReadOnly(permissions.BasePermission):
    """
    Allows read access to everyone, but only allows write access to superusers.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_superuser

def check_and_level_up(user):
    """Check if user should level up based on XP and trigger suggestions if needed"""
    # Define the XP thresholds for each level
    level_thresholds = {
        1: 0,      # Level 1 starts at 0 XP
        2: 100,    # Level 2 requires 100 XP
        3: 300,    # Level 3 requires 300 XP
        4: 600,    # and so on...
        5: 1000,
        6: 1500,
        7: 2100,
        8: 2800,
        9: 3600,
        10: 4500,
    }
    
    # Check if user should level up
    current_level = user.level
    max_level = max(level_thresholds.keys())
    
    # Cap the level at max_level
    if current_level >= max_level:
        return False
    
    # Check if user has enough XP for next level
    next_level = current_level + 1
    if next_level in level_thresholds and user.xp >= level_thresholds[next_level]:
        user.level = next_level
        user.save()
        
        # Trigger level-up suggestions
        from .models import Suggestion, UserSuggestion, Place
        
        # Get newly unlocked places based on user's new level
        newly_unlocked_places = Place.objects.filter(
            level=user.level,
            approved=True
        )
        
        # Create user suggestions for these places
        for place in newly_unlocked_places:
            suggestions = Suggestion.objects.filter(
                place=place,
                trigger_type='level_up',
                min_user_level__lte=user.level,
                active=True
            )
            
            if not suggestions.exists():
                # Create a default suggestion if none exists
                from .models import SuggestionType
                level_up_type, _ = SuggestionType.objects.get_or_create(
                    name="Level Up",
                    defaults={"description": "Suggests places newly unlocked after leveling up"}
                )
                
                suggestion = Suggestion.objects.create(
                    place=place,
                    type=level_up_type,
                    message=f"{place.name} unlocked! Plan your outing now!",
                    trigger_type='level_up',
                    min_user_level=user.level,
                    priority=5,
                    active=True
                )
                
                UserSuggestion.objects.create(
                    user=user,
                    suggestion=suggestion,
                    is_shown=False
                )
            else:
                # Use existing suggestions
                for suggestion in suggestions:
                    UserSuggestion.objects.get_or_create(
                        user=user,
                        suggestion=suggestion,
                        defaults={'is_shown': False}
                    )
        
        return True
        
    return False

def generate_suggestions_for_user(user):
    """Generate personalized suggestions for a user"""
    from .models import Place, Visit, Suggestion, UserSuggestion, SuggestionType
    
    # Get places the user hasn't visited yet
    visited_place_ids = Visit.objects.filter(user=user).values_list('place_id', flat=True)
    unvisited_places = Place.objects.filter(
        approved=True,
        level__lte=user.level
    ).exclude(
        id__in=visited_place_ids
    )
    
    if not unvisited_places.exists():
        return None
    
    # Get or create the exploration suggestion type
    exploration_type, _ = SuggestionType.objects.get_or_create(
        name="Exploration",
        defaults={"description": "Suggests random places to explore"}
    )
    
    # Get a random unvisited place for suggestion
    import random
    place = random.choice(unvisited_places)
    
    # Create a suggestion for this place if it doesn't exist
    suggestion, created = Suggestion.objects.get_or_create(
        place=place,
        type=exploration_type,
        trigger_type='inactivity',
        defaults={
            'message': f"You haven't checked out {place.name} yet. Wanna go there?",
            'min_user_level': place.level,
            'priority': 3,
            'active': True
        }
    )
    
    # Create a user suggestion
    user_suggestion, _ = UserSuggestion.objects.get_or_create(
        user=user,
        suggestion=suggestion,
        defaults={'is_shown': False}
    )
    
    return user_suggestion