from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.models import Dimension, MetricSnapshot

@login_required
def index(request):
    profile = request.user.life_profile
    dimensions = Dimension.objects.filter(profile=profile)
    recent = MetricSnapshot.objects.filter(
        metric__dimension__profile=profile
    ).select_related('metric')[:10]
    
    context = {
        'profile': profile,
        'dimensions': dimensions,
        'recent_snapshots': recent,
    }
    return render(request, 'dashboard/index.html', context)
