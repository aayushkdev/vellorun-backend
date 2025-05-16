import requests
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.db.models import Q
from .serializers import  GoogleAuthSerializer,RegisterSerializer,ProfileSerializer,PlaceImageSerializer,PlaceSerializer,VisitSerializer,UserSuggestionSerializer,SuggestionSerializer,SuggestionTypeSerializer,PlaceSuggestionSerializer,CategorySerializer
from .utils import IsSuperUserOrReadOnly, check_and_level_up
from .models import CustomUser, Place, PlaceImage, Tag,PlaceSuggestion,SuggestionType,Suggestion,UserSuggestion,Category,Visit

class GoogleAuthView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = GoogleAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        id_token = serializer.validated_data["id_token"]

        response = requests.get(f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}")
        if response.status_code != 200:
            return Response({"error": "Invalid Google ID token"}, status=400)

        payload = response.json()
        
        '''
        if payload["aud"] != settings.GOOGLE_CLIENT_ID:
            return Response({"error": "Invalid audience"}, status=400)
        '''

        email = payload["email"]
        username = payload.get("name", email.split("@")[0])

        user, created = CustomUser.objects.get_or_create(email=email, defaults={"username": username})
        if created:
            user.save()

        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        })


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class PlaceListCreateView(generics.ListCreateAPIView):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'type': ['exact'],
        'name': ['icontains'],
        'visits': ['exact', 'gte', 'lte'],
        'coord_x': ['exact'],
        'coord_y': ['exact'],
    }   

    def get_queryset(self):
        qs = Place.objects.all()
        if not self.request.user.is_superuser:
            qs = qs.filter(approved=True)

        tags = self.request.query_params.getlist('tags')
        if tags:
            qs = qs.filter(tags__name__in=tags).distinct()

        return qs

    def perform_create(self, serializer):
        if self.request.user.is_superuser:
            serializer.save(created_by=self.request.user, approved=True)
        else:
            serializer.save(created_by=self.request.user, approved=False)

class PlaceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    permission_classes = [IsSuperUserOrReadOnly]


class VisitPlaceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = VisitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        place_id = serializer.validated_data['place_id']
        place = get_object_or_404(Place, id=place_id)
        user = request.user

        visit, created = Visit.objects.get_or_create(user=user, place=place)

        if not created:
            return Response({
                "message": "You have already visited this place.",
                "place_name": place.name,
                "user_xp": user.xp,
                "user_level": user.level,
                "total_visits_to_place": place.visits,
            }, status=status.HTTP_200_OK)

        place.visits += 1
        user.xp += place.xp_reward
        place.save()
        check_and_level_up(user)
        user.save()

        return Response({
            "message": "Place visited!",
            "place_name": place.name,
            "user_xp": user.xp,
            "user_level": user.level,
            "total_visits_to_place": place.visits,
        }, status=status.HTTP_201_CREATED)


class ApprovePlaceView(APIView):
    permission_classes = [IsSuperUserOrReadOnly]

    def post(self, request, pk):
        try:
            place = Place.objects.get(pk=pk)
        except Place.DoesNotExist:
            return Response({'error': 'Place not found.'}, status=status.HTTP_404_NOT_FOUND)

        if place.approved:
            return Response({'message': 'Place is already approved.'}, status=status.HTTP_200_OK)

        place.approved = True
        place.save()

        return Response({'message': f'Place "{place.name}" has been approved.'}, status=status.HTTP_200_OK)


# Add to views.py

