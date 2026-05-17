from django.conf import settings
from django.urls import path
from .views import CreatePaymentView, VerifyPaymentView, PaymentStatusView, TestPaymentSuccessView

urlpatterns = [
    path('create/',                 CreatePaymentView.as_view(),        name='payment-create'),
    path('verify/',                 VerifyPaymentView.as_view(),        name='payment-verify'),
    path('status/<int:order_id>/',  PaymentStatusView.as_view(),        name='payment-status'),
]

# ⚠️  DEV ONLY: test-success bypass (disabled automatically in production)
if settings.DEBUG:
    urlpatterns += [
        path('test-success/',       TestPaymentSuccessView.as_view(),   name='payment-test-success'),
    ]
