from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Investment, Opportunity, EmailNotification
from .services import EmailService, WalletService


@receiver(post_save, sender=Investment)
def investment_post_save(sender, instance, created, **kwargs):
    """Handle post-save actions for investments"""
    if created:
        # Send initial notification when investment is created
        EmailService.send_investment_created_notification(instance)
    else:
        # Send update notification when investment status changes
        if instance.status == 'confirmed':
            # Update opportunity's current_raised
            opportunity = instance.opportunity
            opportunity.current_raised += instance.amount
            opportunity.save()
            
            # Check if opportunity is now funded
            if opportunity.is_funded:
                opportunity.status = 'funded'
                opportunity.save()
        
        # Send update notification
        EmailService.send_investment_updated_notification(instance)


@receiver(post_save, sender=Opportunity)
def opportunity_post_save(sender, instance, created, **kwargs):
    """Handle post-save actions for opportunities"""
    if not created:
        # Send opportunity update notifications to all investors
        EmailService.send_opportunity_update_notification(instance)


@receiver(pre_save, sender=Opportunity)
def opportunity_pre_save(sender, instance, **kwargs):
    """Handle pre-save actions for opportunities"""
    if instance.pk:
        # Check if deadline has passed
        if timezone.now() > instance.deadline and instance.status == 'active':
            instance.status = 'expired'
        
        # Check if opportunity is funded
        if instance.is_funded and instance.status == 'active':
            instance.status = 'funded' 