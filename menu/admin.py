from django.contrib import admin
from django.utils.html import format_html
from .models import Category, MenuItem, GalleryImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display        = ('name', 'item_count', 'active_status', 'is_active', 'sort_order')
    list_filter         = ('is_active',)
    search_fields       = ('name', 'description')
    ordering            = ('sort_order', 'name')
    list_editable       = ('is_active', 'sort_order')
    list_per_page       = 20
    save_on_top         = True

    def item_count(self, obj):
        count = obj.items.filter(is_available=True).count()
        return format_html('<span style="font-weight:700; color:#fd7e14;">{}</span>', count)
    item_count.short_description = '🍽️ Items'

    def active_status(self, obj):
        if obj.is_active:
            return format_html('<span style="color:#28a745; font-weight:700;">✓ Active</span>')
        return format_html('<span style="color:#dc3545;">✗ Hidden</span>')
    active_status.short_description = 'Status'


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display        = ('image_preview', 'name', 'category', 'formatted_price',
                           'veg_badge', 'spice_level', 'is_available',
                           'is_featured', 'is_bestseller', 'star_rating')
    list_filter         = ('category', 'is_available', 'is_vegetarian',
                           'is_featured', 'is_bestseller', 'spice_level')
    search_fields       = ('name', 'description')
    list_editable       = ('is_available', 'is_featured', 'is_bestseller')
    ordering            = ('category__sort_order', 'name')
    list_per_page       = 25
    list_select_related = ('category',)
    save_on_top         = True
    list_display_links  = ('image_preview', 'name')

    fieldsets = (
        ('📋 Basic Information', {
            'fields': ('category', 'name', 'description', 'price')
        }),
        ('🖼️ Food Photo', {
            'fields': ('image',),
            'description': 'Enter image URL (e.g. /images/chicken_biryani.png) or upload a photo',
        }),
        ('🏷️ Tags & Properties', {
            'fields': (
                ('is_vegetarian', 'is_available'),
                ('is_featured', 'is_bestseller'),
                ('spice_level', 'preparation_time'),
            )
        }),
        ('⭐ Ratings', {
            'fields': (('rating', 'rating_count'),),
            'classes': ('collapse',),
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            try:
                url = obj.image.url
            except AttributeError:
                url = obj.image
            return format_html(
                '<img src="{}" style="height:52px;width:70px;object-fit:cover;'
                'border-radius:8px;border:2px solid #fd7e14;" />',
                url
            )
        return format_html('<span style="font-size:1.5rem;">🍽️</span>')
    image_preview.short_description = 'Photo'

    def formatted_price(self, obj):
        return format_html('<strong style="color:#fd7e14;">₹{}</strong>',
                           int(obj.price))
    formatted_price.short_description = '💰 Price'
    formatted_price.admin_order_field = 'price'

    def veg_badge(self, obj):
        if obj.is_vegetarian:
            return format_html('<span style="color:#28a745; font-weight:700; '
                               'background:#d4edda; padding:2px 8px; border-radius:12px; '
                               'font-size:0.8rem;">🟢 Veg</span>')
        return format_html('<span style="color:#dc3545; font-weight:700; '
                           'background:#f8d7da; padding:2px 8px; border-radius:12px; '
                           'font-size:0.8rem;">🔴 Non-Veg</span>')
    veg_badge.short_description = 'Type'

    def availability(self, obj):
        if obj.is_available:
            return format_html('<span style="color:#28a745; font-weight:700;">✓ Available</span>')
        return format_html('<span style="color:#dc3545;">✗ Hidden</span>')
    availability.short_description = 'Available'

    def star_rating(self, obj):
        stars = '⭐' * int(round(obj.rating or 0))
        return format_html('{} <small style="color:#6c757d;">({})</small>',
                           stars, f'{float(obj.rating or 0):.1f}')
    star_rating.short_description = 'Rating'

@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ('image_preview', 'title', 'created_at', 'is_visible')
    list_editable = ('is_visible',)
    list_filter = ('is_visible', 'created_at')
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:52px;width:70px;object-fit:cover;'
                'border-radius:8px;border:2px solid #fd7e14;" />',
                obj.image.url
            )
        return ""
    image_preview.short_description = 'Photo'

