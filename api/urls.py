from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import GoogleAuthView, ProfileView, PlaceListCreateView, PlaceDetailView, VisitPlaceView, ApprovePlaceView, SavedPlaceView

urlpatterns = [
    path('auth/google/', GoogleAuthView.as_view(), name='google-auth'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('user/profile/', ProfileView.as_view(), name='user-profile'),
    path('places/', PlaceListCreateView.as_view(), name='place-list-create'),
    path('places/<int:pk>/', PlaceDetailView.as_view(), name='place-detail'),
    path('visit/', VisitPlaceView.as_view(), name='visit-place'),
    path('places/<int:pk>/approve/', ApprovePlaceView.as_view(), name='approve-place'),
    path('saved/', SavedPlaceView.as_view(), name='saved-places'),
]
