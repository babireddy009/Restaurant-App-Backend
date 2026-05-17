from django.urls import path
from .views import (
    CategoryListView, CategoryDetailView,
    MenuItemListView, MenuItemDetailView, FeaturedItemsView,
    GalleryImageView
)

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    path('items/', MenuItemListView.as_view(), name='menuitem-list'),
    path('items/<int:pk>/', MenuItemDetailView.as_view(), name='menuitem-detail'),
    path('featured/', FeaturedItemsView.as_view(), name='featured-items'),
    path('gallery/', GalleryImageView.as_view(), name='gallery-images'),
]
