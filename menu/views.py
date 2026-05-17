from django.db.models import Count
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import generics, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Category, MenuItem, GalleryImage
from .serializers import CategorySerializer, CategoryListSerializer, MenuItemSerializer, GalleryImageSerializer


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role in ('admin', 'staff')


class CategoryListView(generics.ListCreateAPIView):
    queryset = Category.objects.filter(is_active=True).annotate(item_count=Count('items')).prefetch_related('items')
    permission_classes = (IsAdminOrReadOnly,)

    @method_decorator(cache_page(60 * 15))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.request.query_params.get('with_items'):
            return CategorySerializer
        return CategoryListSerializer


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)


class MenuItemListView(generics.ListCreateAPIView):
    serializer_class = MenuItemSerializer
    permission_classes = (IsAdminOrReadOnly,)

    @method_decorator(cache_page(60 * 15))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = MenuItem.objects.select_related('category').filter(is_available=True)
        category = self.request.query_params.get('category')
        vegetarian = self.request.query_params.get('vegetarian')
        featured = self.request.query_params.get('featured')
        search = self.request.query_params.get('search')

        if category:
            queryset = queryset.filter(category_id=category)
        if vegetarian == 'true':
            queryset = queryset.filter(is_vegetarian=True)
        if featured == 'true':
            queryset = queryset.filter(is_featured=True)
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset


class MenuItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = (IsAdminOrReadOnly,)


class FeaturedItemsView(generics.ListAPIView):
    queryset = MenuItem.objects.select_related('category').filter(is_featured=True, is_available=True)
    serializer_class = MenuItemSerializer
    permission_classes = (permissions.AllowAny,)

class GalleryImageView(generics.ListAPIView):
    queryset = GalleryImage.objects.filter(is_visible=True)
    serializer_class = GalleryImageSerializer
    permission_classes = (permissions.AllowAny,)

    @method_decorator(cache_page(60 * 15))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
