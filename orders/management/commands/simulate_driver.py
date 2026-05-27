from django.core.management.base import BaseCommand
from orders.models import Order
import time
import math

class Command(BaseCommand):
    help = 'Simulates driver movement for orders that are out for delivery'

    def handle(self, *args, **options):
        self.stdout.write("Starting driver simulation... Press Ctrl+C to stop.")
        
        try:
            while True:
                # ── Move drivers for out_for_delivery orders ──
                orders = Order.objects.filter(status='out_for_delivery')
                if not orders.exists():
                    self.stdout.write("No active orders out for delivery to simulate. Waiting...")
                    time.sleep(5)
                    continue

                for order in orders:
                    # If coordinates aren't set, initialize them
                    if not order.delivery_lat or not order.delivery_lng:
                        # Mock destination (e.g., somewhere in a city)
                        order.delivery_lat = 17.3850
                        order.delivery_lng = 78.4867
                    
                    if not order.driver_lat or not order.driver_lng:
                        # Mock starting point (e.g., the restaurant)
                        order.driver_lat = 15.625224761297483
                        order.driver_lng = 79.62384590419613
                        order.driver_name = "Raju (Delivery Partner)"
                        order.driver_phone = "+919876543210"

                    # Calculate distance
                    dlat = order.delivery_lat - order.driver_lat
                    dlng = order.delivery_lng - order.driver_lng
                    distance = math.sqrt(dlat**2 + dlng**2)

                    # If very close, stop moving and wait for OTP
                    if distance < 0.001:
                        self.stdout.write(f"Driver arrived for Order #{order.id}. Waiting for OTP confirmation...")
                        continue

                    # Move driver 5% closer
                    order.driver_lat += dlat * 0.05
                    order.driver_lng += dlng * 0.05
                    order.save()
                    
                    self.stdout.write(f"Updated Order #{order.id} driver location: ({order.driver_lat}, {order.driver_lng})")

                time.sleep(3) # Update every 3 seconds

        except KeyboardInterrupt:
            self.stdout.write("Simulation stopped.")
