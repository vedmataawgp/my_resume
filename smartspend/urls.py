from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'smartspend'  # Define the namespace here

urlpatterns = [
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    
    # Password reset
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
    # Dashboard and home
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    
    # Expense management
    path('expenses/', views.list_expenses, name='list_expenses'),
    path('expenses/add/', views.add_expense, name='add_expense'),
    path('expenses/edit/<int:expense_id>/', views.edit_expense, name='edit_expense'),
    path('expenses/delete/<int:expense_id>/', views.delete_expense, name='delete_expense'),
    
    # Income management
    path('income/', views.list_incomes, name='list_incomes'),
    path('income/add/', views.add_income, name='add_income'),
    path('income/edit/<int:income_id>/', views.edit_income, name='edit_income'),
    path('income/delete/<int:income_id>/', views.delete_income, name='delete_income'),
    
    # Budget management
    path('budget/', views.budget_planner, name='budget_planner'),
    path('budget/add/', views.add_budget, name='add_budget'),
    path('budget/edit/<int:budget_id>/', views.edit_budget, name='edit_budget'),
    path('budget/delete/<int:budget_id>/', views.delete_budget, name='delete_budget'),
    
    # Savings goals
    path('savings/', views.savings_goals, name='savings_goals'),
    path('savings/add/', views.add_savings_goal, name='add_savings_goal'),
    path('savings/edit/<int:goal_id>/', views.edit_savings_goal, name='edit_savings_goal'),
    path('savings/delete/<int:goal_id>/', views.delete_savings_goal, name='delete_savings_goal'),
    path('savings/update/<int:goal_id>/', views.update_savings_progress, name='update_savings_progress'),
    
    # Recurring expenses
    path('recurring/', views.recurring_expenses, name='recurring_expenses'),
    path('recurring/add/', views.add_recurring_expense, name='add_recurring_expense'),
    path('recurring/edit/<int:expense_id>/', views.edit_recurring_expense, name='edit_recurring_expense'),
    path('recurring/delete/<int:expense_id>/', views.delete_recurring_expense, name='delete_recurring_expense'),
    path('recurring/toggle/<int:expense_id>/', views.toggle_recurring_expense, name='toggle_recurring_expense'),
    
    # Reports and analysis
    path('reports/', views.reports, name='reports'),
    path('reports/export/', views.export_data, name='export_data'),
    
    # Profile
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    
    # API endpoints for charts
    path('api/expense-by-category/', views.expense_by_category, name='expense_by_category'),
    path('api/income-vs-expense/', views.income_vs_expense, name='income_vs_expense'),
    path('api/daily-expense-trend/', views.daily_expense_trend, name='daily_expense_trend'),
]
