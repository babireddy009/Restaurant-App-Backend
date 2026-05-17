import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = get_wsgi_application()

# Bulletproof fix for Render's ephemeral SQLite disk
try:
    from django.core.management import call_command
    print("Running auto-migrations...")
    call_command('migrate', interactive=False)
    
    from menu.models import Category
    if not Category.objects.exists():
        import subprocess
        print("Running seed data...")
        subprocess.run(['python', 'seed_data.py'])
except Exception as e:
    print(f"Auto-startup error: {e}")
