from rest_framework import permissions

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
