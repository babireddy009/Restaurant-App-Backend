import threading
from django.core.mail import send_mail
from django.conf import settings
import logging
import urllib.request
import json
import ssl

logger = logging.getLogger(__name__)

def send_mail_via_brevo(subject, message, recipient_list, html_message=None):
    """
    Sends email via Brevo HTTP API using Python's standard library (urllib.request).
    """
    api_key = getattr(settings, 'BREVO_API_KEY', None)
    sender_email = getattr(settings, 'EMAIL_HOST_USER', None) or 'msrruchulu@gmail.com'
    
    if not api_key:
        raise ValueError("BREVO_API_KEY is not set in Django settings.")

    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "api-key": api_key,
        "content-type": "application/json",
        "accept": "application/json"
    }
    
    payload = {
        "sender": {"name": "MSR Rayalaseema Ruchulu", "email": sender_email},
        "to": [{"email": email} for email in recipient_list],
        "subject": subject,
    }
    
    if html_message:
        payload["htmlContent"] = html_message
        payload["textContent"] = message
    else:
        payload["textContent"] = message
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    with urllib.request.urlopen(req, context=ctx) as res:
        resp_body = res.read().decode('utf-8')
        logger.info(f"Brevo API response: {resp_body}")
        return json.loads(resp_body)

def send_mail_async(subject, message, recipient_list, fail_silently=False, html_message=None):
    """
    Sends an email asynchronously in a separate daemon thread to prevent request blocking.
    Uses Brevo HTTP API if configured, with automatic SMTP fallback if Brevo fails.
    """
    api_key = getattr(settings, 'BREVO_API_KEY', None)

    def _target():
        # Try Brevo if API key is configured
        if api_key:
            try:
                logger.info(f"Starting async email thread via Brevo HTTP API to send to {recipient_list}")
                send_mail_via_brevo(subject, message, recipient_list, html_message=html_message)
                logger.info(f"Successfully sent async email via Brevo HTTP API to {recipient_list}")
                return  # Success, exit thread
            except Exception as brevo_err:
                logger.error(f"Failed to send async email via Brevo: {str(brevo_err)}. Falling back to SMTP...")

        # SMTP Fallback/Default
        try:
            logger.info(f"Starting async email thread via SMTP to send to {recipient_list}")
            if not getattr(settings, 'EMAIL_HOST_USER', None):
                logger.warning("SMTP credentials (EMAIL_HOST_USER) not configured. Skipping email send.")
                return
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=recipient_list,
                fail_silently=fail_silently,
                html_message=html_message,
            )
            logger.info(f"Successfully sent async email via SMTP to {recipient_list}")
        except Exception as smtp_err:
            logger.error(f"Failed to send async email via SMTP to {recipient_list} -> {str(smtp_err)}")

    t = threading.Thread(target=_target)
    t.daemon = True
    t.start()

