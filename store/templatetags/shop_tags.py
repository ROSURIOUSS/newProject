from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()

@register.filter
def money(value):
    """1299.00 -> '1 299 ₴'"""
    try:
        value = Decimal(value)
    except (InvalidOperation, TypeError, ValueError):
        return '—'
    if value == value.to_integral_value():
        text = f'{int(value):,}'.replace(',', ' ')
    else:
        text = f'{value:,.2f}'.replace(',', ' ').replace('.', ',')
    return f'{text} ₴'
