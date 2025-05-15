from rest_framework import serializers
from .models import CustomUser, Place, PlaceImage
from django.contrib.auth.password_validation import validate_password

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'avatar', 'xp', 'level', 'visible']
        read_only_fields = ['avatar', 'xp', 'level', 'visible']

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
        fields = ['username', 'email', 'avatar', 'xp', 'level', 'visible']


class PlaceImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaceImage
        fields = ['id', 'image_url']


class PlaceSerializer(serializers.ModelSerializer):
    images = PlaceImageSerializer(many=True, read_only=True)

    class Meta:
        model = Place
        fields = ['id', 'name', 'type', 'description', 'coord_x', 'coord_y', 'visits', 'level', 'images']


class VisitSerializer(serializers.Serializer):
    place_id = serializers.IntegerField()

    def validate_place_id(self, value):
        if not Place.objects.filter(id=value).exists():
            raise serializers.ValidationError("Place does not exist.")
        return value
