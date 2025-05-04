from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Count
from django.db.models.functions import TruncDay, TruncMonth
from .models import (
    Category, Expense, Income, Budget, SavingsGoal, 
    RecurringExpense, FinancialTip
)
from .forms import (
    RegisterForm, ExpenseForm, IncomeForm, BudgetForm, 
    SavingsGoalForm, RecurringExpenseForm, DateRangeForm, ProfileUpdateForm
)
from .utils import get_spending_suggestions, get_month_year_filter
from .filters import ExpenseFilter, IncomeFilter
import calendar
import csv
import datetime
from django.utils import timezone


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful. Welcome to SmartSpend!")
            
            # Create default categories for new user
            default_categories = [
                ('Food', 'fa-solid fa-utensils'),
                ('Transportation', 'fa-solid fa-car'),
                ('Housing', 'fa-solid fa-home'),
                ('Entertainment', 'fa-solid fa-film'),
                ('Shopping', 'fa-solid fa-shopping-bag'),
                ('Utilities', 'fa-solid fa-bolt'),
                ('Health', 'fa-solid fa-heartbeat'),
                ('Education', 'fa-solid fa-graduation-cap'),
                ('Travel', 'fa-solid fa-plane'),
                ('Other', 'fa-solid fa-receipt')
            ]
            
            for name, icon in default_categories:
                Category.objects.create(name=name, icon=icon)
                
            return redirect('smartspend:dashboard')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def dashboard(request):
    today = timezone.now().date()
    month_start = today.replace(day=1)
    
    # Get expense data for the current month
    current_month_expenses = Expense.objects.filter(
        user=request.user,
        date__year=today.year,
        date__month=today.month
    )
    
    # Split expenses by type
    fixed_expenses = current_month_expenses.filter(expense_type='fixed').order_by('-date')
    daily_expenses = current_month_expenses.filter(expense_type='daily').order_by('-date')
    
    # Calculate totals
    total_expense = current_month_expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    total_fixed_expense = fixed_expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    total_daily_expense = daily_expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    
    total_income = Income.objects.filter(
        user=request.user,
        date__year=today.year,
        date__month=today.month
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # For savings calculation
    total_savings = total_income - total_expense
    
    # Get expenses by category
    expenses_by_category = current_month_expenses.values(
        'category__name', 'category__icon'
    ).annotate(total=Sum('amount'))
    
    # Get recent fixed and daily expenses 
    recent_fixed_expenses = fixed_expenses[:5]
    recent_daily_expenses = daily_expenses[:5]
    
    # Get upcoming recurring expenses
    upcoming_recurring = RecurringExpense.objects.filter(
        user=request.user,
        is_active=True
    ).order_by('start_date')[:5]
    
    # Get budget progress
    budgets = Budget.objects.filter(
        user=request.user,
        month=today.month,
        year=today.year
    )
    
    # Get savings goals
    savings_goals = SavingsGoal.objects.filter(
        user=request.user,
        is_achieved=False
    )
    
    # Get random financial tip
    tip = FinancialTip.objects.order_by('?').first()
    
    # Get spending suggestions
    spending_suggestions = get_spending_suggestions(request.user)
    
    context = {
        'total_expense': total_expense,
        'total_fixed_expense': total_fixed_expense,
        'total_daily_expense': total_daily_expense,
        'total_income': total_income,
        'total_savings': total_savings,
        'expenses_by_category': expenses_by_category,
        'fixed_expenses': recent_fixed_expenses,
        'daily_expenses': recent_daily_expenses,
        'upcoming_recurring': upcoming_recurring,
        'budgets': budgets,
        'savings_goals': savings_goals,
        'financial_tip': tip,
        'suggestions': spending_suggestions,
        'month_name': calendar.month_name[today.month],
        'year': today.year,
    }
    
    return render(request, 'smartspend/dashboard.html', context)


@login_required
def add_expense(request):
    categories = Category.objects.all()
    
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                expense = form.save(commit=False)
                expense.user = request.user
                expense.save()
                
                expense_type = form.cleaned_data.get('expense_type', 'daily')
                success_message = f"{expense_type.title()} expense added successfully!"
                messages.success(request, success_message)
                
                # Redirect based on where the user came from
                next_url = request.POST.get('next', None)
                if not next_url:
                    next_url = 'smartspend:dashboard'  # Use the namespaced URL
                return redirect(next_url)
            except Exception as e:
                print(f"Error saving expense: {str(e)}")
                messages.error(request, f"Error adding expense: {str(e)}")
        else:
            print(f"Form errors: {form.errors}")
            messages.error(request, "Please correct the errors in the form.")
    else:
        initial_data = {}
        expense_type = request.GET.get('expense_type')
        if expense_type in ['fixed', 'daily']:
            initial_data['expense_type'] = expense_type
            
        form = ExpenseForm(initial=initial_data)
    
    context = {
        'form': form,
        'categories': categories,
        'next': request.GET.get('next', 'smartspend:dashboard'),  # Default to dashboard
        'expense_type': request.GET.get('expense_type', '')
    }
    
    return render(request, 'smartspend/add_expense.html', context)


@login_required
def edit_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)
    
    if request.method == 'POST':
        form = ExpenseForm(request.POST, request.FILES, instance=expense)
        if form.is_valid():
            try:
                form.save()
                expense_type = form.cleaned_data.get('expense_type', 'daily')
                messages.success(request, f"{expense_type.title()} expense updated successfully!")
                return redirect('smartspend:list_expenses')
            except Exception as e:
                print(f"Error updating expense: {str(e)}")
                messages.error(request, f"Error updating expense: {str(e)}")
        else:
            print(f"Form errors: {form.errors}")
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = ExpenseForm(instance=expense)
    
    return render(request, 'smartspend/add_expense.html', {
        'form': form,
        'expense': expense,
        'expense_type': expense.expense_type,  # Pass the current expense type
        'edit_mode': True
    })


