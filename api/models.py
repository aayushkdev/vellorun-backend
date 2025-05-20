from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    username = models.CharField(max_length=150, blank=True, null=True, unique=False)
    email = models.EmailField(unique=True)

    avatar = models.IntegerField(blank=True, null=True)
    xp = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    visible = models.BooleanField(default=True)
    online = models.BooleanField(default=True)
    coord_x = models.FloatField(default=0)
    coord_y = models.FloatField(default=0)
    badges = models.JSONField(default=list, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


class Place(models.Model):
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='contributed_places')

    TYPE_CHOICES = [
        ('inside', 'Inside'),
        ('outside', 'Outside'),
    ]

    name = models.CharField(max_length=255)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=69, default="campus")
    coord_x = models.FloatField()
    coord_y = models.FloatField()
    visits = models.PositiveIntegerField(default=0)
    level = models.PositiveIntegerField(default=1)
    xp_reward = models.IntegerField(default=20)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Visit(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    place = models.ForeignKey(Place, on_delete=models.CASCADE)
    visited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'place')


class SavedPlace(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='saved_places')
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='saved_by')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'place')