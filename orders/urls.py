from django.urls import path
from .views import (
    OrderListCreateView, OrderDetailView, StaffOrderListView, 
    UpdateOrderStatusView, UpdateDriverLocationView, ConfirmDeliveryView, 
    DriverOrderView, DriverAvailableOrdersView, DriverMyDeliveriesView, AssignDriverView,
    SubmitReviewView, AnalyticsView, CancelOrderView
)

urlpatterns = [
    path('', OrderListCreateView.as_view(), name='order-list-create'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('staff/all/', StaffOrderListView.as_view(), name='staff-order-list'),
    path('analytics/', AnalyticsView.as_view(), name='analytics-dashboard'),
    path('<int:pk>/status/', UpdateOrderStatusView.as_view(), name='order-status-update'),
    path('<int:pk>/driver-location/', UpdateDriverLocationView.as_view(), name='order-driver-location'),
    path('<int:pk>/confirm-delivery/', ConfirmDeliveryView.as_view(), name='order-confirm-delivery'),
    path('<int:pk>/driver-view/', DriverOrderView.as_view(), name='order-driver-view'),
    path('driver/available/', DriverAvailableOrdersView.as_view(), name='driver-available-orders'),
    path('driver/my-deliveries/', DriverMyDeliveriesView.as_view(), name='driver-my-deliveries'),
    path('<int:pk>/assign-driver/', AssignDriverView.as_view(), name='order-assign-driver'),
    path('<int:pk>/review/', SubmitReviewView.as_view(), name='order-submit-review'),
    path('<int:pk>/cancel/', CancelOrderView.as_view(), name='order-cancel'),
]
