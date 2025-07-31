from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib import messages
from .models import (
    Opportunity, Wallet, Investor, Investment, 
    MultiCurrencyInvestment, InvestmentComponent, EmailNotification
)
from .services import EmailService, WalletService


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ['address', 'wallet_type', 'is_active', 'created_at']
    list_filter = ['wallet_type', 'is_active', 'created_at']
    search_fields = ['address']
    readonly_fields = ['id', 'created_at']
    list_per_page = 20


@admin.register(Investor)
class InvestorAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'phone', 'wallet', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at', 'wallet__wallet_type']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    readonly_fields = ['id', 'created_at', 'updated_at']
    list_per_page = 20
    actions = ['generate_wallet', 'send_test_email']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone')
        }),
        ('Wallet Information', {
            'fields': ('wallet',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def generate_wallet(self, request, queryset):
        """Generate wallet for selected investors"""
        count = 0
        for investor in queryset:
            if not investor.wallet:
                wallet = WalletService.create_wallet_for_investor(investor, 'BTC')
                count += 1
        
        self.message_user(
            request,
            f"Successfully generated wallets for {count} investors.",
            messages.SUCCESS
        )
    generate_wallet.short_description = "Generate wallet for selected investors"
    
    def send_test_email(self, request, queryset):
        """Send test email to selected investors"""
        count = 0
        for investor in queryset:
            # Create a test notification
            notification = EmailNotification.objects.create(
                investor=investor,
                notification_type='investment_created',
                subject='Test Email - Bitcoin Treasury Investment',
                message='This is a test email to verify your email address is working correctly.',
                is_sent=True
            )
            count += 1
        
        self.message_user(
            request,
            f"Test email notifications created for {count} investors.",
            messages.SUCCESS
        )
    send_test_email.short_description = "Send test email to selected investors"


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'company_name', 'country', 'currency', 'total_goal', 
        'current_raised', 'progress_bar', 'status', 'deadline'
    ]
    list_filter = ['status', 'currency', 'country', 'created_at', 'deadline']
    search_fields = ['title', 'company_name', 'description', 'ticker_symbol']
    readonly_fields = ['id', 'current_raised', 'progress_percentage', 'is_funded', 'is_expired', 'created_at', 'updated_at']
    list_per_page = 20
    actions = ['send_deadline_reminders', 'update_expired_opportunities']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'company_name', 'country')
        }),
        ('Market Information', {
            'fields': ('ticker_symbol', 'ticker_url', 'data_room_url')
        }),
        ('Funding Details', {
            'fields': ('total_goal', 'currency', 'minimum_investment', 'current_raised')
        }),
        ('Timeline', {
            'fields': ('deadline',)
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Progress Information', {
            'fields': ('progress_percentage', 'is_funded', 'is_expired'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def progress_bar(self, obj):
        """Display a progress bar for funding progress"""
        percentage = obj.progress_percentage
        color = 'green' if percentage >= 100 else 'orange' if percentage >= 50 else 'red'
        
        return format_html(
            '<div style="width: 100px; background-color: #f0f0f0; border-radius: 3px;">'
            '<div style="width: {}%; height: 20px; background-color: {}; border-radius: 3px; '
            'display: flex; align-items: center; justify-content: center; color: white; font-size: 10px;">'
            '{}%</div></div>',
            min(percentage, 100), color, f"{percentage:.1f}"
        )
    progress_bar.short_description = 'Progress'
    
    def send_deadline_reminders(self, request, queryset):
        """Send deadline reminders for selected opportunities"""
        count = 0
        for opportunity in queryset:
            EmailService.send_deadline_reminder(opportunity)
            count += 1
        
        self.message_user(
            request,
            f"Deadline reminders sent for {count} opportunities.",
            messages.SUCCESS
        )
    send_deadline_reminders.short_description = "Send deadline reminders"
    
    def update_expired_opportunities(self, request, queryset):
        """Update expired opportunities status"""
        count = 0
        for opportunity in queryset:
            if opportunity.is_expired and opportunity.status == 'active':
                opportunity.status = 'expired'
                opportunity.save()
                count += 1
        
        self.message_user(
            request,
            f"Updated {count} expired opportunities.",
            messages.SUCCESS
        )
    update_expired_opportunities.short_description = "Update expired opportunities"


@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display = [
        'investor', 'opportunity', 'amount', 'currency', 'status', 
        'created_at', 'transaction_hash_display'
    ]
    list_filter = ['status', 'currency', 'created_at', 'opportunity__status']
    search_fields = ['investor__first_name', 'investor__last_name', 'investor__email', 'transaction_hash']
    readonly_fields = ['id', 'created_at', 'updated_at']
    list_per_page = 20
    
    fieldsets = (
        ('Investment Details', {
            'fields': ('opportunity', 'investor', 'amount', 'currency')
        }),
        ('Status & Transaction', {
            'fields': ('status', 'transaction_hash')
        }),
        ('Additional Information', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def transaction_hash_display(self, obj):
        """Display transaction hash with link to blockchain explorer"""
        if obj.transaction_hash:
            # You can customize these URLs based on the currency
            if obj.currency == 'BTC':
                url = f"https://blockchain.info/tx/{obj.transaction_hash}"
            elif obj.currency == 'ETH':
                url = f"https://etherscan.io/tx/{obj.transaction_hash}"
            else:
                url = "#"
            
            return format_html(
                '<a href="{}" target="_blank">{}</a>',
                url, obj.transaction_hash[:20] + "..." if len(obj.transaction_hash) > 20 else obj.transaction_hash
            )
        return "-"
    transaction_hash_display.short_description = 'Transaction Hash'


class InvestmentComponentInline(admin.TabularInline):
    model = InvestmentComponent
    extra = 1
    fields = ['amount', 'currency', 'transaction_hash', 'wallet_address']


@admin.register(MultiCurrencyInvestment)
class MultiCurrencyInvestmentAdmin(admin.ModelAdmin):
    list_display = [
        'investor', 'opportunity', 'status', 'total_amount_usd_display', 
        'components_count', 'created_at'
    ]
    list_filter = ['status', 'created_at', 'opportunity__status']
    search_fields = ['investor__first_name', 'investor__last_name', 'investor__email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    list_per_page = 20
    inlines = [InvestmentComponentInline]
    
    fieldsets = (
        ('Investment Details', {
            'fields': ('opportunity', 'investor', 'status')
        }),
        ('Additional Information', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_amount_usd_display(self, obj):
        """Display total amount in USD"""
        return f"${obj.total_amount_usd:,.2f}"
    total_amount_usd_display.short_description = 'Total USD'
    
    def components_count(self, obj):
        """Display number of currency components"""
        return obj.components.count()
    components_count.short_description = 'Currencies'


@admin.register(InvestmentComponent)
class InvestmentComponentAdmin(admin.ModelAdmin):
    list_display = [
        'multi_currency_investment', 'amount', 'currency', 
        'transaction_hash_display', 'created_at'
    ]
    list_filter = ['currency', 'created_at']
    search_fields = ['transaction_hash', 'wallet_address']
    readonly_fields = ['id', 'created_at']
    list_per_page = 20
    
    fieldsets = (
        ('Component Details', {
            'fields': ('multi_currency_investment', 'amount', 'currency')
        }),
        ('Transaction Information', {
            'fields': ('transaction_hash', 'wallet_address')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def transaction_hash_display(self, obj):
        """Display transaction hash with link to blockchain explorer"""
        if obj.transaction_hash:
            # You can customize these URLs based on the currency
            if obj.currency == 'BTC':
                url = f"https://blockchain.info/tx/{obj.transaction_hash}"
            elif obj.currency == 'ETH':
                url = f"https://etherscan.io/tx/{obj.transaction_hash}"
            else:
                url = "#"
            
            return format_html(
                '<a href="{}" target="_blank">{}</a>',
                url, obj.transaction_hash[:20] + "..." if len(obj.transaction_hash) > 20 else obj.transaction_hash
            )
        return "-"
    transaction_hash_display.short_description = 'Transaction Hash'


@admin.register(EmailNotification)
class EmailNotificationAdmin(admin.ModelAdmin):
    list_display = ['investor', 'notification_type', 'subject', 'is_sent', 'sent_at']
    list_filter = ['notification_type', 'is_sent', 'sent_at']
    search_fields = ['investor__email', 'subject', 'message']
    readonly_fields = ['id', 'sent_at']
    list_per_page = 20
    
    fieldsets = (
        ('Notification Details', {
            'fields': ('investor', 'opportunity', 'investment', 'notification_type')
        }),
        ('Email Content', {
            'fields': ('subject', 'message')
        }),
        ('Status', {
            'fields': ('is_sent',)
        }),
        ('Timestamps', {
            'fields': ('sent_at',),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Prevent manual creation of email notifications"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Allow editing of email notifications"""
        return True
    
    def has_delete_permission(self, request, obj=None):
        """Allow deletion of email notifications"""
        return True
