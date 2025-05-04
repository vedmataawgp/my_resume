from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Expense, Income, Budget, SavingsGoal, RecurringExpense, Category


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class ExpenseForm(forms.ModelForm):
    receipt_image = forms.ImageField(required=False)
    
    class Meta:
        model = Expense
        fields = ['amount', 'date', 'category', 'description', 'tag', 'receipt_image', 'expense_type']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.TextInput(attrs={'placeholder': 'What did you spend on?'}),
            'expense_type': forms.RadioSelect(),
        }


class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['amount', 'date', 'source', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'source': forms.TextInput(attrs={'placeholder': 'Source of income'}),
            'description': forms.TextInput(attrs={'placeholder': 'Additional notes'}),
        }


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['category', 'amount', 'month', 'year']
        widgets = {
            'month': forms.Select(choices=[(i, i) for i in range(1, 13)]),
            'year': forms.Select(choices=[(i, i) for i in range(2023, 2031)]),
        }


class SavingsGoalForm(forms.ModelForm):
    class Meta:
        model = SavingsGoal
        fields = ['title', 'target_amount', 'current_amount', 'target_date']
        widgets = {
            'target_date': forms.DateInput(attrs={'type': 'date'}),
            'title': forms.TextInput(attrs={'placeholder': 'What are you saving for?'}),
        }


class RecurringExpenseForm(forms.ModelForm):
    class Meta:
        model = RecurringExpense
        fields = ['title', 'amount', 'category', 'frequency', 'start_date', 'is_active']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'title': forms.TextInput(attrs={'placeholder': 'Name of recurring expense'}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'icon']


class DateRangeForm(forms.Form):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
