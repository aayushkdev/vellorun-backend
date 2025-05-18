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
from .serializers import RegisterSerializer, ProfileSerializer, PlaceSerializer, VisitSerializer, GoogleAuthSerializer, SavedPlaceSerializer
from .utils import IsSuperUserOrReadOnly, check_and_level_up
from .models import CustomUser, Place, Visit, SavedPlace

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


class SavedPlaceView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        saved = SavedPlace.objects.filter(user=request.user)
        serializer = SavedPlaceSerializer(saved, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        serializer = SavedPlaceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        place_id = serializer.validated_data['place_id']
        place = get_object_or_404(Place, id=place_id)
        saved_place, created = SavedPlace.objects.get_or_create(user=request.user, place=place)

        if not created:
            return Response({'message': 'Place already saved.'}, status=200)

        return Response({'message': 'Place saved successfully.'}, status=201)

    def delete(self, request):
        place_id = request.data.get('place_id')
        if not place_id:
            return Response({'error': 'place_id is required.'}, status=400)

        try:
            saved = SavedPlace.objects.get(user=request.user, place_id=place_id)
            saved.delete()
            return Response({'message': 'Place removed from saved list.'}, status=200)
        except SavedPlace.DoesNotExist:
            return Response({'error': 'Place not found in your saved list.'}, status=404)


class VisibleUsersView(generics.ListAPIView):
    serializer_class = ProfileSerializer

    def get_queryset(self):
        return CustomUser.objects.filter(online=True)