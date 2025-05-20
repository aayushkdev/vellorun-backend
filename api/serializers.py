from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser, Place, SavedPlace

class GoogleAuthSerializer(serializers.Serializer):
    id_token = serializers.CharField()

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'avatar', 'xp', 'level', 'visible']
        read_only_fields = ['avatar', 'xp', 'level']

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'avatar', 'badges', 'xp', 'level', 'visible', 'online', 'coord_x', 'coord_y']
        read_only_fields = ['username', 'xp', 'level', 'badges']


class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = ['id', 'name', 'type', 'description', 'category', 'coord_x', 'coord_y', 'visits', 'xp_reward', 'level']
        read_only_fields = ['visits', 'approved']


    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        if request and request.user.is_superuser:
            data['approved'] = instance.approved
        return data


class VisitSerializer(serializers.Serializer):
    place_id = serializers.IntegerField()


class SavedPlaceSerializer(serializers.ModelSerializer):
    place = PlaceSerializer(read_only=True)
    place_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = SavedPlace
        fields = ['place', 'place_id', 'saved_at'] 


class SuggestedPlaceSerializer(serializers.Serializer):
    suggestions = serializers.CharField()