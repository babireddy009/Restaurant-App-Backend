import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = get_wsgi_application()

# Safe, atomic auto-startup hooks (migrations, collectstatic, seed data)
try:
    import time
    from django.core.management import call_command
    
    lock_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'startup.lock')
    should_run = False

    try:
        os.mkdir(lock_dir)
        should_run = True
    except FileExistsError:
        try:
            mtime = os.path.getmtime(lock_dir)
            if time.time() - mtime > 300:  # 5 minutes stale timeout
                os.utime(lock_dir, None)  # Touch directory
                should_run = True
        except Exception:
            pass

    if should_run:
        try:
            print("Startup lock acquired. Running auto-migrations...")
            call_command('migrate', interactive=False)
            
            print("Running collectstatic...")
            call_command('collectstatic', interactive=False)
            
            from menu.models import Category
            if not Category.objects.exists():
                import subprocess
                print("Running seed data...")
                subprocess.run(['python', 'seed_data.py'])
        finally:
            try:
                os.rmdir(lock_dir)
                print("Startup tasks complete. Lock released.")
            except Exception as lock_err:
                print(f"Failed to release startup lock: {lock_err}")
    else:
        print("Startup tasks already running or executed in another worker process.")

except Exception as e:
    print(f"Auto-startup error: {e}")
