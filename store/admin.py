from django.contrib import admin
from django.utils.html import format_html

from .models import Category, Order, OrderItem, Product, Review

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'emoji', 'slug', 'sort', 'products_count']
    list_editable = ['sort']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

    @admin.display(description='Страв')
    def products_count(self, obj):
        return obj.products.count()

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['thumb', 'name', 'category', 'weight', 'price', 'old_price', 'stock',
                    'is_featured', 'is_active']
    list_display_links = ['thumb', 'name']
    list_editable = ['price', 'stock', 'is_featured', 'is_active']
    list_filter = ['category', 'is_active', 'is_featured']
    search_fields = ['name', 'description', 'ingredients']
    prepopulated_fields = {'slug': ('name',)}
    list_per_page = 20
    fieldsets = (
        ('Основне', {'fields': ('category', 'name', 'slug', 'short', 'image')}),
        ('Опис', {'fields': ('description', 'ingredients', 'weight')}),
        ('Ціна та наявність', {'fields': ('price', 'old_price', 'stock')}),
        ('Показ', {'fields': ('is_featured', 'is_active')}),
    )

    @admin.display(description='Фото')
    def thumb(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:38px;border-radius:6px">', obj.image.url)
        return '—'

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ['name', 'price', 'qty', 'line_total']
    readonly_fields = ['name', 'price', 'qty', 'line_total']

    @admin.display(description='Сума')
    def line_total(self, obj):
        return obj.line_total

    def has_add_permission(self, request, obj=None):
        return False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['number', 'user', 'name', 'phone', 'delivery', 'address', 'total', 'status', 'created_at']
    list_filter = ['status', 'delivery', 'payment', 'created_at']
    search_fields = ['name', 'phone', 'address', 'user__username']
    list_select_related = ['user']
    list_editable = ['status']
    readonly_fields = ['total', 'created_at']
    inlines = [OrderItemInline]
    date_hierarchy = 'created_at'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'author', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('text', 'user__username', 'product__name')
    readonly_fields = ('created_at', 'updated_at')

    @admin.display(description='Клієнт')
    def author(self, obj):
        return obj.author
