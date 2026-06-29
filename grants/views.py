from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.db.models import Count
import json
import datetime
import time
from decimal import Decimal

# Email imports
from django.core.mail import send_mail
from django.conf import settings

from .models import ReadingTrack, StudentProfile, ReadingLog, WithdrawalRequest, Achievement, ReferralCommission
from library.models import Book

# --- HELPER FUNCTION TO CALCULATE DYNAMIC PAGE RATE ---
def get_rate_per_page(profile):
    if not profile.current_track:
        return 0
    # The new logic: Grant Amount / 50,000 pages (100 books * 500 pages)
    return profile.current_track.total_grant_value / 50000

@login_required
def dashboard(request):
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    if not profile.current_track: return redirect('explore')
    if not profile.deposit_paid and not profile.deposit_transaction_id:
        return redirect('checkout_deposit', track_id=profile.current_track.id)

    track = profile.current_track
    progress = (profile.total_earned / track.total_grant_value) * 100 if track.total_grant_value > 0 else 0

    recent_logs = ReadingLog.objects.filter(student=profile).order_by('-date_read')[:5]
    rate = get_rate_per_page(profile)
    for log in recent_logs: log.earned_ugx = log.pages_read * rate

    is_pending_approval = (not profile.deposit_paid and profile.deposit_transaction_id)

    return render(request, 'grants/dashboard.html', {
        'profile': profile, 
        'progress': min(progress, 100), 
        'recent_logs': recent_logs,
        'is_pending_approval': is_pending_approval,
    })

@login_required
def explore(request):
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    if profile.current_track and profile.deposit_paid: return redirect('dashboard')
    return render(request, 'grants/explore.html')

@login_required
def select_track(request):
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    tracks = ReadingTrack.objects.all()
    if request.method == 'POST':
        selected_track = ReadingTrack.objects.get(id=request.POST.get('track_id'))
        profile.current_track = selected_track
        profile.deposit_paid = False 
        profile.save()
        return redirect('checkout_deposit', track_id=selected_track.id)
    return render(request, 'grants/select_track.html', {'tracks': tracks})

@login_required
def checkout_deposit(request, track_id):
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    track = ReadingTrack.objects.get(id=track_id)
    
    if profile.deposit_paid:
        return redirect('dashboard')

    if request.method == 'POST':
        transaction_id = request.POST.get('transaction_id', '').strip().upper()
        
        if transaction_id:
            profile.deposit_transaction_id = transaction_id
            profile.save()
            messages.success(request, f"Payment submitted! Our admin team will verify Transaction ID: {transaction_id} shortly.")
            return redirect('dashboard') 
        else:
            messages.error(request, "Please enter a valid Transaction ID.")

    return render(request, 'grants/checkout.html', {'track': track})

