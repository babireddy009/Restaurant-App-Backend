import threading
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_mail_async(subject, message, recipient_list, fail_silently=False):
    """
    Sends an email asynchronously in a separate daemon thread to prevent request blocking.
    """
    if not settings.EMAIL_HOST_USER:
        logger.warning("SMTP credentials (EMAIL_HOST_USER) not configured. Skipping email send.")
        return

    def _target():
        try:
            logger.info(f"Starting async email thread to send to {recipient_list}")
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=recipient_list,
                fail_silently=fail_silently,
            )
            logger.info(f"Successfully sent async email to {recipient_list}")
        except Exception as e:
            logger.error(f"Failed to send async email to {recipient_list} -> {str(e)}")

    t = threading.Thread(target=_target)
    t.daemon = True
    t.start()
