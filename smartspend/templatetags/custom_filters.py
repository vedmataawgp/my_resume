from django import template
from decimal import Decimal
import calendar
from datetime import datetime

register = template.Library()

@register.filter(name='sub')
def subtract(value, arg):
    """Subtract the arg from the value."""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        try:
            return value - arg
        except Exception:
            return 0
        
@register.filter(name='multiply')
def multiply(value, arg):
    """Multiply the value by the arg."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        try:
            return value * arg
        except Exception:
            return 0
            
@register.filter(name='divide')
def divide(value, arg):
    """Divide the value by the arg."""
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter(name='percentage')
def percentage(value, total):
    """Calculate what percentage the value is of the total."""
    try:
        if not total or float(total) == 0:
            return 0
        return round((float(value) / float(total)) * 100, 1)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter(name='total_current_amount')
def total_current_amount(goals):
    """Calculate the total current amount across all savings goals."""
    try:
        if not goals:
            return 0
        return sum(goal.current_amount for goal in goals)
    except Exception:
        return 0

@register.filter(name='get_month_name')
def get_month_name(month_number):
    """Convert month number to month name."""
    try:
        month_number = int(month_number)
        if 1 <= month_number <= 12:
            return calendar.month_name[month_number]
        return "Invalid Month"
    except (ValueError, TypeError):
        return "Invalid Month"

@register.filter(name='split')
def split(value, arg):
    """Split a string by the provided delimiter."""
    try:
        return value.split(arg)
    except (AttributeError, TypeError):
        return [value]

@register.filter(name='monthly_total')
def monthly_total(expenses):
    """Calculate the monthly total for recurring expenses."""
    try:
        if not expenses:
            return 0
            
        total = 0
        for expense in expenses:
            if expense.frequency == 'monthly':
                total += float(expense.amount)
            elif expense.frequency == 'weekly':
                # Assuming 4.33 weeks in a month on average
                total += float(expense.amount) * 4.33
            elif expense.frequency == 'daily':
                # Assuming 30.44 days in a month on average
                total += float(expense.amount) * 30.44
            elif expense.frequency == 'quarterly':
                # Divide by 3 to get monthly amount
                total += float(expense.amount) / 3
            elif expense.frequency == 'yearly':
                # Divide by 12 to get monthly amount
                total += float(expense.amount) / 12
                
        return total
    except Exception:
        return 0