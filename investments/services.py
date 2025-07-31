import uuid
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from .models import EmailNotification, Wallet, Investment, Opportunity


class EmailService:
    """Service for handling email notifications to investors"""
    
    @staticmethod
    def send_investment_created_notification(investment):
        """Send notification when investment is created"""
        subject = f"Investment Opportunity: {investment.opportunity.title}"
        
        context = {
            'investor': investment.investor,
            'investment': investment,
            'opportunity': investment.opportunity,
            'deadline': investment.opportunity.deadline,
        }
        
        message = render_to_string('investments/emails/investment_created.html', context)
        
        # Create email notification record
        notification = EmailNotification.objects.create(
            investor=investment.investor,
            opportunity=investment.opportunity,
            investment=investment,
            notification_type='investment_created',
            subject=subject,
            message=message
        )
        
        # Send email
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[investment.investor.email],
                fail_silently=False,
            )
            notification.is_sent = True
            notification.save()
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
    
    @staticmethod
    def send_investment_updated_notification(investment):
        """Send notification when investment is updated"""
        subject = f"Investment Update: {investment.opportunity.title}"
        
        context = {
            'investor': investment.investor,
            'investment': investment,
            'opportunity': investment.opportunity,
        }
        
        message = render_to_string('investments/emails/investment_updated.html', context)
        
        notification = EmailNotification.objects.create(
            investor=investment.investor,
            opportunity=investment.opportunity,
            investment=investment,
            notification_type='investment_updated',
            subject=subject,
            message=message
        )
        
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[investment.investor.email],
                fail_silently=False,
            )
            notification.is_sent = True
            notification.save()
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
    
    @staticmethod
    def send_deadline_reminder(opportunity):
        """Send deadline reminders to investors"""
        # Get all investors for this opportunity
        investments = Investment.objects.filter(opportunity=opportunity, status='pending')
        
        for investment in investments:
            subject = f"Deadline Reminder: {opportunity.title}"
            
            context = {
                'investor': investment.investor,
                'investment': investment,
                'opportunity': opportunity,
                'deadline': opportunity.deadline,
            }
            
            message = render_to_string('investments/emails/deadline_reminder.html', context)
            
            notification = EmailNotification.objects.create(
                investor=investment.investor,
                opportunity=opportunity,
                investment=investment,
                notification_type='deadline_reminder',
                subject=subject,
                message=message
            )
            
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[investment.investor.email],
                    fail_silently=False,
                )
                notification.is_sent = True
                notification.save()
            except Exception as e:
                print(f"Failed to send deadline reminder: {e}")
    
    @staticmethod
    def send_opportunity_update_notification(opportunity):
        """Send notification when opportunity is updated"""
        investments = Investment.objects.filter(opportunity=opportunity)
        
        for investment in investments:
            subject = f"Opportunity Update: {opportunity.title}"
            
            context = {
                'investor': investment.investor,
                'investment': investment,
                'opportunity': opportunity,
            }
            
            message = render_to_string('investments/emails/opportunity_update.html', context)
            
            notification = EmailNotification.objects.create(
                investor=investment.investor,
                opportunity=opportunity,
                investment=investment,
                notification_type='opportunity_update',
                subject=subject,
                message=message
            )
            
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[investment.investor.email],
                    fail_silently=False,
                )
                notification.is_sent = True
                notification.save()
            except Exception as e:
                print(f"Failed to send opportunity update: {e}")


class WalletService:
    """Service for generating and managing wallets"""
    
    @staticmethod
    def generate_wallet_address(wallet_type):
        """Generate a wallet address for the specified type"""
        # This is a placeholder implementation
        # In a real application, you would integrate with a wallet service
        # like Coinbase Commerce, BitGo, or similar
        
        # For demo purposes, we'll generate a UUID-based address
        address = str(uuid.uuid4()).replace('-', '')
        
        # Add prefix based on wallet type
        if wallet_type == 'BTC':
            address = 'bc1' + address[:40]
        elif wallet_type == 'ETH':
            address = '0x' + address[:40]
        elif wallet_type in ['USDT', 'USDC']:
            address = '0x' + address[:40]  # ERC-20 tokens use Ethereum addresses
        
        return address
    
    @staticmethod
    def create_wallet_for_investor(investor, wallet_type):
        """Create a wallet for an investor"""
        address = WalletService.generate_wallet_address(wallet_type)
        
        wallet = Wallet.objects.create(
            address=address,
            wallet_type=wallet_type
        )
        
        investor.wallet = wallet
        investor.save()
        
        return wallet


class InvestmentService:
    """Service for managing investments"""
    
    @staticmethod
    def create_investment(opportunity, investor, amount, currency):
        """Create a new investment and send notification"""
        investment = Investment.objects.create(
            opportunity=opportunity,
            investor=investor,
            amount=amount,
            currency=currency
        )
        
        # Send notification
        EmailService.send_investment_created_notification(investment)
        
        return investment
    
    @staticmethod
    def update_investment_status(investment, status, transaction_hash=None):
        """Update investment status and send notification"""
        old_status = investment.status
        investment.status = status
        
        if transaction_hash:
            investment.transaction_hash = transaction_hash
        
        investment.save()
        
        # Send notification if status changed
        if old_status != status:
            EmailService.send_investment_updated_notification(investment)
        
        return investment
    
    @staticmethod
    def get_opportunity_summary(opportunity):
        """Get summary statistics for an opportunity"""
        investments = Investment.objects.filter(opportunity=opportunity)
        
        total_investors = investments.count()
        confirmed_investments = investments.filter(status='confirmed')
        total_confirmed_amount = sum(inv.amount for inv in confirmed_investments)
        
        return {
            'total_investors': total_investors,
            'confirmed_investments': confirmed_investments.count(),
            'total_confirmed_amount': total_confirmed_amount,
            'progress_percentage': opportunity.progress_percentage,
            'is_funded': opportunity.is_funded,
            'is_expired': opportunity.is_expired,
        } 