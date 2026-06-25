from django.contrib import admin
from .models import ReadingTrack, StudentProfile, ReadingLog, WithdrawalRequest

admin.site.register(ReadingTrack)
admin.site.register(StudentProfile)
admin.site.register(ReadingLog)
admin.site.register(WithdrawalRequest)