from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Initialize all default data for the application'

    def handle(self, *args, **kwargs):
        self.stdout.write("Initializing application data...")
        
        # Initialize categories
        self.stdout.write("Initializing expense categories...")
        call_command('initialize_categories')
        
        # Initialize financial tips
        self.stdout.write("Initializing financial tips...")
        call_command('initialize_tips')
        
        self.stdout.write(self.style.SUCCESS("All data initialized successfully!"))