@login_required
def reading_session(request):
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    
    # --- THE BULLETPROOF AUTO-FETCHER ENGINE ---
    if Book.objects.count() < 50:
        try:
            import requests
            import random
            topics = ['python programming', 'business finance', 'world history', 'psychology', 'science fiction', 'biography', 'self help']
            topic = random.choice(topics)
            url = f'https://openlibrary.org/search.json?q={topic}&limit=15&fields=title,author_name,first_sentence,number_of_pages_median,cover_i,subject'
            
            response = requests.get(url, timeout=10)
            data = response.json()
            
            for doc in data.get('docs', []):
                title = doc.get('title', 'Unknown Title')
                if Book.objects.filter(title=title).exists(): continue
                    
                authors = doc.get('author_name', ['Unknown Author'])
                author = authors[0] if authors else 'Unknown Author'
                cover_i = doc.get('cover_i')
                cover_url = f'https://covers.openlibrary.org/b/id/{cover_i}-L.jpg' if cover_i else f"https://picsum.photos/seed/{title.replace(' ', '')}/300/450"
                first_sentence = doc.get('first_sentence', [])
                description = f"A fascinating book about {topic}."
                if first_sentence:
                    fs = first_sentence[0]
                    description = fs.get('value', description) if isinstance(fs, dict) else str(fs)
                pages = doc.get('number_of_pages_median') or random.randint(150, 450)
                subjects = doc.get('subject', [])
                genre = ', '.join(subjects[:2]).title() if subjects else topic.title()
                
                Book.objects.create(title=title, author=author, cover_url=cover_url, description=description, pages=pages, genre=genre)
        except Exception as e:
            print(f"API Auto-fetch skipped (Network issue): {e}")

    if Book.objects.count() == 0:
        fallback_books = [
            {"title": "The Psychology of Money", "author": "Morgan Housel", "pages": 256, "genre": "Finance"},
            {"title": "Atomic Habits", "author": "James Clear", "pages": 320, "genre": "Self Help"},
            {"title": "Deep Work", "author": "Cal Newport", "pages": 296, "genre": "Productivity"},
            {"title": "Sapiens", "author": "Yuval Noah Harari", "pages": 443, "genre": "History"},
            {"title": "The Lean Startup", "author": "Eric Ries", "pages": 336, "genre": "Business"},
            {"title": "Thinking, Fast and Slow", "author": "Daniel Kahneman", "pages": 499, "genre": "Psychology"},
            {"title": "Rich Dad Poor Dad", "author": "Robert Kiyosaki", "pages": 336, "genre": "Finance"},
            {"title": "The 4-Hour Workweek", "author": "Timothy Ferriss", "pages": 308, "genre": "Business"},
            {"title": "Educated", "author": "Tara Westover", "pages": 334, "genre": "Biography"},
            {"title": "Dune", "author": "Frank Herbert", "pages": 688, "genre": "Sci-Fi"},
            {"title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "pages": 180, "genre": "Classic"},
            {"title": "1984", "author": "George Orwell", "pages": 328, "genre": "Dystopian"},
            {"title": "Zero to One", "author": "Peter Thiel", "pages": 224, "genre": "Business"},
            {"title": "The Alchemist", "author": "Paulo Coelho", "pages": 197, "genre": "Fiction"},
            {"title": "Steve Jobs", "author": "Walter Isaacson", "pages": 656, "genre": "Biography"},
        ]
        for b in fallback_books:
            cover_url = f"https://picsum.photos/seed/{b['title'].replace(' ', '')}/300/450"
            Book.objects.create(title=b['title'], author=b['author'], pages=b['pages'], genre=b['genre'], cover_url=cover_url, description=f"A highly rated, bestselling book by {b['author']}.")
        print("✅ Fallback triggered: 15 real books injected!")

    completed_book_ids = ReadingLog.objects.filter(student=profile, completed=True).values_list('book_id', flat=True)
    books = Book.objects.exclude(id__in=completed_book_ids).order_by('?')[:12]
    return render(request, 'grants/reading_session.html', {'profile': profile, 'books': books})

@login_required
@require_POST
def submit_reading(request):
    try:
        data = json.loads(request.body)
        pages_read = int(data.get('pages_read', 15)) 
        book_id = data.get('book_id')
        summary_text = data.get('summary_text', '') 
        profile, created = StudentProfile.objects.get_or_create(user=request.user)
        
        book = Book.objects.filter(id=book_id).first() if book_id else Book.objects.first()
        if not book: return JsonResponse({'success': False, 'error': 'No books in library!'}, status=400)

        ReadingLog.objects.create(student=profile, book=book, pages_read=pages_read, time_spent_minutes=5, summary_text=summary_text, completed=True)

        today = timezone.now().date()
        if profile.last_read_date != today:
            profile.current_streak = profile.current_streak + 1 if profile.last_read_date == today - timezone.timedelta(days=1) else 1
            profile.last_read_date = today

        # --- NEW DYNAMIC RATE LOGIC ---
        rate_per_page = get_rate_per_page(profile)
        base_reward = pages_read * rate_per_page
        
        multiplier = 2.0 if profile.current_streak >= 7 else (1.5 if profile.current_streak >= 3 else 1.0)
        reward = Decimal(str(int(base_reward * multiplier)))
        
        profile.wallet_balance += reward
        profile.total_earned += reward
        profile.save()

        new_badges = []
        total_books_read = ReadingLog.objects.filter(student=profile).count()
        if total_books_read == 1:
            _, created = Achievement.objects.get_or_create(student=profile, badge_name='First Book Read', defaults={'badge_icon': '📖'})
            if created: new_badges.append({'name': 'First Book Read', 'icon': '📖'})
        if profile.current_streak >= 7:
            _, created = Achievement.objects.get_or_create(student=profile, badge_name='7-Day Streak', defaults={'badge_icon': '🔥'})
            if created: new_badges.append({'name': '7-Day Streak', 'icon': '🔥'})
        if total_books_read >= 10:
            _, created = Achievement.objects.get_or_create(student=profile, badge_name='10 Books Completed', defaults={'badge_icon': '🏆'})
            if created: new_badges.append({'name': '10 Books Completed', 'icon': '🏆'})
        if profile.total_earned >= 100000:
            _, created = Achievement.objects.get_or_create(student=profile, badge_name='100k UGX Earned', defaults={'badge_icon': '💰'})
            if created: new_badges.append({'name': '100k UGX Earned', 'icon': '💰'})

        return JsonResponse({'success': True, 'new_balance': float(profile.wallet_balance), 'reward_earned': float(reward), 'streak': profile.current_streak, 'multiplier': multiplier, 'new_badges': new_badges})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@login_required
def request_withdrawal(request):
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    if not profile.current_track: return redirect('explore')
    track = profile.current_track
    progress = (profile.total_earned / track.total_grant_value) * 100 if track.total_grant_value > 0 else 0
    if request.method == 'POST':
        if progress < 80:
            messages.error(request, f"You must complete at least 80% of your track to withdraw! You are at {progress:.1f}%.")
            return redirect('request_withdrawal')
        WithdrawalRequest.objects.create(student=profile, amount=profile.wallet_balance)
        profile.wallet_balance = 0.00
        profile.save()
        messages.success(request, "Withdrawal requested! Awaiting Admin approval.")
        return redirect('dashboard')
    return render(request, 'grants/request_withdrawal.html', {'progress': progress, 'profile': profile})

@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':
        messages.error(request, "Access denied. Admins only.")
        return redirect('dashboard')
        
    pending_requests = WithdrawalRequest.objects.filter(status='Pending').select_related('student__user', 'student__current_track')
    for req in pending_requests:
        # Calculate dynamic rate for the admin dashboard logs
        rate = get_rate_per_page(req.student)
        logs = ReadingLog.objects.filter(student=req.student).order_by('-date_read')[:3]
        for log in logs: log.earned_ugx = log.pages_read * rate
        req.recent_logs = logs
        
    pending_deposits = StudentProfile.objects.filter(deposit_paid=False, deposit_transaction_id__isnull=False).exclude(deposit_transaction_id='').select_related('user', 'current_track')

    return render(request, 'grants/admin_dashboard.html', {
        'pending_requests': pending_requests,
        'total_pending_amount': sum(req.amount for req in pending_requests),
        'total_pending_count': pending_requests.count(),
        'pending_deposits': pending_deposits,
    })

@login_required
def process_withdrawal(request, request_id, action):
    if request.user.role != 'admin': return redirect('dashboard')
    withdrawal = WithdrawalRequest.objects.get(id=request_id)
    student_user = withdrawal.student.user
    
    if student_user.email:
        if action == 'approve':
            subject = f"Your Withdrawal of UGX {withdrawal.amount:,.0f} has been Approved! "
            message = f"Hi {student_user.username},\n\nGreat news! Our academic team has verified your reading summaries and approved your withdrawal request.\n\nAMOUNT SENT:\nUGX {withdrawal.amount:,.0f}\n\nThe funds have been dispatched to your registered Mobile Money number. Please allow up to 24 hours for the transaction to reflect on your phone.\n\nKeep up the excellent reading habits to unlock your next withdrawal!\n\nBest,\nThe ScholarGrants Team\n\nLog in: https://ScholarGrantsUG.pythonanywhere.com/"
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [student_user.email], fail_silently=True)
            
        elif action == 'reject':
            subject = "Update on your Withdrawal Request"
            message = f"Hi {student_user.username},\n\nOur academic team has reviewed your recent reading summaries for your withdrawal request of UGX {withdrawal.amount:,.0f}.\n\nUnfortunately, we were unable to approve this request at this time. This usually happens if the summaries provided do not sufficiently demonstrate comprehension of the reading material.\n\nDON'T WORRY:\nThe funds (UGX {withdrawal.amount:,.0f}) have been safely returned to your ScholarGrants wallet. You can request a withdrawal again once you have completed more reading sessions with detailed summaries.\n\nKeep reading, and we look forward to approving your next request!\n\nBest,\nThe ScholarGrants Team\n\nLog in: https://ScholarGrantsUG.pythonanywhere.com/"
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [student_user.email], fail_silently=True)

    if action == 'approve':
        withdrawal.status = 'Approved'
        messages.success(request, f"Approved UGX {withdrawal.amount} for {student_user.username}. Email sent!")
    elif action == 'reject':
        withdrawal.status = 'Rejected'
        withdrawal.student.wallet_balance += withdrawal.amount
        withdrawal.student.save()
        messages.warning(request, f"Rejected request for {student_user.username}. Funds returned to wallet. Email sent!")
        
    withdrawal.save()
    return redirect('admin_dashboard')

