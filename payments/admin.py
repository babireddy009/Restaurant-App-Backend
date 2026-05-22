from django.contrib import admin
from django.utils.html import format_html
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display    = ('payment_id_short', 'order_link', 'amount_display',
                       'status_badge', 'payment_id_display', 'created_at')
    list_filter     = ('status', 'currency', 'created_at')
    search_fields   = ('razorpay_order_id', 'razorpay_payment_id', 'order__id')
    readonly_fields = ('razorpay_order_id', 'razorpay_payment_id',
                       'razorpay_signature', 'created_at', 'updated_at')
    ordering        = ('-created_at',)
    list_per_page   = 30
    date_hierarchy  = 'created_at'

    fieldsets = (
        ('💳 Payment Info', {
            'fields': ('order', 'amount', 'currency', 'status')
        }),
        ('🔑 Razorpay IDs (Read Only)', {
            'fields': ('razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature'),
            'classes': ('collapse',),
            'description': 'These are set automatically by the payment gateway',
        }),
        ('🕐 Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def payment_id_short(self, obj):
        return format_html('<code>#{}</code>', obj.id)
    payment_id_short.short_description = 'ID'

    def order_link(self, obj):
        url = f'/admin/orders/order/{obj.order.id}/change/'
        customer = obj.order.user.get_full_name() or obj.order.user.username
        return format_html('<a href="{}" style="font-weight:700;">Order #{} — {}</a>',
                           url, obj.order.id, customer)
    order_link.short_description = '📦 Order'

    def amount_display(self, obj):
        return format_html('<strong style="color:#fd7e14; font-size:1rem;">₹{}</strong>',
                           f'{obj.amount:.0f}')
    amount_display.short_description = '💰 Amount'
    amount_display.admin_order_field = 'amount'

    def payment_id_display(self, obj):
        if obj.razorpay_payment_id:
            short = obj.razorpay_payment_id[-8:]
            return format_html('<code title="{}" style="font-size:0.8rem;">...{}</code>',
                               obj.razorpay_payment_id, short)
        return format_html('<span style="color:#6c757d;">—</span>')
    payment_id_display.short_description = 'Razorpay ID'

    def status_badge(self, obj):
        colors = {
            'success':  ('#155724', '#d4edda'),
            'failed':   ('#721c24', '#f8d7da'),
            'pending':  ('#856404', '#fff3cd'),
            'refunded': ('#073069', '#cfe2ff'),
        }
        icons = {'success': '✅', 'failed': '❌', 'pending': '⏳', 'refunded': '↩️'}
        fg, bg = colors.get(obj.status, ('#000', '#fff'))
        icon   = icons.get(obj.status, '')
        return format_html(
            '<span style="background:{};color:{};padding:3px 12px;border-radius:12px;'
            'font-size:0.82rem;font-weight:700;">{} {}</span>',
            bg, fg, icon, obj.status.title()
        )
    status_badge.short_description = '📊 Status'
