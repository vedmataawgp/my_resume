from django.core.management.base import BaseCommand
from core.models import Category

class Command(BaseCommand):
    help = 'Initialize default expense categories'

    def handle(self, *args, **kwargs):
        categories = [
            {'name': 'Housing', 'icon': 'fas fa-home'},
            {'name': 'Transportation', 'icon': 'fas fa-car'},
            {'name': 'Food', 'icon': 'fas fa-utensils'},
            {'name': 'Utilities', 'icon': 'fas fa-bolt'},
            {'name': 'Healthcare', 'icon': 'fas fa-medkit'},
            {'name': 'Insurance', 'icon': 'fas fa-shield-alt'},
            {'name': 'Debt', 'icon': 'fas fa-credit-card'},
            {'name': 'Entertainment', 'icon': 'fas fa-film'},
            {'name': 'Shopping', 'icon': 'fas fa-shopping-bag'},
            {'name': 'Personal Care', 'icon': 'fas fa-spa'},
            {'name': 'Education', 'icon': 'fas fa-graduation-cap'},
            {'name': 'Gifts & Donations', 'icon': 'fas fa-gift'},
            {'name': 'Travel', 'icon': 'fas fa-plane'},
            {'name': 'Investments', 'icon': 'fas fa-chart-line'},
            {'name': 'Subscriptions', 'icon': 'fas fa-calendar-check'},
        ]
        
        created_count = 0
        for category_data in categories:
            category, created = Category.objects.get_or_create(
                name=category_data['name'],
                defaults={'icon': category_data['icon']}
            )
            if created:
                created_count += 1
                self.stdout.write(f"Created category: {category.name}")
            else:
                self.stdout.write(f"Category already exists: {category.name}")
                
        self.stdout.write(self.style.SUCCESS(f"Successfully created {created_count} categories"))