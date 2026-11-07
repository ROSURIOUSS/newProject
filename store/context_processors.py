from django.conf import settings
from django.utils import timezone

from .cart import Cart

def cart(request):
    """Спільні дані для всіх шаблонів: кошик, контакти, умови доставки."""
    c = Cart(request)
    return {
        'cart_count': c.count,
        'min_order': settings.MIN_ORDER,
        'free_shipping_from': settings.FREE_SHIPPING_FROM,
        'shipping_cost': settings.SHIPPING_COST,
        'site': {
            'name': settings.SITE_NAME,
            'tagline': settings.SITE_TAGLINE,
            'city': settings.SITE_CITY,
            'city_loc': settings.SITE_CITY_LOC,
            'city_dat': settings.SITE_CITY_DAT,
            'city_gen': settings.SITE_CITY_GEN,
            'phone': settings.SITE_PHONE,
            'phone_link': settings.SITE_PHONE_LINK,
            'email': settings.SITE_EMAIL,
            'address': settings.SITE_ADDRESS,
            'hours': settings.SITE_HOURS,
            'map_query': settings.SITE_MAP_QUERY,
            'keywords': settings.SITE_KEYWORDS,
            'year': timezone.now().year,
        },
    }
