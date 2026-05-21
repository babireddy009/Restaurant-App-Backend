import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Safe, atomic auto-startup hooks for ASGI environment
try:
    import time
    from django.core.management import call_command
    
    lock_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'startup_asgi.lock')
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
            print("ASGI Startup lock acquired. Running auto-migrations...")
            call_command('migrate', interactive=False)
            
            print("Running collectstatic (ASGI)...")
            call_command('collectstatic', interactive=False)
        finally:
            try:
                os.rmdir(lock_dir)
                print("ASGI Startup tasks complete. Lock released.")
            except Exception as lock_err:
                print(f"Failed to release ASGI startup lock: {lock_err}")
    else:
        print("ASGI Startup tasks already running or executed in another process.")
except Exception as e:
    print(f"ASGI Auto-startup error: {e}")

from django.core.asgi import get_asgi_application
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from core.middleware import JWTAuthMiddleware
import orders.routing

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": JWTAuthMiddleware(
        AuthMiddlewareStack(
            URLRouter(
                orders.routing.websocket_urlpatterns
            )
        )
    ),
})
