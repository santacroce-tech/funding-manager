from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, URLValidator
from decimal import Decimal
import uuid


class Opportunity(models.Model):
    """Model for investment opportunities in Bitcoin Treasury companies"""
    CURRENCY_CHOICES = [
        ('BTC', 'Bitcoin'),
        ('ETH', 'Ethereum'),
        ('USDT', 'Tether'),
        ('USDC', 'USD Coin'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('funded', 'Funded'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    company_name = models.CharField(max_length=200)
    country = models.CharField(max_length=100, blank=True, null=True)
    ticker_symbol = models.CharField(max_length=20, blank=True, null=True)
    ticker_url = models.URLField(blank=True, null=True, validators=[URLValidator()])
    data_room_url = models.URLField(blank=True, null=True, validators=[URLValidator()])
    total_goal = models.DecimalField(
        max_digits=20, 
        decimal_places=8,
        validators=[MinValueValidator(Decimal('0.00000001'))]
    )
    currency = models.CharField(max_length=4, choices=CURRENCY_CHOICES, default='BTC')
    current_raised = models.DecimalField(
        max_digits=20, 
        decimal_places=8,
        default=0,
        validators=[MinValueValidator(Decimal('0'))]
    )
    minimum_investment = models.DecimalField(
        max_digits=20, 
        decimal_places=8,
        validators=[MinValueValidator(Decimal('0.00000001'))]
    )
    deadline = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Opportunities"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.company_name}"
    
    @property
    def progress_percentage(self):
        """Calculate the funding progress percentage"""
        if self.total_goal > 0:
            return (self.current_raised / self.total_goal) * 100
        return 0
    
    @property
    def is_funded(self):
        """Check if the opportunity is fully funded"""
        return self.current_raised >= self.total_goal
    
    @property
    def is_expired(self):
        """Check if the opportunity deadline has passed"""
        from django.utils import timezone
        return timezone.now() > self.deadline


class Wallet(models.Model):
    """Model for investor wallets"""
    WALLET_TYPE_CHOICES = [
        ('BTC', 'Bitcoin'),
        ('ETH', 'Ethereum'),
        ('USDT', 'Tether'),
        ('USDC', 'USD Coin'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    address = models.CharField(max_length=255, unique=True)
    wallet_type = models.CharField(max_length=4, choices=WALLET_TYPE_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.wallet_type} - {self.address[:20]}..."


class Investor(models.Model):
    """Model for investors"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    wallet = models.ForeignKey(Wallet, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Investment(models.Model):
    """Model for individual investments"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='investments')
    investor = models.ForeignKey(Investor, on_delete=models.CASCADE, related_name='investments')
    amount = models.DecimalField(
        max_digits=20, 
        decimal_places=8,
        validators=[MinValueValidator(Decimal('0.00000001'))]
    )
    currency = models.CharField(max_length=4, choices=Opportunity.CURRENCY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_hash = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        # Remove unique constraint to allow multiple investments per investor per opportunity
        # unique_together = ['opportunity', 'investor']
    
    def __str__(self):
        return f"{self.investor.full_name} - {self.opportunity.title} - {self.amount} {self.currency}"
    
    def save(self, *args, **kwargs):
        # Update opportunity's current_raised when investment is confirmed
        if self.status == 'confirmed':
            # Check if this is a new confirmation
            if self.pk:
                try:
                    old_instance = Investment.objects.get(pk=self.pk)
                    if old_instance.status != 'confirmed':
                        self.opportunity.current_raised += self.amount
                        self.opportunity.save()
                except Investment.DoesNotExist:
                    # New investment being created as confirmed
                    self.opportunity.current_raised += self.amount
                    self.opportunity.save()
            else:
                # New investment being created as confirmed
                self.opportunity.current_raised += self.amount
                self.opportunity.save()
        super().save(*args, **kwargs)


class MultiCurrencyInvestment(models.Model):
    """Model for investments with multiple currencies"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name='multi_currency_investments')
    investor = models.ForeignKey(Investor, on_delete=models.CASCADE, related_name='multi_currency_investments')
    status = models.CharField(max_length=20, choices=Investment.STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.investor.full_name} - {self.opportunity.title} - Multi-Currency"
    
    @property
    def total_amount_usd(self):
        """Calculate total amount in USD equivalent"""
        total = Decimal('0')
        for component in self.components.all():
            # This would need to be implemented with real-time exchange rates
            # For now, we'll use placeholder conversion rates
            if component.currency == 'BTC':
                total += component.amount * Decimal('50000')  # Placeholder rate
            elif component.currency == 'ETH':
                total += component.amount * Decimal('3000')   # Placeholder rate
            elif component.currency in ['USDT', 'USDC']:
                total += component.amount
        return total


class InvestmentComponent(models.Model):
    """Model for individual currency components of a multi-currency investment"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    multi_currency_investment = models.ForeignKey(
        MultiCurrencyInvestment, 
        on_delete=models.CASCADE, 
        related_name='components'
    )
    amount = models.DecimalField(
        max_digits=20, 
        decimal_places=8,
        validators=[MinValueValidator(Decimal('0.00000001'))]
    )
    currency = models.CharField(max_length=4, choices=Opportunity.CURRENCY_CHOICES)
    transaction_hash = models.CharField(max_length=255, blank=True, null=True)
    wallet_address = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.amount} {self.currency} - {self.multi_currency_investment}"


class EmailNotification(models.Model):
    """Model to track email notifications sent to investors"""
    NOTIFICATION_TYPE_CHOICES = [
        ('investment_created', 'Investment Created'),
        ('investment_updated', 'Investment Updated'),
        ('deadline_reminder', 'Deadline Reminder'),
        ('opportunity_update', 'Opportunity Update'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    investor = models.ForeignKey(Investor, on_delete=models.CASCADE)
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, null=True, blank=True)
    investment = models.ForeignKey(Investment, on_delete=models.CASCADE, null=True, blank=True)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_sent = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"{self.notification_type} - {self.investor.email} - {self.sent_at}"
