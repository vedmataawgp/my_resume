from django.core.management.base import BaseCommand
from core.models import FinancialTip

class Command(BaseCommand):
    help = 'Initialize financial tips'

    def handle(self, *args, **kwargs):
        tips = [
            {
                'title': 'Follow the 50/30/20 Rule',
                'content': 'Allocate 50% of your income to needs, 30% to wants, and 20% to savings and debt repayment.',
                'category': 'budgeting'
            },
            {
                'title': 'Build an Emergency Fund',
                'content': 'Save 3-6 months of living expenses in an easily accessible account for unexpected emergencies.',
                'category': 'saving'
            },
            {
                'title': 'Pay Yourself First',
                'content': 'Set up automatic transfers to your savings account on payday before spending on other expenses.',
                'category': 'saving'
            },
            {
                'title': 'Eliminate High-Interest Debt',
                'content': 'Focus on paying off high-interest debt first, like credit cards, before investing extensively.',
                'category': 'debt'
            },
            {
                'title': 'Use the Envelope System',
                'content': 'Allocate cash to different spending categories in envelopes to avoid overspending your budget.',
                'category': 'budgeting'
            },
            {
                'title': 'Invest Early and Regularly',
                'content': 'Take advantage of compounding by investing early and making regular contributions to your portfolio.',
                'category': 'investing'
            },
            {
                'title': 'Review Subscriptions Quarterly',
                'content': 'Review all your subscriptions every three months and cancel those you don\'t use regularly.',
                'category': 'general'
            },
            {
                'title': 'Use the 24-Hour Rule',
                'content': 'Wait 24 hours before making non-essential purchases over a certain amount to avoid impulse buying.',
                'category': 'saving'
            },
            {
                'title': 'Max Out Retirement Accounts',
                'content': 'Contribute the maximum amount to tax-advantaged retirement accounts before other investments.',
                'category': 'investing'
            },
            {
                'title': 'Keep Fixed Expenses Low',
                'content': 'Minimize recurring fixed expenses like housing and transportation to maintain financial flexibility.',
                'category': 'general'
            },
        ]
        
        created_count = 0
        for tip_data in tips:
            tip, created = FinancialTip.objects.get_or_create(
                title=tip_data['title'],
                defaults={
                    'content': tip_data['content'],
                    'category': tip_data['category']
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f"Created tip: {tip.title}")
            else:
                self.stdout.write(f"Tip already exists: {tip.title}")
                
        self.stdout.write(self.style.SUCCESS(f"Successfully created {created_count} financial tips"))