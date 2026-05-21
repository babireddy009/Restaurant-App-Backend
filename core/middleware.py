import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser

User = get_user_model()

@database_sync_to_async
def get_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()

class JWTAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        query_string = scope.get('query_string', b'').decode('utf-8')
        query_params = parse_qs(query_string)
        token = query_params.get('token', [None])[0]

        scope['user'] = AnonymousUser()

        if token:
            try:
                # Decode JWT token
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                scope['user'] = await get_user(payload['user_id'])
            except Exception as e:
                print("JWT Decode Error:", e)
                pass
        
        return await self.inner(scope, receive, send)


import os
import traceback

class ExceptionLoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        tb_str = traceback.format_exc()
        log_file = os.path.join(settings.BASE_DIR, 'django_errors.log')
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write("=== ERROR ===\n")
                f.write(f"Path: {request.path}\n")
                f.write(f"Method: {request.method}\n")
                f.write(f"User: {request.user}\n")
                f.write(f"Exception: {str(exception)}\n")
                f.write(f"Traceback:\n{tb_str}\n")
                f.write(f"=============\n\n")
        except Exception as e:
            print("Error writing exception log:", e)
        return None

