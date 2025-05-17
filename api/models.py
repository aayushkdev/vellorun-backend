import random
from django.db import models
from django.contrib.auth.models import AbstractUser

AVATARS = ["avatar1", "avatar2", "avatar3", "avatar4"]

class CustomUser(AbstractUser):
    avatar = models.CharField(max_length=100, blank=True)
    xp = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    visible = models.BooleanField(default=True)
    coord_x = models.FloatField(default=0)
    coord_y = models.FloatField(default=0)

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


class Place(models.Model):
    tags = models.ManyToManyField(Tag, related_name='places', blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='contributed_places')

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


class SavedPlace(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='saved_places')
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='saved_by')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'place')