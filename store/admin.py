from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html

from .models import Category, Order, OrderItem, Product, Review

MONEY = '{} ₴'


def money(value):
    return MONEY.format(f'{value:.0f}' if value == int(value) else f'{value:.2f}')


STATUS_STYLES = {
    'new': ('status-new', 'Нове'),
    'cooking': ('status-cooking', 'Готується'),
    'delivering': ('status-delivering', 'Везе курʼєр'),
    'done': ('status-done', 'Виконано'),
    'cancelled': ('status-cancelled', 'Скасовано'),
}


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'emoji', 'slug', 'sort', 'products_count']
    list_display_links = ['name', 'emoji']
    list_editable = ['sort']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    save_on_top = True

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(total_products=Count('products'))

    @admin.display(description='Страв', ordering='total_products')
    def products_count(self, obj):
        total = getattr(obj, 'total_products', obj.products.count())
        if not total:
            return format_html('<span class="pill pill-muted">{}</span>', 0)
        return format_html('<span class="pill pill-count">{}</span>', total)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['thumb', 'name', 'category', 'price_display', 'stock_badge',
                    'is_featured', 'is_active']
    list_display_links = ['thumb', 'name']
    list_editable = ['is_featured', 'is_active']
    list_filter = ['category', 'is_active', 'is_featured']
    search_fields = ['name', 'description', 'ingredients']
    prepopulated_fields = {'slug': ('name',)}
    list_per_page = 20
    save_on_top = True
    readonly_fields = ['image_preview']
    actions = ['make_active', 'make_hidden', 'make_featured']
    fieldsets = (
        ('Основне', {'fields': ('category', 'name', 'slug', 'short', 'image', 'image_preview')}),
        ('Опис', {'fields': ('description', 'ingredients', 'weight')}),
        ('Ціна та наявність', {'fields': ('price', 'old_price', 'stock')}),
        ('Показ', {'fields': ('is_featured', 'is_active')}),
    )

    @admin.display(description='Фото')
    def thumb(self, obj):
        if obj.image:
            return format_html('<img src="{}" class="admin-thumb">', obj.image.url)
        return format_html('<span class="pill pill-muted">{}</span>', 'нема')

    @admin.display(description='Фото', ordering='image')
    def image_preview(self, obj):
        if obj and obj.image:
            return format_html('<img src="{}" class="admin-preview">', obj.image.url)
        return '—'

    @admin.display(description='Ціна, ₴', ordering='price')
    def price_display(self, obj):
        if obj.old_price and obj.old_price > obj.price:
            return format_html(
                '<span class="price-now">{}</span> <s class="price-old">{}</s>',
                money(obj.price), money(obj.old_price))
        return format_html('<span class="price-now">{}</span>', money(obj.price))

    @admin.display(description='Порцій', ordering='stock')
    def stock_badge(self, obj):
        if obj.stock == 0:
            return format_html('<span class="pill pill-out">{}</span>', 'немає')
        if obj.stock <= 5:
            return format_html('<span class="pill pill-low">{}</span>', obj.stock)
        return format_html('<span class="pill pill-ok">{}</span>', obj.stock)

    @admin.action(description='Показати в меню')
    def make_active(self, request, queryset):
        changed = queryset.update(is_active=True)
        self.message_user(request, f'Показано в меню: {changed}')

    @admin.action(description='Прибрати з меню')
    def make_hidden(self, request, queryset):
        changed = queryset.update(is_active=False)
        self.message_user(request, f'Прибрано з меню: {changed}')

    @admin.action(description='Позначити як хіт меню')
    def make_featured(self, request, queryset):
        changed = queryset.update(is_featured=True)
        self.message_user(request, f'Додано до хітів: {changed}')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ['product', 'name', 'price', 'qty', 'line_total']
    readonly_fields = ['product', 'name', 'price', 'qty', 'line_total']

    @admin.display(description='Сума')
    def line_total(self, obj):
        return money(obj.line_total) if obj and obj.pk else '—'

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['number', 'status_badge', 'user', 'name', 'phone', 'delivery',
                    'total_display', 'created_at']
    list_display_links = ['number']
    list_filter = ['status', 'delivery', 'payment', 'created_at']
    search_fields = ['name', 'phone', 'address', 'user__username', 'pk']
    list_select_related = ['user']
    readonly_fields = ['number', 'total_display', 'created_at']
    inlines = [OrderItemInline]
    date_hierarchy = 'created_at'
    save_on_top = True
    actions = ['mark_cooking', 'mark_delivering', 'mark_done', 'mark_cancelled']
    fieldsets = (
        ('Замовлення', {'fields': ('number', ('status', 'total_display'), 'created_at')}),
        ('Клієнт', {'fields': ('user', 'name', ('phone', 'email'))}),
        ('Отримання', {'fields': (('delivery', 'time_slot'), 'address')}),
        ('Оплата і коментар', {'fields': ('payment', 'comment')}),
    )

    @admin.display(description='Замовлення', ordering='pk')
    def number(self, obj):
        return obj.number if obj and obj.pk else '—'

    @admin.display(description='Статус', ordering='status')
    def status_badge(self, obj):
        css, label = STATUS_STYLES.get(obj.status, ('status-new', obj.get_status_display()))
        return format_html('<span class="order-status {}">{}</span>', css, label)

    @admin.display(description='Сума, ₴', ordering='total')
    def total_display(self, obj):
        return money(obj.total)

    @admin.action(description='Готується')
    def mark_cooking(self, request, queryset):
        changed = queryset.update(status='cooking')
        self.message_user(request, f'Переведено в «Готується»: {changed}')

    @admin.action(description='Везе курʼєр')
    def mark_delivering(self, request, queryset):
        changed = queryset.update(status='delivering')
        self.message_user(request, f'Переведено в «Везе курʼєр»: {changed}')

    @admin.action(description='Виконано')
    def mark_done(self, request, queryset):
        changed = queryset.update(status='done')
        self.message_user(request, f'Позначено виконаними: {changed}')

    @admin.action(description='Скасовано')
    def mark_cancelled(self, request, queryset):
        changed = queryset.update(status='cancelled')
        self.message_user(request, f'Скасовано: {changed}')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'author', 'stars_display', 'short_text', 'created_at']
    list_display_links = ['product', 'author']
    list_filter = ['rating', 'created_at']
    search_fields = ['text', 'user__username', 'product__name']
    readonly_fields = ['created_at', 'updated_at']
    list_select_related = ['user', 'product']
    date_hierarchy = 'created_at'

    @admin.display(description='Клієнт', ordering='user__username')
    def author(self, obj):
        return obj.author

    @admin.display(description='Оцінка', ordering='rating')
    def stars_display(self, obj):
        return format_html('<span class="admin-stars">{}</span>', obj.stars)

    @admin.display(description='Відгук')
    def short_text(self, obj):
        text = obj.text if len(obj.text) <= 60 else obj.text[:60] + '…'
        return text
