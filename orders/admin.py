from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem, ChatMessage


class OrderItemInline(admin.TabularInline):
    model           = OrderItem
    extra           = 0
    can_delete      = False
    readonly_fields = ('item_name', 'item_price', 'quantity', 'subtotal_display')
    verbose_name    = 'Ordered Item'
    verbose_name_plural = '🛒 Ordered Items'

    def subtotal_display(self, obj):
        return format_html('<strong>₹{}</strong>', f'{obj.subtotal:.2f}')
    subtotal_display.short_description = 'Subtotal'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display        = ('order_number', 'customer_name', 'customer_phone',
                           'status', 'status_badge', 'total_display',
                           'payment_badge', 'created_at')
    list_filter         = ('status', 'is_paid', 'created_at')
    search_fields       = ('user__username', 'user__email', 'user__phone',
                           'delivery_address', 'id')
    ordering            = ('-created_at',)
    readonly_fields     = ('user', 'total_amount', 'created_at', 'updated_at')
    inlines             = [OrderItemInline]
    list_editable       = ('status',)
    list_per_page       = 25
    date_hierarchy      = 'created_at'
    save_on_top         = True
    list_display_links  = ('order_number', 'customer_name')

    fieldsets = (
        ('📦 Order Details', {
            'fields': ('user', 'status', 'is_paid', 'total_amount')
        }),
        ('📍 Delivery Information', {
            'fields': ('delivery_address', 'notes')
        }),
        ('🛵 Driver & Tracking', {
            'fields': ('driver', 'delivery_otp', 'driver_name', 'driver_phone', 'driver_lat', 'driver_lng'),
            'classes': ('collapse',),
        }),
        ('🕐 Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def order_number(self, obj):
        return format_html('<strong>#{}00{}</strong>', '', obj.id)
    order_number.short_description = 'Order ID'
    order_number.admin_order_field = 'id'

    def customer_name(self, obj):
        name = obj.user.get_full_name() or obj.user.username
        return format_html('<strong>{}</strong>', name)
    customer_name.short_description = '👤 Customer'

    def customer_phone(self, obj):
        return obj.user.phone or '—'
    customer_phone.short_description = '📞 Phone'

    def total_display(self, obj):
        return format_html('<strong style="color:#fd7e14; font-size:1rem;">₹{}</strong>',
                           f'{obj.total_amount:.0f}')
    total_display.short_description = '💰 Total'
    total_display.admin_order_field = 'total_amount'

    def status_badge(self, obj):
        colors = {
            'pending':           ('#856404', '#fff3cd'),
            'confirmed':         ('#155724', '#d4edda'),
            'preparing':         ('#721c24', '#f8d7da'),
            'ready':             ('#0c5460', '#d1ecf1'),
            'out_for_delivery':  ('#383d41', '#e2e3e5'),
            'delivered':         ('#155724', '#d4edda'),
            'cancelled':         ('#721c24', '#f8d7da'),
        }
        icons = {
            'pending': '⏳', 'confirmed': '✅', 'preparing': '👨‍🍳',
            'ready': '🔔', 'out_for_delivery': '🚴', 'delivered': '🎉', 'cancelled': '❌',
        }
        fg, bg = colors.get(obj.status, ('#000', '#fff'))
        icon   = icons.get(obj.status, '')
        label  = obj.status.replace('_', ' ').title()
        return format_html(
            '<span style="background:{};color:{};padding:3px 10px;border-radius:12px;'
            'font-size:0.82rem;font-weight:600;white-space:nowrap;">{} {}</span>',
            bg, fg, icon, label
        )
    status_badge.short_description = '📊 Status'

    def payment_badge(self, obj):
        if obj.is_paid:
            return format_html(
                '<span style="background:#d4edda;color:#155724;padding:3px 10px;'
                'border-radius:12px;font-size:0.82rem;font-weight:700;">💳 Paid</span>'
            )
        return format_html(
            '<span style="background:#fff3cd;color:#856404;padding:3px 10px;'
            'border-radius:12px;font-size:0.82rem;font-weight:700;">⏳ Unpaid</span>'
        )
    payment_badge.short_description = '💳 Payment'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display  = ('order_link', 'item_name', 'item_price_fmt', 'quantity', 'subtotal_display')
    search_fields = ('item_name', 'order__id', 'order__user__username')
    list_per_page = 40
    list_select_related = ('order', 'order__user')

    def order_link(self, obj):
        url = f'/admin/orders/order/{obj.order.id}/change/'
        return format_html('<a href="{}" style="font-weight:700;">#{}</a>', url, obj.order.id)
    order_link.short_description = '📦 Order'

    def item_price_fmt(self, obj):
        return format_html('₹{}', f'{obj.item_price:.0f}')
    item_price_fmt.short_description = 'Unit Price'

    def subtotal_display(self, obj):
        return format_html('<strong>₹{}</strong>', f'{obj.subtotal:.2f}')
    subtotal_display.short_description = '💰 Subtotal'


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('order_link', 'sender', 'message_preview', 'timestamp')
    list_filter = ('sender', 'timestamp')
    search_fields = ('message', 'order__id')
    readonly_fields = ('order', 'sender', 'message', 'timestamp')
    
    def order_link(self, obj):
        url = f'/admin/orders/order/{obj.order.id}/change/'
        return format_html('<a href="{}" style="font-weight:700;">#{}</a>', url, obj.order.id)
    order_link.short_description = '📦 Order'

    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message'
