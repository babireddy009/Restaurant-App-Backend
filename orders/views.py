from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Order, OrderItem, OrderReview
from django.db.models import Sum, Avg, Count
from .serializers import OrderSerializer, CreateOrderSerializer, UpdateOrderStatusSerializer, UpdateDriverLocationSerializer, OrderReviewSerializer
from .services import send_order_confirmation_email, send_order_status_update_email
from menu.models import MenuItem


class IsStaffOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ('staff', 'admin')


class OrderListCreateView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        return OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).select_related('user').prefetch_related('items__menu_item')

    def create(self, request, *args, **kwargs):
        try:
            serializer = CreateOrderSerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            order = serializer.save()
            
            if order.payment_method == 'cod':
                send_order_confirmation_email(order)
                
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.exception("Failed to create order")
            return Response({
                'error': 'An unexpected error occurred while placing the order. Please try again.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class StaffOrderListView(generics.ListAPIView):
    """Staff can see ALL orders"""
    serializer_class = OrderSerializer
    permission_classes = (IsStaffOrAdmin,)

    def get_queryset(self):
        queryset = Order.objects.all().select_related('user').prefetch_related('items__menu_item')
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset


class UpdateOrderStatusView(APIView):
    """Staff updates order status"""
    permission_classes = (IsStaffOrAdmin,)

    def patch(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UpdateOrderStatusSerializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        old_status = order.status
        serializer.save()
        
        # If the status mutated, send notification
        if order.status != old_status:
            send_order_status_update_email(order)
            
        return Response(OrderSerializer(order).data)


class IsDriver(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'driver'


class UpdateDriverLocationView(APIView):
    """Driver updates their location"""
    permission_classes = (IsDriver,)

    def patch(self, request, pk):
        try:
            order = Order.objects.get(pk=pk, driver=request.user)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found or not assigned to you'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UpdateDriverLocationSerializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(OrderSerializer(order).data)


class ConfirmDeliveryView(APIView):
    """Driver confirms delivery with OTP"""
    permission_classes = (IsDriver,)

    def post(self, request, pk):
        try:
            order = Order.objects.get(pk=pk, driver=request.user)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found or not assigned to you'}, status=status.HTTP_404_NOT_FOUND)

        otp = request.data.get('otp')
        if not otp:
            return Response({'error': 'OTP is required'}, status=status.HTTP_400_BAD_REQUEST)

        if str(order.delivery_otp) != str(otp):
            return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)

        order.status = 'delivered'
        order.save()
        send_order_status_update_email(order)
        
        return Response({'success': True, 'message': 'Delivery confirmed successfully!'})


class DriverOrderView(APIView):
    """Authenticated read-only view for the driver portal"""
    permission_classes = (IsDriver,)

    def get(self, request, pk):
        try:
            order = Order.objects.get(pk=pk, driver=request.user)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found or not assigned to you'}, status=status.HTTP_404_NOT_FOUND)

        data = {
            'id': order.id,
            'status': order.status,
            'delivery_address': order.delivery_address,
            'notes': order.notes,
            'driver_name': request.user.get_full_name() or request.user.username,
            'driver_phone': request.user.phone,
            'delivery_lat': order.delivery_lat,
            'delivery_lng': order.delivery_lng,
            'customer_name': order.user.get_full_name() or order.user.username,
            'customer_phone': order.user.phone,
        }
        return Response(data)


class DriverAvailableOrdersView(generics.ListAPIView):
    """List orders that are ready and have no driver"""
    serializer_class = OrderSerializer
    permission_classes = (IsDriver,)

    def get_queryset(self):
        return Order.objects.filter(status='ready', driver__isnull=True).select_related('user').prefetch_related('items__menu_item')


class DriverMyDeliveriesView(generics.ListAPIView):
    """List orders assigned to the logged-in driver"""
    serializer_class = OrderSerializer
    permission_classes = (IsDriver,)

    def get_queryset(self):
        return Order.objects.filter(driver=self.request.user).exclude(status='delivered').select_related('user').prefetch_related('items__menu_item')


class AssignDriverView(APIView):
    """Driver claims an order"""
    permission_classes = (IsDriver,)

    def post(self, request, pk):
        try:
            order = Order.objects.get(pk=pk, status='ready', driver__isnull=True)
        except Order.DoesNotExist:
            return Response({'error': 'Order not available for pickup'}, status=status.HTTP_400_BAD_REQUEST)

        order.driver = request.user
        order.status = 'out_for_delivery'
        order.driver_name = request.user.get_full_name() or request.user.username
        order.driver_phone = request.user.phone
        order.save()
        
        send_order_status_update_email(order)
        return Response({'success': True, 'message': 'Order successfully claimed!'})

class SubmitReviewView(APIView):
    """Customer submits a review for a delivered order"""
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk):
        try:
            order = Order.objects.get(pk=pk, user=request.user, status='delivered')
        except Order.DoesNotExist:
            return Response({'error': 'Order not found or not delivered yet'}, status=status.HTTP_404_NOT_FOUND)

        if hasattr(order, 'review'):
            return Response({'error': 'Review already submitted for this order'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = OrderReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        review = serializer.save(order=order, user=request.user)

        # Update menu item ratings
        food_rating = review.food_rating
        for item in order.items.all():
            if item.menu_item:
                menu_item = item.menu_item
                new_count = menu_item.rating_count + 1
                # Calculate new average rating
                new_rating = ((menu_item.rating * menu_item.rating_count) + food_rating) / new_count
                menu_item.rating = new_rating
                menu_item.rating_count = new_count
                menu_item.save()

        return Response(OrderReviewSerializer(review).data, status=status.HTTP_201_CREATED)

class AnalyticsView(APIView):
    """Staff/Admin analytics dashboard data"""
    permission_classes = (IsStaffOrAdmin,)

    def get(self, request):
        delivered_orders = Order.objects.filter(status='delivered')
        total_revenue = delivered_orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        total_orders = delivered_orders.count()
        active_orders = Order.objects.exclude(status__in=['delivered', 'cancelled']).count()

        reviews = OrderReview.objects.all()
        avg_food_rating = reviews.aggregate(Avg('food_rating'))['food_rating__avg'] or 0
        avg_driver_rating = reviews.aggregate(Avg('driver_rating'))['driver_rating__avg'] or 0

        # Top 5 selling items
        top_items_qs = OrderItem.objects.filter(order__status='delivered') \
            .values('item_name') \
            .annotate(total_sold=Sum('quantity')) \
            .order_by('-total_sold')[:5]

        top_items = [{'name': item['item_name'], 'sold': item['total_sold']} for item in top_items_qs]

        return Response({
            'total_revenue': float(total_revenue),
            'total_orders': total_orders,
            'active_orders': active_orders,
            'avg_food_rating': round(avg_food_rating, 1),
            'avg_driver_rating': round(avg_driver_rating, 1),
            'top_items': top_items
        })
