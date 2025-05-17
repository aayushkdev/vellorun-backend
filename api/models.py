import random
from django.db import models
from django.contrib.auth.models import AbstractUser

AVATARS = ["avatar1", "avatar2", "avatar3"]

class CustomUser(AbstractUser):
    avatar = models.CharField(max_length=100, blank=True)
    xp = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    visible = models.BooleanField(default=True)

    @property
    def visited_places(self):
        return Place.objects.filter(visit__user=self).distinct()

    @property
    def contributed_places(self):
        return self.contributed_places.all()

    def save(self, *args, **kwargs):
        if not self.avatar:
            self.avatar = random.choice(AVATARS)
        super().save(*args, **kwargs)


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


# Add to models.py

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=20, default="🏠")  # Using emoji as default icon
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['order', 'name']
    
    def __str__(self):
        return f"{self.icon} {self.name}"


# Updated Place model with category field

class Place(models.Model):
    tags = models.ManyToManyField(Tag, related_name='places', blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='contributed_places')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='places', blank=True)

    TYPE_CHOICES = [
        ('inside', 'Inside'),
        ('outside', 'Outside'),
    ]

    name = models.CharField(max_length=255)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    description = models.TextField(blank=True)
    coord_x = models.FloatField()
    coord_y = models.FloatField()
    visits = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=0)
    xp_reward = models.IntegerField(default=10)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class PlaceImage(models.Model):
    place = models.ForeignKey(Place, related_name='images', on_delete=models.CASCADE)
    image_url = models.URLField() 

    def __str__(self):
        return f"Image for {self.place.name}"


class Visit(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    visited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'place')



class SuggestionType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name


class Suggestion(models.Model):
    TRIGGER_CHOICES = [
        ('time_based', 'Time Based'),
        ('level_up', 'Level Up'),
        ('new_place', 'New Place'),
        ('inactivity', 'Inactivity'),
        ('category', 'Category Based'),
    ]
    
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='suggestions')
    type = models.ForeignKey(SuggestionType, on_delete=models.SET_NULL, null=True, 
                            related_name='suggestions')
    message = models.CharField(max_length=255)
    trigger_type = models.CharField(max_length=20, choices=TRIGGER_CHOICES)
    min_user_level = models.IntegerField(default=1)
    priority = models.IntegerField(default=1)  # Higher number = higher priority
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.message} ({self.place.name})"


class UserSuggestion(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='suggestions')
    suggestion = models.ForeignKey(Suggestion, on_delete=models.CASCADE)
    is_shown = models.BooleanField(default=False)
    is_dismissed = models.BooleanField(default=False)
    is_followed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'suggestion')
    
    def __str__(self):
        return f"{self.user.username} - {self.suggestion.message}"


class PlaceSuggestion(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('implemented', 'Implemented'),
    ]
    
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=10, choices=Place.TYPE_CHOICES)
    description = models.TextField(blank=True)
    coord_x = models.FloatField()
    coord_y = models.FloatField()
    category = models.CharField(max_length=100, blank=True)
    suggested_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, 
                                    null=True, related_name='place_suggestions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} (suggested by {self.suggested_by.username if self.suggested_by else 'Anonymous'})"
    
    def convert_to_place(self):
        """Convert this suggestion to an actual Place"""
        place = Place(
            name=self.name,
            type=self.type,
            description=self.description,
            coord_x=self.coord_x,
            coord_y=self.coord_y,
            created_by=self.suggested_by,
            approved=True,
            level=0  # Default level, admin can change later
        )
        place.save()
        
        # Update this suggestion's status
        self.status = 'implemented'
        self.save()
        
        return place

