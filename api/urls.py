# Updated urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    GoogleAuthView, ProfileView, PlaceListCreateView, PlaceDetailView, 
    VisitPlaceView, ApprovePlaceView, SuggestionView, SuggestionTriggerView,
    PlaceSuggestionListCreateView, PlaceSuggestionDetailView, ProcessPlaceSuggestionView,
    CategoryListView, CategoryDetailView, CategoryPlacesView, SuggestPlacesByCategoryView
)

urlpatterns = [
    # Authentication
    path('auth/google/', GoogleAuthView.as_view(), name='google-auth'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User Profile
    path('user/profile/', ProfileView.as_view(), name='user-profile'),
    
    # Places
    path('places/', PlaceListCreateView.as_view(), name='place-list-create'),
    path('places/<int:pk>/', PlaceDetailView.as_view(), name='place-detail'),
    path('places/<int:pk>/approve/', ApprovePlaceView.as_view(), name='approve-place'),
    path('visit/', VisitPlaceView.as_view(), name='visit-place'),
    
    # Suggestion Buddy
    path('suggestions/', SuggestionView.as_view(), name='suggestion-list'),
    path('suggestions/trigger/', SuggestionTriggerView.as_view(), name='suggestion-trigger'),
    
    # Place Suggestions (User Contributions)
    path('place-suggestions/', PlaceSuggestionListCreateView.as_view(), name='place-suggestion-list'),
    path('place-suggestions/<int:pk>/', PlaceSuggestionDetailView.as_view(), name='place-suggestion-detail'),
    path('place-suggestions/<int:pk>/process/', ProcessPlaceSuggestionView.as_view(), name='process-place-suggestion'),
    
    # Categories
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    path('categories/<int:pk>/places/', CategoryPlacesView.as_view(), name='category-places'),
    path('suggest-by-category/', SuggestPlacesByCategoryView.as_view(), name='suggest-by-category'),
]