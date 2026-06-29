from django.urls import path
from . import views

urlpatterns = [
    # Main Dashboard & Explore
    path('', views.dashboard, name='dashboard'),
    path('explore/', views.explore, name='explore'),
    
    # Track Selection & Checkout
    path('select-track/', views.select_track, name='select_track'),
    path('checkout/<int:track_id>/', views.checkout_deposit, name='checkout_deposit'),
    
    # Reading Session
    path('read/', views.reading_session, name='reading_session'),
    path('api/submit-reading/', views.submit_reading, name='submit_reading'),
    
    # Withdrawals
    path('withdraw/', views.request_withdrawal, name='request_withdrawal'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('process-withdrawal/<int:request_id>/<str:action>/', views.process_withdrawal, name='process_withdrawal'),
    
    # Student Profile (The one we just built!)
    path('profile/', views.student_profile, name='student_profile'),
    
    # Static Information Pages
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('privacy/', views.privacy, name='privacy'),
    path('terms/', views.terms, name='terms'),



    path('profile/edit/', views.edit_profile, name='edit_profile'),

    path('book/<int:book_id>/', views.book_detail, name='book_detail'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),


    path('approve-deposit/<int:profile_id>/', views.approve_deposit, name='approve_deposit'),
]