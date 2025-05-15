from django.urls import path
from .views import RegisterView, ProfileView, PlaceListCreateView, PlaceDetailView, VisitPlaceView, ApprovePlaceView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/profile/', ProfileView.as_view(), name='user-profile'),
    path('places/', PlaceListCreateView.as_view(), name='place-list-create'),
    path('places/<int:pk>/', PlaceDetailView.as_view(), name='place-detail'),
    path('visit/', VisitPlaceView.as_view(), name='visit-place'),
    path('places/<int:pk>/approve/', ApprovePlaceView.as_view(), name='approve-place'),
]
