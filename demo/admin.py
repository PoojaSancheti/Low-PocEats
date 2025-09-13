# demo/admin.py
from django.contrib import admin
from .models import HealthConditions, Meal, UserProfile, EmailVerificationCode, Feedback

# Register your models here.
@admin.register(HealthConditions)
class HealthConditionsAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ['name', 'meal_type', 'diet_suitability', 'total_cost']
    list_filter = ['meal_type', 'diet_suitability']
    search_fields = ['name', 'ingredients']
    filter_horizontal = ['health_condition_suitability']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'age', 'diet_pref']
    list_filter = ['diet_pref']
    search_fields = ['user__username', 'name']

@admin.register(EmailVerificationCode)
class EmailVerificationCodeAdmin(admin.ModelAdmin):
    list_display = ['user', 'code', 'created_at', 'expires_at', 'is_valid']
    list_filter = ['is_valid', 'created_at']

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['name', 'email']
    readonly_fields = ['created_at']