@login_required
def approve_deposit(request, profile_id):
    if request.user.role != 'admin':
        return redirect('dashboard')
    
    profile = StudentProfile.objects.get(id=profile_id)
    profile.deposit_paid = True
    profile.save()
    
    deposit_amount = profile.current_track.deposit_amount
    current_level_profile = profile.referred_by
    level = 1
    commission_rates = {1: 0.30, 2: 0.15, 3: 0.10}

    while current_level_profile and level <= 3:
        rate = commission_rates.get(level, 0)
        commission_amount = Decimal(str(deposit_amount * rate))
        
        if commission_amount > 0:
            current_level_profile.wallet_balance += commission_amount
            current_level_profile.total_earned += commission_amount
            current_level_profile.save()
            
            ReferralCommission.objects.create(
                beneficiary=current_level_profile,
                from_user=profile,
                amount=commission_amount,
                level=level
            )
        current_level_profile = current_level_profile.referred_by
        level += 1

    messages.success(request, f"Verified deposit for {profile.user.username}. Referral commissions automatically distributed!")
    return redirect('admin_dashboard')

def about(request): return render(request, 'grants/about.html')
def contact(request): return render(request, 'grants/contact.html')
def privacy(request): return render(request, 'grants/privacy.html')
def terms(request): return render(request, 'grants/terms.html')

