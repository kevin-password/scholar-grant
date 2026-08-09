from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import LifeProfile, Dimension

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        from datetime import date
        profile = LifeProfile.objects.create(user=instance, birth_date=date(2000, 1, 1))
        
        # Create all 10 dimensions
        for dim_type, _ in Dimension.DIMENSION_TYPES:
            Dimension.objects.create(profile=profile, dimension_type=dim_type)
