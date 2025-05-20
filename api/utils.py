from rest_framework import permissions
from .models import Place

def check_and_level_up(user):
    if user.xp%100 == 0:
        user.level += 1
    user.save()


class IsSuperUserOrReadOnly(permissions.BasePermission):
    """
    Custom permission:
    - Allow GET, HEAD, OPTIONS for everyone
    - Only allow POST, PUT, PATCH, DELETE if user is superuser
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True 
        return request.user and request.user.is_authenticated and request.user.is_superuser


def update_user_badges(user):
    visited_places = Place.objects.filter(visit__user=user)
    place_description = {place.description.lower() for place in visited_places}
    categories = {place.category.lower() for place in visited_places if place.category}
    badges = []

    if "library" in place_description or any("academic" in name for name in place_description):
        badges.append("nerd")

    if "food" in categories:
        badges.append("foodie")

    if "rnr" in place_description or "arcade" in place_description:
        badges.append("gamer")

    if "fitness" in categories:
        badges.append("jock")

    if any("hostel" in name for name in place_description) and categories == {"campus"}:
        badges.append("sleepyhead")

    user.badges = list(set(badges))
    user.save()