@login_required
def student_profile(request):
    profile, created = StudentProfile.objects.get_or_create(user=request.user)
    reading_history = ReadingLog.objects.filter(student=profile).order_by('-date_read')
    rate = get_rate_per_page(profile)
    for log in reading_history: log.earned_ugx = log.pages_read * rate
    
    achievements = Achievement.objects.filter(student=profile).order_by('-earned_date')

    end_date = timezone.now().date()
    start_date = end_date - datetime.timedelta(days=89) 
    logs_in_range = ReadingLog.objects.filter(student=profile, date_read__gte=start_date, date_read__lte=end_date).values_list('date_read', flat=True)
    active_dates = set()
    for dt in logs_in_range: active_dates.add(dt.date() if hasattr(dt, 'date') else dt)
    streak_calendar = [{'date': start_date + datetime.timedelta(days=i), 'read': (start_date + datetime.timedelta(days=i)) in active_dates} for i in range(90)]

    return render(request, 'grants/profile.html', {
        'profile': profile, 'reading_history': reading_history,
        'total_books': reading_history.count(), 'total_pages': sum(log.pages_read for log in reading_history),
        'days_active': reading_history.dates('date_read', 'day').count(), 'achievements': achievements,
        'streak_calendar': streak_calendar,
    })

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user) 
            messages.success(request, 'Your password was successfully changed!')
            return redirect('student_profile')
    else: form = PasswordChangeForm(request.user)
    return render(request, 'grants/edit_profile.html', {'form': form})

@login_required
def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    page_count = getattr(book, 'pages', 15)
    rate = 20 # Default fallback for display purposes
    if hasattr(book, 'student'): # Just in case
        rate = get_rate_per_page(book.student)
    book.earned_value = page_count * rate 
    return render(request, 'grants/book_detail.html', {'book': book, 'page_count': page_count})

@login_required
def leaderboard(request):
    top_earners = StudentProfile.objects.filter(total_earned__gt=0).select_related('user', 'current_track').order_by('-total_earned')[:20]
    top_streaks = StudentProfile.objects.filter(current_streak__gt=0).select_related('user').order_by('-current_streak')[:10]
    top_readers = StudentProfile.objects.annotate(books_count=Count('reading_logs')).filter(books_count__gt=0).select_related('user').order_by('-books_count')[:10]
    return render(request, 'grants/leaderboard.html', {'top_earners': top_earners, 'top_streaks': top_streaks, 'top_readers': top_readers})
