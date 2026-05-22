import razorpay
from django.conf import settings
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from orders.models import Order
from orders.services import send_order_confirmation_email
from .models import Payment


def get_razorpay_client():
    key_id = (settings.RAZORPAY_KEY_ID or '').strip()
    key_secret = (settings.RAZORPAY_KEY_SECRET or '').strip()
    return razorpay.Client(auth=(key_id, key_secret))


class CreatePaymentView(APIView):
    """
    Step 1: Create a Razorpay order for an existing app order.
    POST /api/payments/create/
    Body: { "order_id": <int> }
    Returns: razorpay_order_id, amount, key
    """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        order_id = request.data.get('order_id')
        if not order_id:
            return Response(
                {'error': 'order_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response(
                {'error': 'Order not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        if order.is_paid:
            return Response(
                {'error': 'Order is already paid'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Razorpay requires amount in paise (1 INR = 100 paise)
        amount_paise = int(float(order.total_amount) * 100)

        try:
            client = get_razorpay_client()
            rz_order = client.order.create({
                'amount': amount_paise,
                'currency': 'INR',
                'receipt': f'receipt_order_{order.id}',
                'payment_capture': 1,      # auto-capture payment
                'notes': {
                    'order_id': str(order.id),
                    'customer': request.user.username,
                }
            })
        except Exception as e:
            return Response(
                {'error': f'Razorpay error: {str(e)}. Check your API keys in .env'},
                status=status.HTTP_502_BAD_GATEWAY
            )

        # Save/update payment record in DB
        Payment.objects.update_or_create(
            order=order,
            defaults={
                'razorpay_order_id': rz_order['id'],
                'amount': order.total_amount,
                'status': 'created',
                'razorpay_payment_id': '',
                'razorpay_signature': '',
            }
        )

        return Response({
            'razorpay_order_id': rz_order['id'],
            'amount': amount_paise,
            'currency': 'INR',
            'key': (settings.RAZORPAY_KEY_ID or '').strip(),
            'order_id': order.id,
        })


class VerifyPaymentView(APIView):
    """
    Step 2: Verify Razorpay payment signature after successful payment.
    POST /api/payments/verify/
    Body: { razorpay_order_id, razorpay_payment_id, razorpay_signature }
    """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        rz_order_id  = request.data.get('razorpay_order_id')
        rz_payment_id = request.data.get('razorpay_payment_id')
        rz_signature  = request.data.get('razorpay_signature')

        if not all([rz_order_id, rz_payment_id, rz_signature]):
            return Response(
                {'error': 'Missing payment credentials (order_id, payment_id, signature)'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            payment = Payment.objects.get(razorpay_order_id=rz_order_id)
        except Payment.DoesNotExist:
            return Response(
                {'error': 'Payment record not found. Create payment first.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Use Razorpay SDK's built-in HMAC-SHA256 verifier (recommended for v2)
        try:
            client = get_razorpay_client()
            client.utility.verify_payment_signature({
                'razorpay_order_id':   rz_order_id,
                'razorpay_payment_id': rz_payment_id,
                'razorpay_signature':  rz_signature,
            })
            # If no exception raised → signature is valid
            signature_valid = True
        except razorpay.errors.SignatureVerificationError:
            signature_valid = False
        except Exception as e:
            return Response(
                {'error': f'Verification error: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        if signature_valid:
            # Update payment record
            payment.razorpay_payment_id = rz_payment_id
            payment.razorpay_signature  = rz_signature
            payment.status = 'success'
            payment.save()

            # Confirm the order
            order = payment.order
            order.is_paid = True
            order.status  = 'confirmed'
            order.save()

            # Dispatch Paid Order Confirmation Email
            send_order_confirmation_email(order)

            return Response({
                'status': 'success',
                'message': 'Payment verified successfully!',
                'order_id': order.id,
            })
        else:
            payment.status = 'failed'
            payment.save()
            return Response(
                {'error': 'Invalid payment signature. Payment not verified.'},
                status=status.HTTP_400_BAD_REQUEST
            )


class PaymentStatusView(APIView):
    """Get payment status for an order"""
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            payment = order.payment
            return Response({
                'order_id':            order.id,
                'payment_status':      payment.status,
                'amount':              str(payment.amount),
                'razorpay_order_id':   payment.razorpay_order_id,
                'razorpay_payment_id': payment.razorpay_payment_id,
            })
        except Payment.DoesNotExist:
            return Response({
                'order_id':       order.id,
                'payment_status': 'not_initiated',
            })


class TestPaymentSuccessView(APIView):
    """
    ⚠️  DEV ONLY — Simulates a successful payment without calling Razorpay.
    Only works when DEBUG=True in settings.py.
    POST /api/payments/test-success/
    Body: { "order_id": <int> }
    """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        if not settings.DEBUG:
            return Response(
                {'error': 'Test payment endpoint is disabled in production.'},
                status=status.HTTP_403_FORBIDDEN
            )

        order_id = request.data.get('order_id')
        if not order_id:
            return Response({'error': 'order_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        if order.is_paid:
            return Response({'error': 'Order already paid', 'order_id': order.id})

        # Create or update payment record with simulated IDs
        import uuid
        fake_payment_id = f'pay_TEST_{uuid.uuid4().hex[:14].upper()}'
        fake_order_id   = f'order_TEST_{uuid.uuid4().hex[:12].upper()}'
        fake_signature  = f'sig_TEST_{uuid.uuid4().hex[:20].upper()}'

        Payment.objects.update_or_create(
            order=order,
            defaults={
                'razorpay_order_id':   fake_order_id,
                'razorpay_payment_id': fake_payment_id,
                'razorpay_signature':  fake_signature,
                'amount':  order.total_amount,
                'status':  'success',
            }
        )

        # Mark order confirmed
        order.is_paid = True
        order.status  = 'confirmed'
        order.save()

        # Dispatch Test Payment Success Notification
        send_order_confirmation_email(order)

        return Response({
            'status':           'success',
            'message':          '✅ Test payment successful! (DEBUG mode only)',
            'order_id':         order.id,
            'fake_payment_id':  fake_payment_id,
        })


class RazorpayMethodsView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        import urllib.request
        import json
        import base64
        import ssl

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        key_id = (settings.RAZORPAY_KEY_ID or '').strip()
        key_secret = (settings.RAZORPAY_KEY_SECRET or '').strip()

        url = "https://api.razorpay.com/v1/methods"
        auth_str = f"{key_id}:{key_secret}"
        auth_bytes = auth_str.encode('utf-8')
        auth_b64 = base64.b64encode(auth_bytes).decode('utf-8')

        headers = {
            "Authorization": f"Basic {auth_b64}"
        }

        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=ctx) as res:
                data = json.loads(res.read().decode('utf-8'))
                return Response({
                    "key_id": key_id,
                    "methods": data
                })
        except Exception as e:
            return Response({
                "key_id": key_id,
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

