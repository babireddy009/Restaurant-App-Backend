from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def _send_customer_email(order, subject, message, html_message=None):
    if not order.user or not order.user.email:
        return  # Missing email address

    from core.email_utils import send_mail_async
    send_mail_async(
        subject=subject,
        message=message,
        recipient_list=[order.user.email],
        fail_silently=False,
        html_message=html_message,
    )


def send_order_confirmation_email(order):
    """Fired when pure COD is placed, or Online Payment clears."""
    subject = f"Order #{order.id} Confirmed - MSR Rayalaseema Ruchulu"
    
    # Calculate receipt breakdowns
    subtotal = sum(item.subtotal for item in order.items.all())
    delivery_fee = 0 # Currently free
    tax = int(round(float(subtotal) * 0.05))
    grand_total = order.total_amount
    
    # Generate items details for text and HTML
    items_list_text = "\n".join([f"- {item.quantity}x {item.item_name} (₹{item.item_price})" for item in order.items.all()])
    
    items_list_html = ""
    for item in order.items.all():
        item_sub = item.quantity * item.item_price
        items_list_html += f"""
        <tr style="border-bottom: 1px solid #eee;">
          <td style="padding: 8px 0; font-size: 14px; color: #333;">{item.item_name}</td>
          <td style="padding: 8px 0; text-align: center; font-size: 14px; color: #666;">{item.quantity}</td>
          <td style="padding: 8px 0; text-align: right; font-size: 14px; font-weight: 600; color: #333;">₹{item_sub:.2f}</td>
        </tr>
        """
        
    payment_display = 'Cash on Delivery' if order.payment_method == 'cod' else 'Online (Paid)'
    
    # 1. Plain Text Message
    text_body = (
        f"Hello {order.user.username},\n\n"
        f"Thank you for ordering with MSR Rayalaseema Ruchulu!\n"
        f"Your order #{order.id} has been fully confirmed.\n\n"
        f"ORDER SUMMARY:\n"
        f"{items_list_text}\n\n"
        f"Subtotal: ₹{subtotal:.2f}\n"
        f"GST (5%): ₹{tax:.2f}\n"
        f"Delivery Fee: FREE\n"
        f"Grand Total: ₹{grand_total:.2f}\n\n"
        f"Payment Method: {payment_display}\n"
        f"Delivery Address:\n{order.delivery_address}\n\n"
        f"Our chefs are preparing your food right now. We will notify you when it's on the way!\n"
    )

    # 2. Rich HTML Invoice
    html_body = f"""
    <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 600px; margin: auto; border: 1px solid #e0e0e0; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.04);">
      <div style="background-color: #ff6b35; padding: 30px; text-align: center; color: white;">
        <h1 style="margin: 0; font-size: 26px; font-weight: 800; letter-spacing: 0.5px;">MSR Rayalaseema Ruchulu</h1>
        <p style="margin: 6px 0 0 0; font-size: 14px; opacity: 0.9;">Your Authentic Taste of Rayalaseema</p>
      </div>
      <div style="padding: 30px; background-color: #ffffff;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 1px solid #eee; padding-bottom: 15px;">
          <div>
            <h2 style="margin: 0; color: #2d3748; font-size: 18px; font-weight: 700;">Order Confirmed!</h2>
            <p style="margin: 4px 0 0 0; color: #718096; font-size: 13px;">Order #{order.id} &bull; {order.created_at.strftime('%b %d, %Y %I:%M %p') if order.created_at else ''}</p>
          </div>
        </div>
        <p style="color: #4a5568; font-size: 14px; line-height: 1.5;">Hi <strong>{order.user.first_name or order.user.username}</strong>,</p>
        <p style="color: #4a5568; font-size: 14px; line-height: 1.5; margin-bottom: 25px;">Thank you for your order! Your delicious food has been confirmed and is now being prepared. Below is your detailed receipt.</p>
        
        <h3 style="color: #ff6b35; margin: 0 0 10px 0; font-size: 15px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">Order Details</h3>
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 25px;">
          <thead>
            <tr style="border-bottom: 2px solid #edf2f7; text-align: left; color: #718096; font-size: 12px; text-transform: uppercase;">
              <th style="padding: 10px 0; font-weight: 600;">Item Description</th>
              <th style="padding: 10px 0; text-align: center; font-weight: 600; width: 60px;">Qty</th>
              <th style="padding: 10px 0; text-align: right; font-weight: 600; width: 90px;">Subtotal</th>
            </tr>
          </thead>
          <tbody>
            {items_list_html}
          </tbody>
        </table>
        
        <div style="width: 260px; margin-left: auto; margin-bottom: 25px; border-top: 1px solid #edf2f7; padding-top: 10px;">
          <table style="width: 100%; font-size: 14px; color: #4a5568; border-collapse: collapse;">
            <tr>
              <td style="padding: 5px 0;">Subtotal:</td>
              <td style="padding: 5px 0; text-align: right; font-weight: 500;">₹{subtotal:.2f}</td>
            </tr>
            <tr>
              <td style="padding: 5px 0;">GST (5%):</td>
              <td style="padding: 5px 0; text-align: right; font-weight: 500;">₹{tax:.2f}</td>
            </tr>
            <tr>
              <td style="padding: 5px 0;">Delivery Fee:</td>
              <td style="padding: 5px 0; text-align: right; color: #38a169; font-weight: 600;">FREE</td>
            </tr>
            <tr style="border-top: 2px double #edf2f7; font-weight: 700; font-size: 16px; color: #ff6b35;">
              <td style="padding: 10px 0 5px 0;">Grand Total:</td>
              <td style="padding: 10px 0 5px 0; text-align: right;">₹{grand_total:.2f}</td>
            </tr>
          </table>
        </div>
        
        <table style="width: 100%; font-size: 13px; color: #4a5568; background-color: #f7fafc; border-radius: 8px; padding: 15px; margin-bottom: 20px;">
          <tr>
            <td style="width: 50%; vertical-align: top; padding-right: 10px;">
              <strong style="color: #2d3748; display: block; margin-bottom: 4px;">Payment Method</strong>
              {payment_display}
            </td>
            <td style="width: 50%; vertical-align: top;">
              <strong style="color: #2d3748; display: block; margin-bottom: 4px;">Delivery Address</strong>
              {order.delivery_address}
            </td>
          </tr>
        </table>
      </div>
      <div style="background-color: #f7fafc; padding: 20px; text-align: center; font-size: 12px; color: #a0aec0; border-top: 1px solid #edf2f7;">
        Need help? Contact support at <a href="mailto:contact@msrrayalaseemaruchulu.in" style="color: #ff6b35; text-decoration: none; font-weight: 600;">contact@msrrayalaseemaruchulu.in</a><br>
        <span style="display: block; margin-top: 6px;">&copy; 2024 MSR Rayalaseema Ruchulu. All rights reserved.</span>
      </div>
    </div>
    """

    # Send Email Bill
    _send_customer_email(order, subject, text_body, html_message=html_body)

    # 3. WhatsApp Message
    phone_number = getattr(order.user, 'phone', None)
    if phone_number:
        whatsapp_body = (
            f"*MSR Rayalaseema Ruchulu* 🍛\n"
            f"Order *#{order.id}* Confirmed! 🎉\n\n"
            f"Hi {order.user.username},\n"
            f"Thank you for ordering with us. Your bill summary:\n\n"
            f"{items_list_text}\n\n"
            f"*Subtotal:* ₹{subtotal:.2f}\n"
            f"*GST (5%):* ₹{tax:.2f}\n"
            f"*Delivery:* FREE\n"
            f"*Grand Total:* ₹{grand_total:.2f}\n\n"
            f"*Payment Method:* {payment_display}\n"
            f"*Address:* {order.delivery_address}\n\n"
            f"Our chefs are preparing your hot meal now! 🛵"
        )
        from core.sms_utils import send_whatsapp_message_async
        send_whatsapp_message_async(phone_number, whatsapp_body)


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
        f"Thank you,\nMSR Rayalaseema Ruchulu Team"
    )

    _send_customer_email(order, subject, body)
