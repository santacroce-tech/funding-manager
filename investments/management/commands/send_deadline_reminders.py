from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from investments.models import Opportunity
from investments.services import EmailService


class Command(BaseCommand):
    help = 'Send deadline reminders for opportunities that are approaching their deadline'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days-ahead',
            type=int,
            default=3,
            help='Number of days ahead to send reminders (default: 3)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be sent without actually sending emails'
        )

    def handle(self, *args, **options):
        days_ahead = options['days_ahead']
        dry_run = options['dry_run']
        
        # Calculate the deadline threshold
        threshold_date = timezone.now() + timedelta(days=days_ahead)
        
        # Get opportunities that are approaching their deadline
        opportunities = Opportunity.objects.filter(
            status='active',
            deadline__lte=threshold_date,
            deadline__gt=timezone.now()
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Found {opportunities.count()} opportunities with deadlines approaching within {days_ahead} days'
            )
        )
        
        if dry_run:
            self.stdout.write('DRY RUN - No emails will be sent')
        
        for opportunity in opportunities:
            self.stdout.write(f'Processing opportunity: {opportunity.title}')
            
            if not dry_run:
                EmailService.send_deadline_reminder(opportunity)
                self.stdout.write(
                    self.style.SUCCESS(f'Sent deadline reminders for {opportunity.title}')
                )
            else:
                self.stdout.write(f'Would send deadline reminders for {opportunity.title}')
        
        self.stdout.write(
            self.style.SUCCESS('Deadline reminder process completed')
        ) 