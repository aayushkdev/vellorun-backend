from django.db import models
from django.contrib.auth.models import AbstractUser
import random

AVATARS = ["avatar1", "avatar2", "avatar3"]

class CustomUser(AbstractUser):
    avatar = models.CharField(max_length=100, blank=True)
    xp = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    visible = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.avatar:
            self.avatar = random.choice(AVATARS)
        super().save(*args, **kwargs)


class Place(models.Model):
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
