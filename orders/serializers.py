from rest_framework import serializers
from .models import Order, OrderItem, OrderReview
from menu.models import MenuItem
from accounts.serializers import UserSerializer


class OrderItemCreateSerializer(serializers.Serializer):
    menu_item_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)


class OrderItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.ReadOnlyField()

    class Meta:
        model = OrderItem
        fields = ('id', 'menu_item', 'item_name', 'item_price', 'quantity', 'subtotal')


class OrderReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderReview
        fields = ('id', 'food_rating', 'driver_rating', 'comments', 'created_at')
        read_only_fields = ('id', 'created_at')


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    review = serializers.SerializerMethodField()

    def get_review(self, obj):
        if hasattr(obj, 'review'):
            return OrderReviewSerializer(obj.review).data
        return None

    class Meta:
        model = Order
        fields = ('id', 'user', 'status', 'status_display', 'total_amount', 'delivery_address',
                  'notes', 'payment_method', 'is_paid', 'items', 'created_at', 'updated_at',
                  'delivery_lat', 'delivery_lng', 'driver_lat', 'driver_lng', 'driver_name', 'driver_phone', 'delivery_otp', 'review')
        read_only_fields = ('id', 'user', 'total_amount', 'is_paid', 'created_at', 'updated_at', 'delivery_otp', 'review')


class CreateOrderSerializer(serializers.Serializer):
    items = OrderItemCreateSerializer(many=True)
    delivery_address = serializers.CharField()
    delivery_lat = serializers.FloatField(required=False, allow_null=True)
    delivery_lng = serializers.FloatField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    payment_method = serializers.CharField(required=False, default='online')

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError("Order must have at least one item.")
        return items

    def validate(self, attrs):
        delivery_lat = attrs.get('delivery_lat')
        delivery_lng = attrs.get('delivery_lng')
        
        if delivery_lat is None or delivery_lng is None:
            raise serializers.ValidationError({
                "location": "Delivery coordinates are required to verify delivery eligibility. Please select your location on the map."
            })
            
        # Restaurant location: MSR Rayalaseema Ruchulu (Podili)
        RESTAURANT_LAT = 15.6249768
        RESTAURANT_LNG = 79.6233953
        
        # Calculate Haversine distance
        import math
        R = 6371.0  # Radius of Earth in km
        
        lat1 = math.radians(RESTAURANT_LAT)
        lon1 = math.radians(RESTAURANT_LNG)
        lat2 = math.radians(delivery_lat)
        lon2 = math.radians(delivery_lng)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        
        if distance > 10.0:
            raise serializers.ValidationError({
                "location": f"We do not deliver to this location. Delivery is only available within 10 km. (Your distance: {distance:.2f} km)"
            })
            
        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        items_data = validated_data.pop('items')
        total = 0
        order_items = []

        for item_data in items_data:
            try:
                menu_item = MenuItem.objects.get(id=item_data['menu_item_id'], is_available=True)
            except MenuItem.DoesNotExist:
                raise serializers.ValidationError(f"Menu item {item_data['menu_item_id']} not available.")
            subtotal = menu_item.price * item_data['quantity']
            total += subtotal
            order_items.append((menu_item, item_data['quantity']))

        # Round tax to nearest integer to match Math.round(totalPrice * 0.05) on the frontend
        from decimal import Decimal
        tax = int(round(float(total) * 0.05))
        total_with_tax = total + Decimal(str(tax))

        import random
        delivery_otp = str(random.randint(1000, 9999))
        order = Order.objects.create(user=user, total_amount=total_with_tax, delivery_otp=delivery_otp, **validated_data)

        for menu_item, quantity in order_items:
            OrderItem.objects.create(
                order=order,
                menu_item=menu_item,
                item_name=menu_item.name,
                item_price=menu_item.price,
                quantity=quantity
            )
        return order


class UpdateOrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('status',)


class UpdateDriverLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('driver_lat', 'driver_lng')