@login_required
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)
    expense.delete()
    messages.success(request, "Expense deleted successfully!")
    return redirect('smartspend:list_expenses')


@login_required
def list_expenses(request):
    expenses = Expense.objects.filter(user=request.user)
    
    # Filter by expense type if provided
    expense_type = request.GET.get('expense_type')
    if expense_type in ['fixed', 'daily']:
        expenses = expenses.filter(expense_type=expense_type)
        
    expenses = expenses.order_by('-date')
    
    # Filter expenses
    expense_filter = ExpenseFilter(request.GET, queryset=expenses)
    
    # Calculate the total amount
    total_amount = expense_filter.qs.aggregate(Sum('amount'))['amount__sum'] or 0

    context = {
        'filter': expense_filter,
        'expense_type': expense_type,  # Pass to template for UI customization
        'total_amount': total_amount,  # Pass the total amount to the template
    }
    
    return render(request, 'smartspend/list_expenses.html', context)


@login_required
def add_income(request):
    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            income = form.save(commit=False)
            income.user = request.user
            income.save()
            messages.success(request, "Income added successfully!")
            
            # Redirect based on where the user came from
            next_url = request.POST.get('next', 'smartspend:dashboard')
            return redirect(next_url)
    else:
        form = IncomeForm()
    
    return render(request, 'smartspend/add_income.html', {
        'form': form,
        'next': request.GET.get('next', 'smartspend:dashboard')
    })


@login_required
def edit_income(request, income_id):
    income = get_object_or_404(Income, id=income_id, user=request.user)
    
    if request.method == 'POST':
        form = IncomeForm(request.POST, instance=income)
        if form.is_valid():
            form.save()
            messages.success(request, "Income updated successfully!")
            return redirect('smartspend:list_incomes')
    else:
        form = IncomeForm(instance=income)
    
    return render(request, 'smartspend/add_income.html', {
        'form': form,
        'income': income,
        'edit_mode': True
    })


@login_required
def delete_income(request, income_id):
    income = get_object_or_404(Income, id=income_id, user=request.user)
    income.delete()
    messages.success(request, "Income deleted successfully!")
    return redirect('smartspend:list_incomes')


@login_required
def list_incomes(request):
    incomes = Income.objects.filter(user=request.user).order_by('-date')
    
    # Filter incomes
    income_filter = IncomeFilter(request.GET, queryset=incomes)
    
    return render(request, 'smartspend/list_incomes.html', {
        'filter': income_filter,
    })


@login_required
def budget_planner(request):
    today = timezone.now().date()
    month, year = get_month_year_filter(request)
    
    # Get all budgets for the selected month
    budgets = Budget.objects.filter(
        user=request.user,
        month=month,
        year=year
    )
    
    # Get categories that don't have a budget yet
    existing_categories = budgets.values_list('category_id', flat=True)
    available_categories = Category.objects.exclude(id__in=existing_categories)
    
    context = {
        'budgets': budgets,
        'available_categories': available_categories,
        'current_month': month,
        'current_year': year,
        'month_name': calendar.month_name[month],
    }
    
    return render(request, 'smartspend/budget_planner.html', context)


