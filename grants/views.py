from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
import json
import time
from decimal import Decimal

from .models import ReadingTrack, StudentProfile, ReadingLog, WithdrawalRequest
from library.models import Book

@login_required
def dashboard(request):
    """The main student dashboard."""
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    
    if not profile.current_track:
        return redirect('select_track')

    if not profile.deposit_paid:
        return redirect('checkout_deposit', track_id=profile.current_track.id)

    track = profile.current_track
    if track.total_grant_value > 0:
        progress = (profile.total_earned / track.total_grant_value) * 100
    else:
        progress = 0

    context = {
        'profile': profile,
        'progress': min(progress, 100),
    }
    return render(request, 'grants/dashboard.html', context)

@login_required
def select_track(request):
    """Allows student to pick Bronze, Silver, or Gold."""
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    tracks = ReadingTrack.objects.all()

    if request.method == 'POST':
        track_id = request.POST.get('track_id')
        selected_track = ReadingTrack.objects.get(id=track_id)
        
        profile.current_track = selected_track
        profile.deposit_paid = False 
        profile.save()
        
        return redirect('checkout_deposit', track_id=selected_track.id)

    return render(request, 'grants/select_track.html', {'tracks': tracks})

@login_required
def checkout_deposit(request, track_id):
    """The secure checkout page where the student pays their deposit."""
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    track = ReadingTrack.objects.get(id=track_id)
    
    if profile.deposit_paid:
        return redirect('dashboard')

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        phone_number = request.POST.get('phone_number', '')
        
        time.sleep(1.5) 
        
        profile.deposit_paid = True
        profile.save()
        
        messages.success(request, f"✅ Deposit of UGX {track.deposit_amount} successful! Welcome to the {track.name} Track.")
        return redirect('dashboard')

    return render(request, 'grants/checkout.html', {'track': track})

@login_required
def reading_session(request):
    """The page where the actual reading/research happens."""
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    
    completed_book_ids = ReadingLog.objects.filter(
        student=profile, 
        completed=True
    ).values_list('book_id', flat=True)
    
    books = Book.objects.exclude(id__in=completed_book_ids).order_by('?')[:12]
    
    if books.count() < 5:
        from library.management.commands.generate_mock_books import Command
        cmd = Command()
        cmd.handle() 
        books = Book.objects.exclude(id__in=completed_book_ids).order_by('?')[:12]
        
    context = {
        'profile': profile,
        'books': books,
    }
    return render(request, 'grants/reading_session.html', context)

@login_required
@require_POST
def submit_reading(request):
    """API endpoint called by JavaScript when the student submits their summary."""
    try:
        data = json.loads(request.body)
        pages_read = int(data.get('pages_read', 15)) 
        book_id = data.get('book_id')
        summary_text = data.get('summary_text', '') 

        profile, created = StudentProfile.objects.get_or_create(user=request.user)
        
        book = Book.objects.filter(id=book_id).first() if book_id else None
        if not book:
            book = Book.objects.first()
            
        if not book:
            return JsonResponse({'success': False, 'error': 'No books in library!'}, status=400)

        ReadingLog.objects.create(
            student=profile,
            book=book,
            pages_read=pages_read,
            time_spent_minutes=5, 
            summary_text=summary_text, 
            completed=True
        )

        reward = Decimal(str(pages_read * 1000))
        
        profile.wallet_balance += reward
        profile.total_earned += reward
        
        today = timezone.now().date()
        if profile.last_read_date != today:
            if profile.last_read_date == today - timezone.timedelta(days=1):
                profile.current_streak += 1
            else:
                profile.current_streak = 1
            profile.last_read_date = today
            
        profile.save()

        return JsonResponse({
            'success': True, 
            'new_balance': float(profile.wallet_balance),
            'reward_earned': float(reward),
            'streak': profile.current_streak
        })

    except Exception as e:
        print(f"ERROR IN SUBMIT_READING: {e}") 
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@login_required
def request_withdrawal(request):
    """Allows a student to request a cash-out if they hit 80% completion."""
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    
    if not profile.current_track:
        return redirect('select_track')

    track = profile.current_track
    if track.total_grant_value > 0:
        progress = (profile.total_earned / track.total_grant_value) * 100
    else:
        progress = 0

    if request.method == 'POST':
        if progress < 80:
            messages.error(request, f"You must complete at least 80% of your track to withdraw! You are at {progress:.1f}%.")
            return redirect('request_withdrawal')
        
        WithdrawalRequest.objects.create(
            student=profile,
            amount=profile.wallet_balance
        )
        
        profile.wallet_balance = 0.00
        profile.save()
        
        messages.success(request, "Withdrawal requested! Awaiting Admin approval.")
        return redirect('dashboard')

    return render(request, 'grants/request_withdrawal.html', {'progress': progress, 'profile': profile})

@login_required
def admin_dashboard(request):
    """The dashboard for Teachers/Admins to review and approve withdrawals."""
    if request.user.role != 'admin':
        messages.error(request, "Access denied. Admins only.")
        return redirect('dashboard')

    pending_requests = WithdrawalRequest.objects.filter(status='Pending').select_related('student__user', 'student__current_track')
    
    for req in pending_requests:
        req.recent_logs = ReadingLog.objects.filter(student=req.student).order_by('-date_read')[:3]

    context = {
        'pending_requests': pending_requests,
    }
    return render(request, 'grants/admin_dashboard.html', context)

@login_required
def process_withdrawal(request, request_id, action):
    """Admin clicks Approve or Reject."""
    if request.user.role != 'admin':
        return redirect('dashboard')

    withdrawal = WithdrawalRequest.objects.get(id=request_id)
    
    if action == 'approve':
        withdrawal.status = 'Approved'
        messages.success(request, f"Approved UGX {withdrawal.amount} for {withdrawal.student.user.username}.")
    elif action == 'reject':
        withdrawal.status = 'Rejected'
        withdrawal.student.wallet_balance += withdrawal.amount
        withdrawal.student.save()
        messages.warning(request, f"Rejected request for {withdrawal.student.user.username}. Funds returned to wallet.")
        
    withdrawal.save()
    return redirect('admin_dashboard')