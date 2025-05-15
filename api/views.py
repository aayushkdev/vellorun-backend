from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import RegisterSerializer, ProfileSerializer, PlaceSerializer, VisitSerializer
from .utils import IsSuperUserOrReadOnly, check_and_level_up
from .models import CustomUser, Place, Visit
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404


class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


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
        return qs

    def perform_create(self, serializer):
        if self.request.user.is_superuser:
            serializer.save(approved=True)
        else:
            serializer.save(approved=False)


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
