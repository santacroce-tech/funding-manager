from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from investments.models import (
    Opportunity, Investor, Wallet, Investment, 
    MultiCurrencyInvestment, InvestmentComponent
)
from investments.services import WalletService


class Command(BaseCommand):
    help = 'Create sample data for testing the investment management system'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create sample opportunities
        opportunities = []
        
        # Opportunity 1: Bitcoin Mining Company
        opp1 = Opportunity.objects.create(
            title="Bitcoin Mining Expansion",
            description="Expanding our mining operations with new ASIC hardware to increase hash rate by 50%",
            company_name="CryptoMine Corp",
            country="United States",
            ticker_symbol="CRYPT",
            ticker_url="https://finance.yahoo.com/quote/CRYPT",
            data_room_url="https://dataroom.cryptomine.com",
            total_goal=Decimal('100.00000000'),
            currency='BTC',
            minimum_investment=Decimal('0.00100000'),
            deadline=timezone.now() + timedelta(days=30),
            status='active'
        )
        opportunities.append(opp1)
        self.stdout.write(f'Created opportunity: {opp1.title}')
        
        # Opportunity 2: DeFi Platform
        opp2 = Opportunity.objects.create(
            title="DeFi Lending Platform",
            description="Building a decentralized lending platform for cryptocurrency assets",
            company_name="DeFiLend Inc",
            country="Singapore",
            ticker_symbol="DEFI",
            ticker_url="https://finance.yahoo.com/quote/DEFI",
            data_room_url="https://dataroom.defilend.com",
            total_goal=Decimal('500.00000000'),
            currency='ETH',
            minimum_investment=Decimal('0.10000000'),
            deadline=timezone.now() + timedelta(days=45),
            status='active'
        )
        opportunities.append(opp2)
        self.stdout.write(f'Created opportunity: {opp2.title}')
        
        # Opportunity 3: NFT Marketplace
        opp3 = Opportunity.objects.create(
            title="NFT Marketplace Development",
            description="Creating a premium NFT marketplace with advanced features",
            company_name="NFTWorld Ltd",
            country="United Kingdom",
            ticker_symbol="NFTW",
            ticker_url="https://finance.yahoo.com/quote/NFTW",
            data_room_url="https://dataroom.nftworld.com",
            total_goal=Decimal('1000.00000000'),
            currency='USDT',
            minimum_investment=Decimal('100.00000000'),
            deadline=timezone.now() + timedelta(days=60),
            status='active'
        )
        opportunities.append(opp3)
        self.stdout.write(f'Created opportunity: {opp3.title}')
        
        # Create sample investors
        investors = []
        
        investor_data = [
            {'first_name': 'John', 'last_name': 'Smith', 'email': 'john.smith@example.com', 'phone': '+1-555-0101'},
            {'first_name': 'Sarah', 'last_name': 'Johnson', 'email': 'sarah.johnson@example.com', 'phone': '+1-555-0102'},
            {'first_name': 'Michael', 'last_name': 'Brown', 'email': 'michael.brown@example.com', 'phone': '+1-555-0103'},
            {'first_name': 'Emily', 'last_name': 'Davis', 'email': 'emily.davis@example.com', 'phone': '+1-555-0104'},
            {'first_name': 'David', 'last_name': 'Wilson', 'email': 'david.wilson@example.com', 'phone': '+1-555-0105'},
        ]
        
        for data in investor_data:
            investor = Investor.objects.create(**data)
            # Generate wallet for each investor
            wallet = WalletService.create_wallet_for_investor(investor, 'BTC')
            investors.append(investor)
            self.stdout.write(f'Created investor: {investor.full_name}')
        
        # Create sample single-currency investments
        investment_data = [
            # Bitcoin Mining investments
            {'opportunity': opp1, 'investor': investors[0], 'amount': Decimal('0.00500000'), 'currency': 'BTC', 'status': 'confirmed'},
            {'opportunity': opp1, 'investor': investors[1], 'amount': Decimal('0.00300000'), 'currency': 'BTC', 'status': 'pending'},
            {'opportunity': opp1, 'investor': investors[2], 'amount': Decimal('0.00200000'), 'currency': 'BTC', 'status': 'confirmed'},
            
            # DeFi Platform investments
            {'opportunity': opp2, 'investor': investors[0], 'amount': Decimal('0.50000000'), 'currency': 'ETH', 'status': 'confirmed'},
            {'opportunity': opp2, 'investor': investors[3], 'amount': Decimal('0.30000000'), 'currency': 'ETH', 'status': 'pending'},
            {'opportunity': opp2, 'investor': investors[4], 'amount': Decimal('0.20000000'), 'currency': 'ETH', 'status': 'confirmed'},
            
            # NFT Marketplace investments
            {'opportunity': opp3, 'investor': investors[1], 'amount': Decimal('500.00000000'), 'currency': 'USDT', 'status': 'confirmed'},
            {'opportunity': opp3, 'investor': investors[2], 'amount': Decimal('300.00000000'), 'currency': 'USDT', 'status': 'pending'},
            {'opportunity': opp3, 'investor': investors[3], 'amount': Decimal('200.00000000'), 'currency': 'USDT', 'status': 'confirmed'},
        ]
        
        for data in investment_data:
            investment = Investment.objects.create(**data)
            self.stdout.write(f'Created investment: {investment.investor.full_name} -> {investment.opportunity.title}')
        
        # Create sample multi-currency investments
        multi_investment_data = [
            {
                'opportunity': opp1,
                'investor': investors[0],
                'status': 'confirmed',
                'notes': 'Multi-currency investment with BTC and ETH',
                'components': [
                    {'amount': Decimal('0.00200000'), 'currency': 'BTC', 'transaction_hash': 'abc123btc'},
                    {'amount': Decimal('0.10000000'), 'currency': 'ETH', 'transaction_hash': 'def456eth'},
                ]
            },
            {
                'opportunity': opp2,
                'investor': investors[1],
                'status': 'pending',
                'notes': 'Mixed investment with ETH and USDT',
                'components': [
                    {'amount': Decimal('0.20000000'), 'currency': 'ETH', 'transaction_hash': 'ghi789eth'},
                    {'amount': Decimal('150.00000000'), 'currency': 'USDT', 'transaction_hash': 'jkl012usdt'},
                ]
            },
            {
                'opportunity': opp3,
                'investor': investors[2],
                'status': 'confirmed',
                'notes': 'Large multi-currency investment',
                'components': [
                    {'amount': Decimal('0.00100000'), 'currency': 'BTC', 'transaction_hash': 'mno345btc'},
                    {'amount': Decimal('0.50000000'), 'currency': 'ETH', 'transaction_hash': 'pqr678eth'},
                    {'amount': Decimal('250.00000000'), 'currency': 'USDT', 'transaction_hash': 'stu901usdt'},
                ]
            },
        ]
        
        for data in multi_investment_data:
            components = data.pop('components')
            multi_investment = MultiCurrencyInvestment.objects.create(**data)
            
            for component_data in components:
                InvestmentComponent.objects.create(
                    multi_currency_investment=multi_investment,
                    **component_data
                )
            
            self.stdout.write(f'Created multi-currency investment: {multi_investment.investor.full_name} -> {multi_investment.opportunity.title}')
        
        # Update opportunity current_raised based on confirmed investments
        for opportunity in opportunities:
            confirmed_investments = Investment.objects.filter(
                opportunity=opportunity, 
                status='confirmed'
            )
            total_confirmed = sum(inv.amount for inv in confirmed_investments)
            
            # Add confirmed multi-currency investments
            confirmed_multi_investments = MultiCurrencyInvestment.objects.filter(
                opportunity=opportunity,
                status='confirmed'
            )
            for multi_inv in confirmed_multi_investments:
                for component in multi_inv.components.all():
                    if component.currency == opportunity.currency:
                        total_confirmed += component.amount
            
            opportunity.current_raised = total_confirmed
            opportunity.save()
            self.stdout.write(f'Updated {opportunity.title}: {total_confirmed} {opportunity.currency} raised')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created sample data:\n'
                f'- {len(opportunities)} opportunities\n'
                f'- {len(investors)} investors\n'
                f'- {len(investment_data)} single-currency investments\n'
                f'- {len(multi_investment_data)} multi-currency investments'
            )
        ) 