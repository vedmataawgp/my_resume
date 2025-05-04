import django_filters
from django import forms
from .models import Expense, Income, Category


class ExpenseFilter(django_filters.FilterSet):
    date_range = django_filters.DateFromToRangeFilter(
        field_name='date',
        label='Date Range',
        widget=django_filters.widgets.RangeWidget(attrs={'type': 'date'})
    )
    
    description = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Description contains'
    )
    
    amount_min = django_filters.NumberFilter(
        field_name='amount',
        lookup_expr='gte',
        label='Min Amount'
    )
    
    amount_max = django_filters.NumberFilter(
        field_name='amount',
        lookup_expr='lte',
        label='Max Amount'
    )
    
    expense_type = django_filters.ChoiceFilter(
        choices=Expense.EXPENSE_TYPE_CHOICES,
        label='Expense Type'
    )
    
    class Meta:
        model = Expense
        fields = ['category', 'tag', 'expense_type']


class IncomeFilter(django_filters.FilterSet):
    date_range = django_filters.DateFromToRangeFilter(
        field_name='date',
        label='Date Range',
        widget=django_filters.widgets.RangeWidget(attrs={'type': 'date'})
    )
    
    source = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Source contains'
    )
    
    description = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Description contains'
    )
    
    amount_min = django_filters.NumberFilter(
        field_name='amount',
        lookup_expr='gte',
        label='Min Amount'
    )
    
    amount_max = django_filters.NumberFilter(
        field_name='amount',
        lookup_expr='lte',
        label='Max Amount'
    )
    
    class Meta:
        model = Income
        fields = []
