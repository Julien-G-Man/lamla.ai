from django.contrib import admin
from .models import Question, Quiz, Feedback, Subscription, Contact

# Register your models here.

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['email', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['email']
    readonly_fields = ['created_at']
    actions = ['deactivate_subscriptions', 'activate_subscriptions']
    
    def deactivate_subscriptions(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_subscriptions.short_description = "Deactivate selected subscriptions"
    
    def activate_subscriptions(self, request, queryset):
        queryset.update(is_active=True)
    activate_subscriptions.short_description = "Activate selected subscriptions"

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'created_at', 'is_resolved', 'response_sent']
    list_filter = ['is_resolved', 'response_sent', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['created_at']
    actions = ['mark_as_resolved', 'mark_response_sent']
    fieldsets = (
        ('Student Information', {
            'fields': ('name', 'email')
        }),
        ('Message Details', {
            'fields': ('subject', 'message')
        }),
        ('Status', {
            'fields': ('is_resolved', 'response_sent', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def mark_as_resolved(self, request, queryset):
        queryset.update(is_resolved=True)
    mark_as_resolved.short_description = "Mark selected contacts as resolved"
    
    def mark_response_sent(self, request, queryset):
        queryset.update(response_sent=True)
    mark_response_sent.short_description = "Mark response as sent"
