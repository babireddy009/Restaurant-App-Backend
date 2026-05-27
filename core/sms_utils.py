import os
import logging
import threading
import urllib.request
import urllib.parse
import json
import ssl
import base64

logger = logging.getLogger(__name__)

def send_sms_via_twilio(to_number, message_body):
    """
    Sends SMS via Twilio API using Python standard library urllib.
    """
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    from_number = os.getenv('TWILIO_FROM_NUMBER')

    if not all([account_sid, auth_token, from_number]):
        raise ValueError("Twilio credentials not fully configured in environment variables.")

    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
    data = urllib.parse.urlencode({
        'To': to_number,
        'From': from_number,
        'Body': message_body
    }).encode('utf-8')

    auth_str = f"{account_sid}:{auth_token}"
    auth_b64 = base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')
    headers = {
        'Authorization': f'Basic {auth_b64}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    with urllib.request.urlopen(req, context=ctx) as res:
        return res.read().decode('utf-8')

def send_sms_via_fast2sms(to_number, message_body):
    """
    Sends SMS via Fast2SMS API Bulk SMS service.
    """
    api_key = os.getenv('FAST2SMS_API_KEY')
    if not api_key:
        raise ValueError("FAST2SMS_API_KEY not configured in environment variables.")

    url = "https://www.fast2sms.com/dev/bulkV2"
    
    # Extract only digits and keep the last 10 characters (valid mobile number in India)
    clean_number = ''.join(filter(str.isdigit, to_number))
    if len(clean_number) > 10:
        clean_number = clean_number[-10:]

    payload = {
        "route": "q",
        "message": message_body,
        "language": "english",
        "flash": 0,
        "numbers": clean_number
    }
    
    data = json.dumps(payload).encode('utf-8')
    headers = {
        'authorization': api_key,
        'Content-Type': 'application/json',
        'accept': 'application/json'
    }
    
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    with urllib.request.urlopen(req, context=ctx) as res:
        return res.read().decode('utf-8')

def send_sms_async(to_number, message_body):
    """
    Sends an SMS asynchronously. Tries Fast2SMS first, then Twilio, and falls back to console logs.
    """
    def _target():
        # Auto-format number for Twilio if not starting with '+'
        formatted_number = to_number
        if not formatted_number.startswith('+'):
            clean_num = ''.join(filter(str.isdigit, formatted_number))
            if len(clean_num) == 10:
                formatted_number = f"+91{clean_num}"

        # 1. Try Fast2SMS
        if os.getenv('FAST2SMS_API_KEY'):
            try:
                logger.info(f"Attempting to send SMS to {formatted_number} via Fast2SMS...")
                send_sms_via_fast2sms(formatted_number, message_body)
                logger.info(f"SMS successfully sent to {formatted_number} via Fast2SMS.")
                return
            except Exception as e:
                logger.error(f"Fast2SMS SMS delivery failed: {str(e)}")

        # 2. Try Twilio
        if os.getenv('TWILIO_ACCOUNT_SID'):
            try:
                logger.info(f"Attempting to send SMS to {formatted_number} via Twilio...")
                send_sms_via_twilio(formatted_number, message_body)
                logger.info(f"SMS successfully sent to {formatted_number} via Twilio.")
                return
            except Exception as e:
                logger.error(f"Twilio SMS delivery failed: {str(e)}")

        # 3. Fallback to mock log
        print(f"\n==========================================")
        print(f" MOCK SMS SENT (NO ACTIVE API GATEWAY) ")
        print(f" TO: {formatted_number}")
        print(f" BODY: {message_body}")
        print(f"==========================================\n")

    t = threading.Thread(target=_target)
    t.daemon = True
    t.start()

def send_whatsapp_message_async(to_number, message_body):
    """
    Sends an async WhatsApp message via Twilio API.
    """
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    from_whatsapp = os.getenv('TWILIO_WHATSAPP_FROM') or 'whatsapp:+14155238886'

    if not all([account_sid, auth_token]):
        logger.warning("Twilio credentials not configured for WhatsApp. Printing mock WhatsApp body instead.")
        print(f"\n==========================================")
        print(f" MOCK WHATSAPP SENT ")
        print(f" TO: {to_number}")
        print(f" BODY: {message_body}")
        print(f"==========================================\n")
        return

    # Normalize phone format
    clean_num = ''.join(filter(str.isdigit, to_number))
    if len(clean_num) == 10:
        clean_num = f"91{clean_num}"
    to_whatsapp = f"whatsapp:+{clean_num}"

    def _target():
        import urllib.request
        import urllib.parse
        import ssl
        import base64

        url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
        data = urllib.parse.urlencode({
            'To': to_whatsapp,
            'From': from_whatsapp,
            'Body': message_body
        }).encode('utf-8')

        auth_str = f"{account_sid}:{auth_token}"
        auth_b64 = base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')
        headers = {
            'Authorization': f'Basic {auth_b64}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        req = urllib.request.Request(url, data=data, headers=headers, method='POST')
        
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        try:
            with urllib.request.urlopen(req, context=ctx) as res:
                logger.info(f"WhatsApp sent successfully: {res.read().decode('utf-8')}")
        except Exception as e:
            logger.error(f"Failed to send WhatsApp message: {str(e)}")

    t = threading.Thread(target=_target)
    t.daemon = True
    t.start()

