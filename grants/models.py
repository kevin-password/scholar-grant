from django.db import models
from django.conf import settings # Imports our Custom User model safely

class ReadingTrack(models.Model):
    """The tier the student chooses (Bronze, Silver, Gold)."""
    TIER_CHOICES = [('Bronze', 'Bronze'), ('Silver', 'Silver'), ('Gold', 'Gold')]
    
    name = models.CharField(max_length=20, choices=TIER_CHOICES, unique=True)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Initial deposit to join")
    total_grant_value = models.DecimalField(max_digits=10, decimal_places=2, help_text="Total promised grant (100k-500k)")
    daily_page_target = models.IntegerField(default=10, help_text="Pages to read daily (5-20)")

    def __str__(self):
        return f"{self.name} Track (${self.total_grant_value})"

class StudentProfile(models.Model):
    """Extended profile for students to track wallet and streaks."""
    # Use settings.AUTH_USER_MODEL to link to our custom user
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    current_track = models.ForeignKey(ReadingTrack, on_delete=models.SET_NULL, null=True, blank=True)
    deposit_paid = models.BooleanField(default=False)
    deposit_transaction_id = models.CharField(max_length=50, blank=True, null=True)
    
    # --- NEW: VIRAL REFERRAL SYSTEM FIELDS ---
    referral_code = models.CharField(max_length=10, unique=True, blank=True, null=True)
    referred_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='referrals')
    
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    current_streak = models.IntegerField(default=0)
    last_read_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile (Wallet: ${self.wallet_balance})"

class ReadingLog(models.Model):
    """Tracks every reading session a student completes."""
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='reading_logs')
    # Use the string 'library.Book' to avoid circular import issues
    book = models.ForeignKey('library.Book', on_delete=models.CASCADE)
    pages_read = models.IntegerField()
    time_spent_minutes = models.IntegerField()
    
    # Stores the summary the student pastes!
    summary_text = models.TextField(blank=True, help_text="The summary pasted by the student") 
    
    completed = models.BooleanField(default=False)
    date_read = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.user.username} read {self.pages_read} pages of {self.book.title}"

class WithdrawalRequest(models.Model):
    """When a student wants to cash out their grant."""
    STATUS_CHOICES = [('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')]
    
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='withdrawals')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    requested_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    
    def __str__(self):
        return f"${self.amount} request by {self.student.user.username} ({self.status})"
    
class Achievement(models.Model):
    """Tracks which badges a student has earned."""
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='achievements')
    badge_name = models.CharField(max_length=100)
    badge_icon = models.CharField(max_length=10, default='🏆')  # Emoji icon
    earned_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('student', 'badge_name')  # Can't earn same badge twice
    
    def __str__(self):
        return f"{self.student.user.username} - {self.badge_name}"

# --- NEW: REFERRAL COMMISSION TRACKING ---
class ReferralCommission(models.Model):
    """Tracks the 30-15-10 commission payouts."""
    beneficiary = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='commissions_earned')
    from_user = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='commissions_generated')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    level = models.IntegerField() # 1, 2, or 3
    date_earned = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.beneficiary.user.username} earned {self.amount} from {self.from_user.user.username} (Level {self.level})"