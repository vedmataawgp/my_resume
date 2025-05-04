from django.contrib import admin
from .models import Category, Expense, Income, Budget, SavingsGoal, RecurringExpense, FinancialTip

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon')
    search_fields = ('name',)

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'category', 'date', 'description', 'tag')
    list_filter = ('user', 'category', 'date', 'tag')
    search_fields = ('description',)
    date_hierarchy = 'date'

@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'source', 'date', 'description')
    list_filter = ('user', 'date')
    search_fields = ('source', 'description')
    date_hierarchy = 'date'

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'amount', 'month', 'year')
    list_filter = ('user', 'category', 'month', 'year')

@admin.register(SavingsGoal)
class SavingsGoalAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'target_amount', 'current_amount', 'target_date', 'is_achieved')
    list_filter = ('user', 'is_achieved')
    search_fields = ('title',)

@admin.register(RecurringExpense)
class RecurringExpenseAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'amount', 'category', 'frequency', 'start_date', 'is_active')
    list_filter = ('user', 'category', 'frequency', 'is_active')
    search_fields = ('title',)

@admin.register(FinancialTip)
class FinancialTipAdmin(admin.ModelAdmin):
    list_display = ('title', 'category')
    list_filter = ('category',)
    search_fields = ('title', 'content')
