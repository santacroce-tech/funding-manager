from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from .models import Opportunity, Investor, Investment, Wallet
from .services import InvestmentService


def home(request):
    """Home page that redirects to dashboard"""
    return redirect('investments:dashboard')


@login_required
def dashboard(request):
    """Dashboard view showing investment statistics"""
    
    # Get basic statistics
    total_opportunities = Opportunity.objects.count()
    active_opportunities = Opportunity.objects.filter(status='active').count()
    total_investors = Investor.objects.count()
    total_investments = Investment.objects.count()
    confirmed_investments = Investment.objects.filter(status='confirmed').count()
    
    # Get total funding raised
    total_raised = Investment.objects.filter(status='confirmed').aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    # Get recent opportunities
    recent_opportunities = Opportunity.objects.all()[:5]
    
    # Get recent investments
    recent_investments = Investment.objects.select_related('investor', 'opportunity').all()[:10]
    
    # Get funding progress for active opportunities
    active_opportunities_list = Opportunity.objects.filter(status='active')
    
    context = {
        'total_opportunities': total_opportunities,
        'active_opportunities': active_opportunities,
        'total_investors': total_investors,
        'total_investments': total_investments,
        'confirmed_investments': confirmed_investments,
        'total_raised': total_raised,
        'recent_opportunities': recent_opportunities,
        'recent_investments': recent_investments,
        'active_opportunities_list': active_opportunities_list,
    }
    
    return render(request, 'investments/dashboard.html', context)
