from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('select-track/', views.select_track, name='select_track'),
    path('read/', views.reading_session, name='reading_session'),
    path('api/submit-reading/', views.submit_reading, name='submit_reading'),


    path('checkout/<int:track_id>/', views.checkout_deposit, name='checkout_deposit'),
    
    # NEW: Withdrawal routes
    path('withdraw/', views.request_withdrawal, name='request_withdrawal'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/process/<int:request_id>/<str:action>/', views.process_withdrawal, name='process_withdrawal'),
]