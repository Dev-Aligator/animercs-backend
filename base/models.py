from operator import mod
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.

class Anime(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    title = models.CharField(max_length=120, blank=False, null=False)
    synopsis = models.CharField(max_length=2750, blank=True, null=True)
    genre = models.CharField(max_length=160, blank=True, null=True)
    aired = models.CharField(max_length=30, blank=True, null=True)
    episodes = models.PositiveSmallIntegerField(blank=True, null=True)
    popularity = models.PositiveSmallIntegerField(blank=True, null=True)
    ranked = models.PositiveSmallIntegerField(blank=True, null=True)
    score = models.FloatField(blank=True, null=True)
    img_url = models.URLField(max_length=60, blank=True, null=True)

    objects = models.Manager()

    def __str__(self):
        return f"{self.id} - {self.title}"


class UserFeature(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    firstName = models.CharField(max_length=20, null=True, blank=True)
    lastName = models.CharField(max_length=20, null=True, blank=True)
    photoUrl = models.URLField(null=True, blank=True)

    objects = models.Manager()
    def __str__(self):
        return self.user.username
    
@receiver(post_save, sender=User)
def create_user_feature(sender, instance, created, **kwargs):
    if created:
        UserFeature.objects.create(user=instance)

# Connect the signal
post_save.connect(create_user_feature, sender=User)

