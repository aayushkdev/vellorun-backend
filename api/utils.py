from rest_framework import permissions

def check_and_level_up(user):
    level_thresholds = [0, 100, 300, 600, 1000]
    while user.level < len(level_thresholds) and user.xp >= level_thresholds[user.level]:
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