@login_required
def add_budget(request):
    if request.method == 'POST':
        form = BudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            
            # Check if budget already exists for this category/month/year
            try:
                existing_budget = Budget.objects.get(
                    user=request.user,
                    category=budget.category,
                    month=budget.month,
                    year=budget.year
                )
                # Update existing budget
                existing_budget.amount = budget.amount
                existing_budget.save()
                messages.success(request, "Budget updated successfully!")
            except Budget.DoesNotExist:
                # Create new budget
                budget.save()
                messages.success(request, "Budget added successfully!")
                
            return redirect('smartspend:budget_planner')
    else:
        # Default to current month/year
        today = timezone.now().date()
        form = BudgetForm(initial={'month': today.month, 'year': today.year})
    
    return render(request, 'smartspend/add_budget.html', {'form': form})


@login_required
def edit_budget(request, budget_id):
    budget = get_object_or_404(Budget, id=budget_id, user=request.user)
    
    if request.method == 'POST':
        form = BudgetForm(request.POST, instance=budget)
        if form.is_valid():
            form.save()
            messages.success(request, "Budget updated successfully!")
            return redirect('smartspend:budget_planner')
    else:
        form = BudgetForm(instance=budget)
    
    return render(request, 'smartspend/add_budget.html', {
        'form': form,
        'budget': budget,
        'edit_mode': True
    })


@login_required
def delete_budget(request, budget_id):
    budget = get_object_or_404(Budget, id=budget_id, user=request.user)
    budget.delete()
    messages.success(request, "Budget deleted successfully!")
    return redirect('smartspend:budget_planner')


@login_required
def savings_goals(request):
    goals = SavingsGoal.objects.filter(user=request.user).order_by('target_date')
    
    # Separate active and achieved goals
    active_goals = goals.filter(is_achieved=False)
    achieved_goals = goals.filter(is_achieved=True)
    
    context = {
        'active_goals': active_goals,
        'achieved_goals': achieved_goals,
    }
    
    return render(request, 'smartspend/savings_goals.html', context)


@login_required
def add_savings_goal(request):
    if request.method == 'POST':
        form = SavingsGoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.user = request.user
            
            # Check if achieved
            if goal.current_amount >= goal.target_amount:
                goal.is_achieved = True
                
            goal.save()
            messages.success(request, "Savings goal added successfully!")
            return redirect('smartspend:savings_goals')
    else:
        form = SavingsGoalForm()
    
    return render(request, 'smartspend/add_savings_goal.html', {'form': form})


@login_required
def edit_savings_goal(request, goal_id):
    goal = get_object_or_404(SavingsGoal, id=goal_id, user=request.user)
    
    if request.method == 'POST':
        form = SavingsGoalForm(request.POST, instance=goal)
        if form.is_valid():
            goal = form.save(commit=False)
            
            # Check if achieved
            if goal.current_amount >= goal.target_amount:
                goal.is_achieved = True
            else:
                goal.is_achieved = False
                
            goal.save()
            messages.success(request, "Savings goal updated successfully!")
            return redirect('smartspend:savings_goals')
    else:
        form = SavingsGoalForm(instance=goal)
    
    return render(request, 'smartspend/add_savings_goal.html', {
        'form': form,
        'goal': goal,
        'edit_mode': True
    })


@login_required
def delete_savings_goal(request, goal_id):
    goal = get_object_or_404(SavingsGoal, id=goal_id, user=request.user)
    goal.delete()
    messages.success(request, "Savings goal deleted successfully!")
    return redirect('smartspend:savings_goals')


@login_required
def update_savings_progress(request, goal_id):
    goal = get_object_or_404(SavingsGoal, id=goal_id, user=request.user)
    
    if request.method == 'POST':
        # Get the amount to add
        try:
            amount = float(request.POST.get('amount', 0))
            
            if amount > 0:
                goal.current_amount += amount
                
                # Check if achieved
                if goal.current_amount >= goal.target_amount:
                    goal.is_achieved = True
                    
                goal.save()
                messages.success(request, f"Added ₹{amount:.2f} to your savings goal!")
            else:
                messages.error(request, "Please enter a positive amount.")
        except ValueError:
            messages.error(request, "Please enter a valid number.")
            
    return redirect('smartspend:savings_goals')