class SuggestionView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """
        Get personalized suggestions for the logged-in user.
        Returns a single active suggestion with highest priority that the user hasn't dismissed.
        """
        user = request.user
        
        # Get all places the user has already visited
        visited_place_ids = Visit.objects.filter(user=user).values_list('place_id', flat=True)
        
        # Find potential suggestions
        potential_suggestions = Suggestion.objects.filter(
            active=True,
            min_user_level__lte=user.level
        ).exclude(
            place_id__in=visited_place_ids
        ).exclude(
            usersuggestion__user=user,
            usersuggestion__is_dismissed=True
        ).order_by('-priority')
        
        if not potential_suggestions.exists():
            return Response({"message": "No suggestions available."}, status=status.HTTP_204_NO_CONTENT)
        
        # Get the highest priority suggestion
        suggestion = potential_suggestions.first()
        
        # Create or update UserSuggestion record
        user_suggestion, created = UserSuggestion.objects.get_or_create(
            user=user,
            suggestion=suggestion,
            defaults={'is_shown': True}
        )
        
        if not created:
            user_suggestion.is_shown = True
            user_suggestion.save()
        
        serializer = SuggestionSerializer(suggestion)
        return Response(serializer.data)
    
    def post(self, request):
        """
        Handle user interaction with a suggestion (dismiss or follow)
        """
        suggestion_id = request.data.get('suggestion_id')
        action = request.data.get('action')  # 'dismiss' or 'follow'
        
        if not suggestion_id or not action:
            return Response({
                "error": "suggestion_id and action are required."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if action not in ['dismiss', 'follow']:
            return Response({
                "error": "action must be either 'dismiss' or 'follow'."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user_suggestion = UserSuggestion.objects.get(
                user=request.user,
                suggestion_id=suggestion_id
            )
        except UserSuggestion.DoesNotExist:
            return Response({
                "error": "Suggestion not found or not associated with user."
            }, status=status.HTTP_404_NOT_FOUND)
        
        if action == 'dismiss':
            user_suggestion.is_dismissed = True
            user_suggestion.save()
            return Response({
                "message": "Suggestion dismissed successfully."
            })
        
        if action == 'follow':
            user_suggestion.is_followed = True
            user_suggestion.save()
            return Response({
                "message": "Suggestion followed successfully."
            })


# Trigger a suggestion when a place becomes available (level unlocked)
class SuggestionTriggerView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """
        Check for new suggestions based on user's current level
        """
        user = request.user
        
        # Get newly unlocked places based on user level
        newly_unlocked = Place.objects.filter(
            level__lte=user.level,
            approved=True
        ).exclude(
            visit__user=user
        )
        
        if not newly_unlocked.exists():
            return Response({"message": "No new places unlocked."}, 
                           status=status.HTTP_204_NO_CONTENT)
        
        # Get the top newly unlocked place to suggest
        place = newly_unlocked.order_by('level', '?').first()
        
        response_data = {
            "message": f"{place.name} unlocked! Plan your outing now!",
            "place": PlaceSerializer(place).data
        }
        
        return Response(response_data)


# Add to views.py

class PlaceSuggestionListCreateView(generics.ListCreateAPIView):
    serializer_class = PlaceSuggestionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'type', 'category']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return PlaceSuggestion.objects.all().order_by('-created_at')
        else:
            return PlaceSuggestion.objects.filter(suggested_by=user).order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(suggested_by=self.request.user)


class PlaceSuggestionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PlaceSuggestionSerializer
    lookup_field = 'pk'
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return PlaceSuggestion.objects.all()
        else:
            return PlaceSuggestion.objects.filter(suggested_by=user)
    
    def update(self, request, *args, **kwargs):
        # Only allow superusers to update status and admin_notes
        if not request.user.is_superuser:
            for field in ['status', 'admin_notes']:
                if field in request.data:
                    return Response(
                        {"error": f"You don't have permission to update {field}."},
                        status=status.HTTP_403_FORBIDDEN
                    )
        return super().update(request, *args, **kwargs)


class ProcessPlaceSuggestionView(APIView):
    permission_classes = [IsSuperUserOrReadOnly]
    
    def post(self, request, pk):
        try:
            suggestion = PlaceSuggestion.objects.get(pk=pk)
        except PlaceSuggestion.DoesNotExist:
            return Response({'error': 'Place suggestion not found.'}, 
                           status=status.HTTP_404_NOT_FOUND)
        
        action = request.data.get('action')
        if action not in ['approve', 'reject', 'implement']:
            return Response({
                'error': 'Invalid action. Must be "approve", "reject", or "implement".'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        notes = request.data.get('admin_notes', '')
        
        if action == 'approve':
            suggestion.status = 'approved'
            suggestion.admin_notes = notes
            suggestion.save()
            return Response({
                'message': f'Place suggestion "{suggestion.name}" has been approved.'
            })
        
        elif action == 'reject':
            suggestion.status = 'rejected'
            suggestion.admin_notes = notes
            suggestion.save()
            return Response({
                'message': f'Place suggestion "{suggestion.name}" has been rejected.'
            })
        
        elif action == 'implement':
            try:
                place = suggestion.convert_to_place()
                return Response({
                    'message': f'Place suggestion "{suggestion.name}" has been implemented.',
                    'place_id': place.id
                })
            except Exception as e:
                return Response({
                    'error': f'Failed to implement suggestion: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            


# Add to views.py

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all().order_by('order', 'name')
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class CategoryDetailView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class CategoryPlacesView(generics.ListAPIView):
    """List all places in a specific category"""
    serializer_class = PlaceSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        category_id = self.kwargs.get('pk')
        qs = Place.objects.filter(category_id=category_id, approved=True)
        
        # Filter by user level if user is authenticated
        if self.request.user.is_authenticated:
            user_level = self.request.user.level
            qs = qs.filter(level__lte=user_level)
        else:
            # For non-authenticated users, only show level 0 places
            qs = qs.filter(level=0)
        
        return qs


class SuggestPlacesByCategoryView(APIView):
    """Suggest places based on category"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        category_id = request.data.get('category_id')
        if not category_id:
            return Response({
                "error": "category_id is required."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response({
                "error": "Category not found."
            }, status=status.HTTP_404_NOT_FOUND)
        
        user = request.user
        
        # Get places the user has already visited
        visited_place_ids = Visit.objects.filter(user=user).values_list('place_id', flat=True)
        
        # Find places in the category that the user hasn't visited yet
        # and are appropriate for their level
        places = Place.objects.filter(
            category=category,
            approved=True,
            level__lte=user.level
        ).exclude(
            id__in=visited_place_ids
        ).order_by('?')[:3]  # Get up to 3 random suggestions
        
        if not places.exists():
            return Response({
                "message": f"You've already visited all available places in {category.name} category!"
            }, status=status.HTTP_200_OK)
        
        serializer = PlaceSerializer(places, many=True)
        return Response({
            "category": CategorySerializer(category).data,
            "suggested_places": serializer.data
        })