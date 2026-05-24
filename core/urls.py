from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# ── Customize Django Admin branding ──────────────────────────────────────────
admin.site.site_header  = 'MSR Rayalaseema Ruchulu — Admin'
admin.site.site_title   = 'MSR Admin'
admin.site.index_title  = 'Restaurant Management Dashboard'

original_index = admin.site.index

def custom_admin_index(request, extra_context=None):
    if extra_context is None:
        extra_context = {}
    
    try:
        from django.utils import timezone
        from django.db.models import Sum, Count
        from orders.models import Order, OrderItem
        from accounts.models import CustomUser
        from menu.models import MenuItem

        today = timezone.localtime(timezone.now()).date()
        today_orders = Order.objects.filter(created_at__date=today)
        
        extra_context['today_date'] = today.strftime('%Y-%m-%d')
        extra_context['total_sales'] = Order.objects.filter(is_paid=True).aggregate(total=Sum('total_amount'))['total'] or 0.0
        extra_context['today_sales'] = today_orders.filter(is_paid=True).aggregate(total=Sum('total_amount'))['total'] or 0.0
        extra_context['total_orders'] = Order.objects.count()
        extra_context['active_orders'] = Order.objects.filter(status__in=['pending', 'confirmed', 'preparing', 'ready', 'out_for_delivery']).count()
        extra_context['total_items'] = MenuItem.objects.filter(is_available=True).count()
        extra_context['total_customers'] = CustomUser.objects.filter(role='customer').count()
        
        # Recent orders (last 5)
        extra_context['recent_orders_list'] = Order.objects.all().select_related('user')[:5]
        
        # Best selling items (top 3)
        best_sellers = OrderItem.objects.values('item_name').annotate(total_qty=Sum('quantity')).order_by('-total_qty')[:3]
        extra_context['best_sellers'] = best_sellers
    except Exception as e:
        print(f"Error gathering custom admin stats: {e}")
        
    return original_index(request, extra_context=extra_context)

admin.site.index = custom_admin_index


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/menu/', include('menu.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/payments/', include('payments.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