@login_required
def recurring_expenses(request):
    expenses = RecurringExpense.objects.filter(user=request.user).order_by('title')
    
    # Separate active and inactive
    active_expenses = expenses.filter(is_active=True)
    inactive_expenses = expenses.filter(is_active=False)
    
    context = {
        'active_expenses': active_expenses,
        'inactive_expenses': inactive_expenses,
    }
    
    return render(request, 'smartspend/recurring_expenses.html', context)


@login_required
def add_recurring_expense(request):
    if request.method == 'POST':
        form = RecurringExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, "Recurring expense added successfully!")
            return redirect('smartspend:recurring_expenses')
    else:
        form = RecurringExpenseForm(initial={'start_date': timezone.now().date()})
    
    categories = Category.objects.all()
    return render(request, 'smartspend/add_recurring_expense.html', {
        'form': form,
        'categories': categories
    })


@login_required
def edit_recurring_expense(request, expense_id):
    expense = get_object_or_404(RecurringExpense, id=expense_id, user=request.user)
    
    if request.method == 'POST':
        form = RecurringExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, "Recurring expense updated successfully!")
            return redirect('smartspend:recurring_expenses')
    else:
        form = RecurringExpenseForm(instance=expense)
    
    categories = Category.objects.all()
    return render(request, 'smartspend/add_recurring_expense.html', {
        'form': form,
        'expense': expense,
        'categories': categories,
        'edit_mode': True
    })


@login_required
def delete_recurring_expense(request, expense_id):
    expense = get_object_or_404(RecurringExpense, id=expense_id, user=request.user)
    expense.delete()
    messages.success(request, "Recurring expense deleted successfully!")
    return redirect('smartspend:recurring_expenses')


@login_required
def toggle_recurring_expense(request, expense_id):
    expense = get_object_or_404(RecurringExpense, id=expense_id, user=request.user)
    expense.is_active = not expense.is_active
    expense.save()
    
    status = "activated" if expense.is_active else "deactivated"
    messages.success(request, f"Recurring expense {status} successfully!")
    
    return redirect('smartspend:recurring_expenses')


@login_required
def reports(request):
    # Get date range from request, default to current month
    today = timezone.now().date()
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if not start_date:
        start_date = today.replace(day=1)
    else:
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        
    if not end_date:
        # Last day of current month
        if today.month == 12:
            end_date = today.replace(day=31)
        else:
            end_date = today.replace(month=today.month+1, day=1) - datetime.timedelta(days=1)
    else:
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Get expenses and income for selected period
    expenses = Expense.objects.filter(
        user=request.user,
        date__range=[start_date, end_date]
    )
    
    incomes = Income.objects.filter(
        user=request.user,
        date__range=[start_date, end_date]
    )
    
    # Total expenses and income
    total_expense = expenses.aggregate(Sum('amount'))['amount__sum'] or 0
    total_income = incomes.aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Category breakdown
    category_expenses = expenses.values('category__name').annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    # Tag breakdown
    tag_expenses = expenses.values('tag').annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    # Daily breakdown
    daily_expenses = expenses.annotate(
        day=TruncDay('date')
    ).values('day').annotate(
        total=Sum('amount')
    ).order_by('day')
    
    form = DateRangeForm(initial={
        'start_date': start_date,
        'end_date': end_date
    })
    
    context = {
        'form': form,
        'total_expense': total_expense,
        'total_income': total_income,
        'category_expenses': category_expenses,
        'tag_expenses': tag_expenses,
        'daily_expenses': daily_expenses,
        'start_date': start_date,
        'end_date': end_date,
        'net_savings': total_income - total_expense
    }
    
    return render(request, 'smartspend/reports.html', context)


@login_required
def export_data(request):
    # Get date range from request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date and end_date:
        start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Get expenses for selected period
        expenses = Expense.objects.filter(
            user=request.user,
            date__range=[start_date, end_date]
        ).order_by('date')
        
        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="expenses_{start_date}_to_{end_date}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Date', 'Amount', 'Category', 'Description', 'Tag'])
        
        for expense in expenses:
            writer.writerow([
                expense.date,
                expense.amount,
                expense.category.name if expense.category else 'No Category',
                expense.description,
                expense.tag
            ])
            
        return response
    
    # If no date range, return to reports
    messages.error(request, "Please select a date range to export.")
    return redirect('reports')


