from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def _send_customer_email(order, subject, message):
    if not order.user or not order.user.email:
        return  # Missing email address

    from core.email_utils import send_mail_async
    send_mail_async(
        subject=subject,
        message=message,
        recipient_list=[order.user.email],
        fail_silently=False,
    )


def send_order_confirmation_email(order):
    """Fired when pure COD is placed, or Online Payment clears."""
    subject = f"Order #{order.id} Confirmed - MSR Rayalasema Ruchulu"
    
    items_list = "\n".join([f"- {item.quantity}x {item.item_name} (₹{item.item_price})" for item in order.items.all()])
    
    body = (
        f"Hello {order.user.username},\n\n"
        f"Thank you for ordering with MSR Rayalasema Ruchulu!\n"
        f"Your order #{order.id} has been fully confirmed.\n\n"
        f"ORDER SUMMARY:\n"
        f"{items_list}\n\n"
        f"Total Amount: ₹{order.total_amount}\n"
        f"Payment Method: {'Cash on Delivery' if order.payment_method == 'cod' else 'Online (Paid)'}\n\n"
        f"Delivery Address:\n{order.delivery_address}\n\n"
        f"Our chefs are preparing your food right now. We will notify you when it's on the way!\n"
    )
    
    _send_customer_email(order, subject, body)


def send_order_status_update_email(order):
    """Fired explicitly when admin mutations occur bounds checking actual states"""
    # Create robust mapped text contexts
    status_map = {
        'preparing': ('is now being prepared by our chefs!', 'Estimated prep time is 20-30 mins.'),
        'ready': ('is fully cooked and ready for pickup/dispatch!', 'Get ready to enjoy.'),
        'out_for_delivery': ('is securely packed and out for delivery!', 'Our delivery partner is en route to your address.'),
        'delivered': ('has been delivered successfully!', 'Enjoy your authentic Rayalaseema flavors!'),
        'cancelled': ('has regrettably been cancelled.', 'If you have questions, please reach out to our support.')
    }

    if order.status not in status_map:
        return # Fallback for pending / confirmed which are handled by the confirmation email
        
    headline, flavor = status_map[order.status]
    
    subject = f"Order #{order.id} Update - {dict(order.STATUS_CHOICES).get(order.status, order.status)}"
    
    body = (
        f"Hello {order.user.username},\n\n"
        f"An update regarding your recent order #{order.id}:\n\n"
        f"Your food {headline}\n"
        f"{flavor}\n\n"
        f"Thank you,\nMSR Rayalasema Ruchulu Team"
    )

    _send_customer_email(order, subject, body)
