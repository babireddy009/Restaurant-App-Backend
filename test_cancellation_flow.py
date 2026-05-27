import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from orders.models import Order
from payments.models import Payment
from rest_framework.test import APIRequestFactory, force_authenticate
from orders.views import CancelOrderView, UpdateOrderStatusView
from decimal import Decimal

User = get_user_model()

# Setup test user and staff
user, _ = User.objects.get_or_create(username='test_customer', defaults={'email': 'customer@example.com', 'role': 'customer'})
staff, _ = User.objects.get_or_create(username='test_staff', defaults={'email': 'staff@example.com', 'role': 'staff'})

factory = APIRequestFactory()

def test_refund_before_prepare():
    print("\n--- Test 1: Refund before preparation (confirmed) ---")
    order = Order.objects.create(
        user=user,
        total_amount=Decimal('150.00'),
        payment_method='online',
        status='confirmed',
        is_paid=True
    )
    payment = Payment.objects.create(
        order=order,
        razorpay_order_id='order_mock_123',
        razorpay_payment_id='pay_TEST_MOCK_123',
        amount=Decimal('150.00'),
        status='success'
    )
    
    view = CancelOrderView.as_view()
    request = factory.post(f'/api/orders/{order.id}/cancel/')
    force_authenticate(request, user=user)
    
    response = view(request, pk=order.id)
    print(f"Response Status: {response.status_code}")
    print(f"Response Message: {response.data.get('message')}")
    
    # Reload from DB
    order.refresh_from_db()
    payment.refresh_from_db()
    print(f"Order Status in DB: {order.status}")
    print(f"Payment Status in DB: {payment.status}")
    assert order.status == 'cancelled', "Order status should be cancelled"
    assert payment.status == 'refunded', "Payment status should be refunded"
    print("SUCCESS: Full refund simulation succeeded!")

def test_no_refund_after_prepare():
    print("\n--- Test 2: No refund after preparation (preparing) ---")
    order = Order.objects.create(
        user=user,
        total_amount=Decimal('200.00'),
        payment_method='online',
        status='preparing',
        is_paid=True
    )
    payment = Payment.objects.create(
        order=order,
        razorpay_order_id='order_mock_456',
        razorpay_payment_id='pay_TEST_MOCK_456',
        amount=Decimal('200.00'),
        status='success'
    )
    
    view = CancelOrderView.as_view()
    request = factory.post(f'/api/orders/{order.id}/cancel/')
    force_authenticate(request, user=user)
    
    response = view(request, pk=order.id)
    print(f"Response Status: {response.status_code}")
    print(f"Response Message: {response.data.get('message')}")
    
    # Reload from DB
    order.refresh_from_db()
    payment.refresh_from_db()
    print(f"Order Status in DB: {order.status}")
    print(f"Payment Status in DB: {payment.status}")
    assert order.status == 'cancelled', "Order status should be cancelled"
    assert payment.status == 'success', "Payment status should remain success (no refund)"
    print("SUCCESS: 100% cancellation charge logic succeeded!")

def test_cod_cancellation_blocked():
    print("\n--- Test 3: COD cancellation blocked ---")
    order = Order.objects.create(
        user=user,
        total_amount=Decimal('120.00'),
        payment_method='cod',
        status='confirmed',
        is_paid=False
    )
    
    view = CancelOrderView.as_view()
    request = factory.post(f'/api/orders/{order.id}/cancel/')
    force_authenticate(request, user=user)
    
    response = view(request, pk=order.id)
    print(f"Response Status: {response.status_code}")
    print(f"Response Error: {response.data.get('error')}")
    
    # Reload from DB
    order.refresh_from_db()
    print(f"Order Status in DB: {order.status}")
    assert response.status_code == 400
    assert order.status == 'confirmed', "COD Order status should not change"
    print("SUCCESS: COD cancellation was successfully blocked!")

def test_staff_update_blocked_on_cancelled():
    print("\n--- Test 4: Staff status update blocked on cancelled order ---")
    order = Order.objects.create(
        user=user,
        total_amount=Decimal('100.00'),
        payment_method='online',
        status='cancelled',
        is_paid=True
    )
    
    view = UpdateOrderStatusView.as_view()
    request = factory.patch(f'/api/orders/{order.id}/status/', {'status': 'preparing'}, format='json')
    force_authenticate(request, user=staff)
    
    response = view(request, pk=order.id)
    print(f"Response Status: {response.status_code}")
    print(f"Response Error: {response.data.get('error')}")
    
    # Reload from DB
    order.refresh_from_db()
    print(f"Order Status in DB: {order.status}")
    assert response.status_code == 400
    assert order.status == 'cancelled', "Order status should remain cancelled"
    print("SUCCESS: Staff update on cancelled order was successfully blocked!")

if __name__ == '__main__':
    test_refund_before_prepare()
    test_no_refund_after_prepare()
    test_cod_cancellation_blocked()
    test_staff_update_blocked_on_cancelled()