@login_required
def profile(request):
    user = request.user
    context = {
        'user': user,
    }
    return render(request, 'smartspend/profile.html', context)


@login_required
def update_profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('smartspend:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    return render(request, 'smartspend/profile.html', {'form': form})


# API endpoints for chart data
@login_required
def expense_by_category(request):
    month, year = get_month_year_filter(request)
    
    # Get expense data grouped by category
    expenses = Expense.objects.filter(
        user=request.user,
        date__year=year,
        date__month=month
    ).values('category__name').annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    # Format for Chart.js
    labels = [item['category__name'] or 'Uncategorized' for item in expenses]
    data = [float(item['total']) for item in expenses]
    
    return JsonResponse({
        'labels': labels,
        'datasets': [{
            'label': 'Expenses by Category',
            'data': data,
            'backgroundColor': [
                '#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b',
                '#858796', '#5a5c69', '#6610f2', '#6f42c1', '#fd7e14',
            ],
        }]
    })


@login_required
def income_vs_expense(request):
    # Get last 6 months data
    today = timezone.now().date()
    months_data = []
    
    for i in range(5, -1, -1):
        # Calculate month and year
        month_date = (today.replace(day=1) - datetime.timedelta(days=1))
        month_date = month_date.replace(day=1)
        month_date = month_date - datetime.timedelta(days=(i * 30))
        
        month = month_date.month
        year = month_date.year
        
        # Get expenses and income for this month
        monthly_expense = Expense.objects.filter(
            user=request.user,
            date__year=year,
            date__month=month
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        monthly_income = Income.objects.filter(
            user=request.user,
            date__year=year,
            date__month=month
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        # Calculate savings
        monthly_savings = monthly_income - monthly_expense
        
        # Add to data
        months_data.append({
            'month': calendar.month_name[month][:3],
            'expense': float(monthly_expense),
            'income': float(monthly_income),
            'savings': float(monthly_savings)
        })
    
    # Format for Chart.js
    labels = [item['month'] for item in months_data]
    expense_data = [item['expense'] for item in months_data]
    income_data = [item['income'] for item in months_data]
    savings_data = [item['savings'] for item in months_data]
    
    return JsonResponse({
        'labels': labels,
        'datasets': [
            {
                'label': 'Income',
                'data': income_data,
                'backgroundColor': 'rgba(28, 200, 138, 0.2)',
                'borderColor': 'rgb(28, 200, 138)',
                'borderWidth': 2,
            },
            {
                'label': 'Expense',
                'data': expense_data,
                'backgroundColor': 'rgba(231, 74, 59, 0.2)',
                'borderColor': 'rgb(231, 74, 59)',
                'borderWidth': 2,
            },
            {
                'label': 'Savings',
                'data': savings_data,
                'backgroundColor': 'rgba(54, 185, 204, 0.2)',
                'borderColor': 'rgb(54, 185, 204)',
                'borderWidth': 2,
            }
        ]
    })


@login_required
def daily_expense_trend(request):
    month, year = get_month_year_filter(request)
    
    # Get start and end dates for the selected month
    start_date = datetime.date(year, month, 1)
    if month == 12:
        end_date = datetime.date(year + 1, 1, 1) - datetime.timedelta(days=1)
    else:
        end_date = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)
    
    # Get daily expense data
    daily_expenses = Expense.objects.filter(
        user=request.user,
        date__gte=start_date,
        date__lte=end_date
    ).annotate(
        day=TruncDay('date')
    ).values('day').annotate(
        total=Sum('amount')
    ).order_by('day')
    
    # Create a list of all days in the month
    all_days = []
    current_date = start_date
    while current_date <= end_date:
        all_days.append(current_date)
        current_date += datetime.timedelta(days=1)
    
    # Format for Chart.js
    data = []
    for day in all_days:
        # Look for matching expense data
        day_expense = next(
            (item for item in daily_expenses if item['day'] == day), 
            {'total': 0}
        )
        data.append({
            'x': day.strftime('%Y-%m-%d'),
            'y': float(day_expense['total'])
        })
    
    return JsonResponse({
        'datasets': [{
            'label': 'Daily Expenses',
            'data': data,
            'backgroundColor': 'rgba(78, 115, 223, 0.2)',
            'borderColor': 'rgb(78, 115, 223)',
            'borderWidth': 2,
            'tension': 0.3,
            'fill': True,
        }]
    })
