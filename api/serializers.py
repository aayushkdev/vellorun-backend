from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser, Place, PlaceImage, Tag

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
        fields = ['username', 'email', 'avatar', 'xp', 'level', 'visible']
        read_only_fields = ['avatar', 'xp', 'level']


class PlaceImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaceImage
        fields = ['id', 'image_url']


class PlaceSerializer(serializers.ModelSerializer):
    images = PlaceImageSerializer(many=True, required=False)
    tags = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=False
    )

    class Meta:
        model = Place
        fields = ['id', 'name', 'type', 'description', 'coord_x', 'coord_y', 'visits', 'xp_reward', 'level', 'tags', 'images']
        read_only_fields = ['visits', 'approved']

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        images_data = validated_data.pop('images', [])
        place = Place.objects.create(**validated_data)

        for tag_name in tags_data:
            tag, _ = Tag.objects.get_or_create(name=tag_name.strip())
            place.tags.add(tag)

        for image_data in images_data:
            PlaceImage.objects.create(place=place, **image_data)

        return place

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data['tags'] = [tag.name for tag in instance.tags.all()]
        request = self.context.get('request')
        if request and request.user.is_superuser:
            data['approved'] = instance.approved
        return data


class VisitSerializer(serializers.Serializer):
    place_id = serializers.IntegerField()