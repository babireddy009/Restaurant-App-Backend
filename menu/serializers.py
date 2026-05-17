from rest_framework import serializers
from .models import Category, MenuItem, GalleryImage


class MenuItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = MenuItem
        fields = (
            'id', 'category', 'category_name', 'name', 'description', 'price',
            'image', 'is_available', 'is_vegetarian', 'is_featured', 'is_bestseller',
            'spice_level', 'preparation_time', 'rating', 'rating_count', 'created_at'
        )


class CategorySerializer(serializers.ModelSerializer):
    items = MenuItemSerializer(many=True, read_only=True)
    item_count = serializers.IntegerField(source='items.count', read_only=True)

    class Meta:
        model = Category
        fields = ('id', 'name', 'description', 'image', 'is_active', 'sort_order', 'item_count', 'items')


class CategoryListSerializer(serializers.ModelSerializer):
    item_count = serializers.IntegerField(source='items.count', read_only=True)

    class Meta:
        model = Category
        fields = ('id', 'name', 'description', 'image', 'is_active', 'item_count')

class GalleryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GalleryImage
        fields = ('id', 'title', 'image', 'created_at', 'is_visible')
