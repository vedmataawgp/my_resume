from django.db import models
from django.contrib.auth.models import User
import datetime
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, default='fa-solid fa-receipt')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Expense(models.Model):
    TAG_CHOICES = [
        ('essential', 'Essential'),
        ('luxury', 'Luxury'),
        ('investment', 'Investment'),
        ('emergency', 'Emergency'),
    ]
    
    EXPENSE_TYPE_CHOICES = [
        ('fixed', 'Fixed Expense'),
        ('daily', 'Daily Expense'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    description = models.CharField(max_length=200)
    receipt_image = models.ImageField(upload_to='receipts/', null=True, blank=True)
    tag = models.CharField(max_length=20, choices=TAG_CHOICES, default='essential')
    expense_type = models.CharField(max_length=10, choices=EXPENSE_TYPE_CHOICES, default='daily')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.amount} for {self.description} ({self.date})"


class Income(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)
    source = models.CharField(max_length=100)
    description = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.amount} from {self.source} ({self.date})"


class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    month = models.IntegerField()  # 1-12 for month
    year = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'category', 'month', 'year')

    def __str__(self):
        return f"Budget for {self.category.name}: {self.amount} ({self.month}/{self.year})"
    
    def get_spent_amount(self):
        """Calculate how much has been spent in this category during this month/year"""
        month_start = datetime.date(self.year, self.month, 1)
        # Calculate end date (first day of next month)
        if self.month == 12:
            month_end = datetime.date(self.year + 1, 1, 1)
        else:
            month_end = datetime.date(self.year, self.month + 1, 1)
        
        spent = Expense.objects.filter(
            user=self.user,
            category=self.category,
            date__gte=month_start,
            date__lt=month_end
        ).aggregate(models.Sum('amount'))['amount__sum'] or 0
        
        return spent
    
    def get_percentage_used(self):
        """Calculate percentage of budget used"""
        if self.amount == 0:
            return 100  # Avoid division by zero
        
        spent = self.get_spent_amount()
        percentage = (spent / self.amount) * 100
        return min(percentage, 100)  # Cap at 100%


class SavingsGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    target_date = models.DateField()
    is_achieved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title}: {self.current_amount}/{self.target_amount}"
    
    def get_percentage_complete(self):
        """Calculate percentage of savings goal achieved"""
        if self.target_amount == 0:
            return 100  # Avoid division by zero
        
        percentage = (self.current_amount / self.target_amount) * 100
        return min(percentage, 100)  # Cap at 100%
    
    def get_days_remaining(self):
        """Calculate days remaining until target date"""
        today = timezone.now().date()
        if today > self.target_date:
            return 0
        return (self.target_date - today).days


class RecurringExpense(models.Model):
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='monthly')
    start_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title}: {self.amount} ({self.frequency})"


class FinancialTip(models.Model):
    CATEGORY_CHOICES = [
        ('saving', 'Saving Money'),
        ('budgeting', 'Budgeting'),
        ('investing', 'Investing'),
        ('debt', 'Debt Management'),
        ('general', 'General Finance'),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
