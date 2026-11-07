from decimal import Decimal

from django.db import models
from django.urls import reverse

from .utils import uk_slugify


class Category(models.Model):
    """Категорія меню: Піца, Суші, Напої..."""
    name = models.CharField('Назва', max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    emoji = models.CharField('Іконка', max_length=8, blank=True, help_text='Один емодзі, напр. 🍕')
    sort = models.PositiveIntegerField('Порядок', default=0, help_text='Менше число — вище в списку')

    class Meta:
        ordering = ['sort', 'name']
        verbose_name = 'Категорія'
        verbose_name_plural = 'Категорії'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = uk_slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Product(models.Model):
    """Страва або напій."""
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name='products', verbose_name='Категорія'
    )
    name = models.CharField('Назва', max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    short = models.CharField('Короткий опис', max_length=160, blank=True,
                             help_text='Показується на картці, 1 рядок')
    description = models.TextField('Опис')
    ingredients = models.TextField('Склад', blank=True, help_text='Через кому: тісто, томати, моцарела')
    weight = models.CharField('Вага / обʼєм', max_length=40, blank=True, help_text='Напр. 550 г або 0,5 л')
    price = models.DecimalField('Ціна, ₴', max_digits=10, decimal_places=2)
    old_price = models.DecimalField(
        'Стара ціна, ₴', max_digits=10, decimal_places=2, null=True, blank=True,
        help_text='Заповніть, якщо є знижка'
    )
    stock = models.PositiveIntegerField('Порцій на кухні', default=0,
                                        help_text='0 — показати «Немає» і вимкнути кнопку')
    image = models.FileField('Фото', upload_to='products/', blank=True)
    is_featured = models.BooleanField('Хіт меню', default=False)
    is_active = models.BooleanField('Показувати в меню', default=True)
    created_at = models.DateTimeField('Додано', auto_now_add=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']
        verbose_name = 'Страва'
        verbose_name_plural = 'Меню'

    def save(self, *args, **kwargs):
        if not self.slug:
            base = uk_slugify(self.name) or 'strawa'
            slug, i = base, 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                i += 1
                slug = f'{base}-{i}'
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('store:product', kwargs={'slug': self.slug})

    @property
    def discount_percent(self):
        if self.old_price and self.old_price > self.price:
            return round((self.old_price - self.price) / self.old_price * 100)
        return 0

    def __str__(self):
        return self.name


class Order(models.Model):
    """Замовлення їжі. Корзина живе в сесії, тут — уже оформлене замовлення."""
    STATUS_NEW = 'new'
    STATUS_CHOICES = [
        (STATUS_NEW, 'Нове'),
        ('cooking', 'Готується'),
        ('delivering', 'Везе курʼєр'),
        ('done', 'Виконано'),
        ('cancelled', 'Скасовано'),
    ]
    DELIVERY_DELIVERY = 'delivery'
    DELIVERY_CHOICES = [
        (DELIVERY_DELIVERY, 'Доставка курʼєром'),
        ('pickup', 'Самовивіз'),
    ]
    PAYMENT_CHOICES = [
        ('cash', 'Готівкою курʼєру'),
        ('card', 'Карткою курʼєру'),
        ('online', 'Онлайн-оплата'),
    ]
    TIME_CHOICES = [
        ('asap', 'Якнайшвидше (40–60 хв)'),
        ('hour', 'Протягом години'),
        ('later', 'На пізніший час'),
    ]

    name = models.CharField('Імʼя', max_length=120)
    phone = models.CharField('Телефон', max_length=30)
    email = models.EmailField('Email', blank=True)
    delivery = models.CharField('Спосіб отримання', max_length=20,
                                choices=DELIVERY_CHOICES, default=DELIVERY_DELIVERY)
    address = models.CharField('Адреса', max_length=250, blank=True,
                               help_text='Вулиця, будинок, квартира, підʼїзд')
    time_slot = models.CharField('Час', max_length=20, choices=TIME_CHOICES, default='asap')
    payment = models.CharField('Оплата', max_length=20, choices=PAYMENT_CHOICES, default='cash')
    comment = models.TextField('Коментар', blank=True)
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)
    total = models.DecimalField('Сума, ₴', max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField('Створено', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Замовлення'
        verbose_name_plural = 'Замовлення'

    @property
    def number(self):
        return f'№{self.pk:05d}'

    @property
    def items_count(self):
        return sum(item.qty for item in self.items.all())

    def __str__(self):
        return f'{self.number} — {self.name}'

class OrderItem(models.Model):
    """Позиція замовлення: фіксуємо назву й ціну на момент покупки."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Замовлення')
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Страва'
    )
    name = models.CharField('Назва', max_length=200)
    price = models.DecimalField('Ціна, ₴', max_digits=10, decimal_places=2)
    qty = models.PositiveIntegerField('Кількість', default=1)

    class Meta:
        verbose_name = 'Позиція замовлення'
        verbose_name_plural = 'Позиції замовлення'

    @property
    def line_total(self):
        return self.price * self.qty

    def __str__(self):
        return f'{self.name} × {self.qty}'
