from django.contrib import admin
from .models import Question, Quiz, Feedback, Subscription, Contact, UserProfile, ChatMessage, ChatbotKnowledge

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

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Profile Details', {
            'fields': ('profile_picture', 'bio')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['message_type', 'user', 'session_id', 'content_preview', 'created_at']
    list_filter = ['message_type', 'created_at']
    search_fields = ['content', 'session_id', 'user__username']
    readonly_fields = ['created_at']
    fieldsets = (
        ('Message Information', {
            'fields': ('user', 'session_id', 'message_type', 'content')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = "Content Preview"

@admin.register(ChatbotKnowledge)
class ChatbotKnowledgeAdmin(admin.ModelAdmin):
    list_display = ['category', 'question', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['question', 'answer', 'keywords']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Knowledge Information', {
            'fields': ('category', 'question', 'answer', 'keywords')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
