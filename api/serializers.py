from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser, Place, PlaceImage, Tag,PlaceSuggestion,SuggestionType,Suggestion,UserSuggestion,Category
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
    visited_places = serializers.SerializerMethodField()
    contributed_places = serializers.SerializerMethodField()
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'avatar', 'xp', 'level', 'visible', 'visited_places', 'contributed_places']
        read_only_fields = ['avatar', 'xp', 'level', 'visited_places', 'contributed_places']
    
    def get_visited_places(self, user):
        places = Place.objects.filter(visit__user=user).distinct()
        return PlaceSerializer(places, many=True, context=self.context).data

    def get_contributed_places(self, user):
        places = Place.objects.filter(created_by=user)
        return PlaceSerializer(places, many=True, context=self.context).data



class PlaceImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaceImage
        fields = ['id', 'image_url']


class PlaceSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all(), required=False)
    created_by_username = serializers.ReadOnlyField(source='created_by.username')
    category_name = serializers.ReadOnlyField(source='category.name', default=None)
    category_icon = serializers.ReadOnlyField(source='category.icon', default=None)
    
   
    images = PlaceImageSerializer(many=True, required=False)
    tags = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=False
    )

    class Meta:
        model = Place
        fields = ['id', 'name', 'type', 'description', 'coord_x', 'coord_y', 
                  'visits', 'level', 'xp_reward', 'approved', 'tags', 
                  'created_by', 'created_by_username', 'category', 
                  'category_name', 'category_icon']
        read_only_fields = ['visits', 'approved', 'created_by']

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


#commits:-
# Add to serializers.py

class SuggestionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuggestionType
        fields = '__all__'


class SuggestionSerializer(serializers.ModelSerializer):
    place_name = serializers.CharField(source='place.name', read_only=True)
    type_name = serializers.CharField(source='type.name', read_only=True)
    
    class Meta:
        model = Suggestion
        fields = ['id', 'place', 'place_name', 'type', 'type_name', 'message', 
                  'trigger_type', 'min_user_level', 'priority', 'active']


class UserSuggestionSerializer(serializers.ModelSerializer):
    suggestion_details = SuggestionSerializer(source='suggestion', read_only=True)
    
    class Meta:
        model = UserSuggestion
        fields = ['id', 'suggestion', 'suggestion_details', 'is_shown', 
                  'is_dismissed', 'is_followed', 'created_at']
        read_only_fields = ['user', 'created_at']



# Add to serializers.py

class PlaceSuggestionSerializer(serializers.ModelSerializer):
    suggested_by_username = serializers.CharField(source='suggested_by.username', read_only=True)
    
    class Meta:
        model = PlaceSuggestion
        fields = ['id', 'name', 'type', 'description', 'coord_x', 'coord_y', 
                  'category', 'suggested_by', 'suggested_by_username', 'status', 
                  'admin_notes', 'created_at', 'updated_at']
        read_only_fields = ['suggested_by', 'status', 'admin_notes', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        validated_data['suggested_by'] = self.context['request'].user
        return super().create(validated_data)


# Add to serializers.py

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'icon', 'description', 'order']

# Update PlaceSerializer to include category


#RegisterSerializer,ProfileSerializer,PlaceImageSerializer,PlaceSerializer,VisitSerializer,UserSuggestionSerializer,SuggestionSerializer,SuggestionTypeSerializer,PlaceSuggestionSerializer,CategorySerializer,PlaceSerializer