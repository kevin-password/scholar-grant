from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .models import User
from grants.models import StudentProfile

def register(request):
    """Allows new students to create their own accounts."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if User.objects.filter(username=username).exists():
            return render(request, 'accounts/register.html', {'error': 'Username already taken!'})
            
        user = User.objects.create_user(username=username, password=password, role='student')
        StudentProfile.objects.create(user=user)
        
        login(request, user)
        return redirect('select_track')
        
    return render(request, 'accounts/register.html')

def login_view(request):
    """Custom login page."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'accounts/login.html', {'error': 'Invalid username or password.'})
            
    return render(request, 'accounts/login.html')

@login_required
def logout_view(request):
    """Logs the user out and sends them to the login page."""
    logout(request)
    return redirect('login')