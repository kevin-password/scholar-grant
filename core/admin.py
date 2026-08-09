from django.contrib import admin
from .models import LifeProfile, Dimension, Metric, MetricSnapshot

@admin.register(LifeProfile)
class LifeProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_age', 'life_phase', 'overall_goat_score']

@admin.register(Dimension)
class DimensionAdmin(admin.ModelAdmin):
    list_display = ['profile', 'dimension_type', 'score']

@admin.register(Metric)
class MetricAdmin(admin.ModelAdmin):
    list_display = ['name', 'dimension', 'icon']

@admin.register(MetricSnapshot)
class MetricSnapshotAdmin(admin.ModelAdmin):
    list_display = ['metric', 'value', 'timestamp', 'source']
