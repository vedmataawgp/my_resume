from django.db.models import Sum, Count, Avg
from django.utils import timezone
import datetime
import calendar


def get_month_year_filter(request):
    """Helper function to get month and year from request params or use current month"""
    today = timezone.now().date()
    
    try:
        month = int(request.GET.get('month', today.month))
        year = int(request.GET.get('year', today.year))
        
        # Validate month and year
        if month < 1 or month > 12:
            month = today.month
        if year < 2000 or year > 2100:
            year = today.year
    except (ValueError, TypeError):
        month = today.month
        year = today.year
    
    return month, year


def get_spending_suggestions(user):
    """Generate smart spending suggestions based on user's expense patterns"""
    today = timezone.now().date()
    suggestions = []
    
    # Get this month's expenses
    current_month_expenses = user.expense_set.filter(
        date__year=today.year,
        date__month=today.month
    )
    
    # Get previous month's expenses
    if today.month == 1:
        prev_month = 12
        prev_year = today.year - 1
    else:
        prev_month = today.month - 1
        prev_year = today.year
        
    prev_month_expenses = user.expense_set.filter(
        date__year=prev_year,
        date__month=prev_month
    )
    
    # 1. Look for categories with higher spending this month
    if prev_month_expenses.exists():
        current_by_category = current_month_expenses.values('category__name').annotate(
            total=Sum('amount')
        )
        prev_by_category = prev_month_expenses.values('category__name').annotate(
            total=Sum('amount')
        )
        
        # Convert to dict for easier comparison
        current_dict = {item['category__name']: item['total'] for item in current_by_category}
        prev_dict = {item['category__name']: item['total'] for item in prev_by_category}
        
        # Compare and find significant increases
        for category, current_amount in current_dict.items():
            if category in prev_dict:
                prev_amount = prev_dict[category]
                if current_amount > prev_amount * 1.2:  # 20% increase
                    increase = current_amount - prev_amount
                    suggestions.append(
                        f"You've spent ${increase:.2f} more on {category} this month compared to last month."
                    )
    
    # 2. Check for frequent small expenses (e.g., coffee)
    coffee_keywords = ['coffee', 'cafe', 'starbucks', 'dunkin', 'tim hortons']
    coffee_expenses = current_month_expenses.filter(
        description__iregex=r'(' + '|'.join(coffee_keywords) + ')'
    )
    
    if coffee_expenses.exists():
        coffee_total = coffee_expenses.aggregate(Sum('amount'))['amount__sum'] or 0
        coffee_count = coffee_expenses.count()
        
        if coffee_total > 50:  # Arbitrary threshold
            suggestions.append(
                f"You spent ${coffee_total:.2f} on coffee this month. Making coffee at home could save you around ${coffee_total * 0.7:.2f}."
            )
    
    # 3. Check for entertainment/dining out spending
    entertainment_categories = ['Entertainment', 'Dining', 'Food']
    entertainment_expenses = current_month_expenses.filter(
        category__name__in=entertainment_categories
    )
    
    if entertainment_expenses.exists():
        entertainment_total = entertainment_expenses.aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Get total expenses
        total_expenses = current_month_expenses.aggregate(Sum('amount'))['amount__sum'] or 0
        
        if total_expenses > 0:
            entertainment_percentage = (entertainment_total / total_expenses) * 100
            
            if entertainment_percentage > 30:  # If more than 30% spent on entertainment
                suggestions.append(
                    f"Entertainment and dining make up {entertainment_percentage:.1f}% of your expenses. Consider reducing this to 20% to increase your savings."
                )
    
    # 4. Look for "luxury" tagged expenses
    luxury_expenses = current_month_expenses.filter(tag='luxury')
    if luxury_expenses.exists():
        luxury_total = luxury_expenses.aggregate(Sum('amount'))['amount__sum'] or 0
        
        if luxury_total > 100:  # Arbitrary threshold
            suggestions.append(
                f"You spent ${luxury_total:.2f} on luxury items this month. Consider if all these purchases were necessary."
            )
    
    # 5. Check budget adherence
    from .models import Budget
    
    budgets = Budget.objects.filter(
        user=user,
        month=today.month,
        year=today.year
    )
    
    for budget in budgets:
        spent = budget.get_spent_amount()
        if spent > budget.amount:
            overspent = spent - budget.amount
            suggestions.append(
                f"You've exceeded your {budget.category.name} budget by ${overspent:.2f}."
            )
    
    # If no specific suggestions, add general savings tip
    if not suggestions:
        general_tips = [
            "Track your expenses daily for better awareness of your spending habits.",
            "Try the 50/30/20 rule: 50% needs, 30% wants, 20% savings.",
            "Set up automatic transfers to a savings account when you receive income.",
            "Compare prices before making large purchases to get the best deals.",
            "Consider meal planning to reduce food waste and save on groceries."
        ]
        import random
        suggestions.append(random.choice(general_tips))
    
    return suggestions[:3]  # Return top 3 suggestions
