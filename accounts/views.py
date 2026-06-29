from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .models import User
from grants.models import StudentProfile
import uuid # Needed to generate unique referral codes

# Email imports (Using standard send_mail for bulletproof plain text)
from django.core.mail import send_mail
from django.conf import settings

def register(request):
    """Allows new students to create their own accounts with referral tracking."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email', '') 
        referral_code_input = request.POST.get('referral_code', '').strip().upper()
        
        if User.objects.filter(username=username).exists():
            return render(request, 'accounts/register.html', {'error': 'Username already taken!'})
            
        # Create the user and save the email to their profile
        user = User.objects.create_user(
            username=username, 
            password=password, 
            email=email, 
            role='student'
        )
        profile = StudentProfile.objects.create(user=user)
        
        # --- VIRAL REFERRAL SYSTEM LOGIC ---
        # 1. Generate a unique 8-character referral code for the new user (e.g., A1B2C3D4)
        profile.referral_code = uuid.uuid4().hex[:8].upper()
        
        # 2. Link to the referrer if they provided a valid code
        if referral_code_input:
            try:
                referrer_profile = StudentProfile.objects.get(referral_code=referral_code_input)
                if referrer_profile != profile: # Prevent self-referral
                    profile.referred_by = referrer_profile
            except StudentProfile.DoesNotExist:
                pass # Invalid code, just ignore it
                
        profile.save()
        
        # --- SEND WELCOME EMAIL (PLAIN TEXT) ---
        if user.email:
            subject = "Welcome to ScholarGrants! Start Reading & Earning 📚💰"
            message = f"""Hi {user.username},

Welcome to ScholarGrants! Your journey to earning while reading starts now.

🚀 HOW TO GET STARTED:
1. Log in and choose your Reading Track (Bronze, Silver, or Gold).
2. Pay your small refundable deposit to activate your track.
3. Read books, submit your summaries, and watch your UGX wallet grow!

💡 PRO TIP: Consistency is key! Read for 3 days in a row to unlock a 1.5x earnings multiplier, and 7 days for a massive 2x multiplier.

🔥 EARN PASSIVE INCOME:
Share your unique referral code from your dashboard to earn 30% passive commissions on your friends' deposits!

Log in here to get started: http://127.0.0.1:8000/

Need help? Reply to this email or visit our support page: http://127.0.0.1:8000/contact/

Best,
The ScholarGrants Team
Empowering scholars, one page at a time.
"""
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
            
        login(request, user)
        return redirect('dashboard')
        
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