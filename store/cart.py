"""Корзина на сесіях — без БД і без JS. Класика для початкового магазину."""
from decimal import Decimal

from django.conf import settings

from .models import Product

class Cart:
    def __init__(self, request):
        self.session = request.session
        self.cart = self.session.get(settings.CART_SESSION_ID, {})

    def add(self, product, qty=1):
        key = str(product.pk)
        item = self.cart.get(key, {'qty': 0, 'price': str(product.price)})
        item['qty'] = min(item['qty'] + int(qty), 99)
        item['price'] = str(product.price)
        self.cart[key] = item
        self.save()

    def set_qty(self, product_id, qty):
        key = str(product_id)
        if key not in self.cart:
            return
        qty = int(qty)
        if qty <= 0:
            self.cart.pop(key)
        else:
            self.cart[key]['qty'] = min(qty, 99)
        self.save()

    def remove(self, product_id):
        self.cart.pop(str(product_id), None)
        self.save()

    def clear(self):
        self.session[settings.CART_SESSION_ID] = {}
        self.session.modified = True
        self.cart = {}

    def save(self):
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True

    def __len__(self):
        return sum(item['qty'] for item in self.cart.values())

    @property
    def count(self):
        return len(self)

    def items(self):
        """Віддає позиції разом з обʼєктами товарів і сумами."""
        products = Product.objects.filter(pk__in=self.cart.keys())
        result = []
        for product in products:
            item = self.cart[str(product.pk)]
            qty = item['qty']
            price = Decimal(item['price'])
            result.append({
                'product': product,
                'qty': qty,
                'price': price,
                'line_total': price * qty,
            })
        return result

    @property
    def subtotal(self):
        return sum((item['line_total'] for item in self.items()), Decimal('0'))

    @property
    def shipping(self):
        if not self.cart or self.subtotal >= settings.FREE_SHIPPING_FROM:
            return Decimal('0')
        return Decimal(settings.SHIPPING_COST)

    @property
    def total(self):
        return self.subtotal + self.shipping

    @property
    def left_to_min_order(self):
        left = Decimal(settings.MIN_ORDER) - self.subtotal
        return left if left > 0 else Decimal('0')

    @property
    def free_shipping_left(self):
        left = Decimal(settings.FREE_SHIPPING_FROM) - self.subtotal
        return left if left > 0 else Decimal('0')
