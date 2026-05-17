from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# ── Customize Django Admin branding ──────────────────────────────────────────
admin.site.site_header  = 'MSR Rayalasema Ruchulu — Admin'
admin.site.site_title   = 'MSR Admin'
admin.site.index_title  = 'Restaurant Management Dashboard'


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/menu/', include('menu.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/payments/', include('payments.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
