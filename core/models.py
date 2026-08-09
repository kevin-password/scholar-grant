from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

class LifeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='life_profile')
    birth_date = models.DateField()
    biological_age = models.FloatField(default=0.0)
    
    LIFE_PHASES = [
        ('CURIOSITY', '🔍 Curiosity Phase (5-18)'),
        ('FAILURE', '💪 Failure Phase (18-30)'),
        ('DELEGATION', '🤝 Delegation Phase (30-50)'),
        ('MENTORSHIP', '📚 Mentorship Phase (50-70)'),
        ('ACCEPTANCE', '🕊️ Acceptance Phase (70-90)'),
    ]
    life_phase = models.CharField(max_length=20, choices=LIFE_PHASES, default='CURIOSITY')
    overall_goat_score = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()}'s Profile"
    
    def get_age(self):
        from datetime import date
        today = date.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )

class Dimension(models.Model):
    DIMENSION_TYPES = [
        ('PHYSICAL', '💪 Physical'),
        ('COGNITIVE', '🧠 Cognitive'),
        ('SPIRITUAL', '🙏 Spiritual'),
        ('SOCIAL', '👥 Social'),
        ('CHARACTER', '⚡ Character'),
        ('EMOTIONAL', '💖 Emotional'),
        ('FINANCIAL', '💰 Financial'),
        ('CREATIVE', '🎨 Creative'),
        ('LONGEVITY', '🧬 Longevity'),
        ('SOUL', '✨ Soul'),
    ]
    
    profile = models.ForeignKey(LifeProfile, on_delete=models.CASCADE, related_name='dimensions')
    dimension_type = models.CharField(max_length=20, choices=DIMENSION_TYPES)
    score = models.FloatField(default=0.0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['profile', 'dimension_type']
    
    def __str__(self):
        return f"{self.get_dimension_type_display()}: {self.score:.1f}"

class Metric(models.Model):
    dimension = models.ForeignKey(Dimension, on_delete=models.CASCADE, related_name='metrics')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    unit = models.CharField(max_length=20, blank=True)
    icon = models.CharField(max_length=10, default='📊')
    is_real_time = models.BooleanField(default=True)
    is_lower_better = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.icon} {self.name}"

class MetricSnapshot(models.Model):
    metric = models.ForeignKey(Metric, on_delete=models.CASCADE, related_name='snapshots')
    value = models.FloatField()
    timestamp = models.DateTimeField(default=timezone.now)
    source = models.CharField(max_length=50, default='manual')
    
    def __str__(self):
        return f"{self.metric.name}: {self.value}"
    
    class Meta:
        ordering = ['-timestamp']
