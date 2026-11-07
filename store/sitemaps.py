from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Product

class ProductSitemap(Sitemap):
    """Усі страви в sitemap.xml."""
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Product.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.created_at

class StaticSitemap(Sitemap):
    """Головні сторінки сайту."""
    priority = 0.6
    changefreq = 'monthly'

    def items(self):
        return ['store:index', 'store:about', 'store:delivery', 'store:contacts']

    def location(self, item):
        return reverse(item)

sitemaps = {'products': ProductSitemap, 'pages': StaticSitemap}
