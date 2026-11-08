from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .cart import Cart
from .forms import CheckoutForm, SignUpForm
from .models import Category, Order, OrderItem, Product

SORT_OPTIONS = {
    'new': ('Новинки', '-created_at'),
    'cheap': ('Спочатку дешевші', 'price'),
    'expensive': ('Спочатку дорожчі', '-price'),
    'name': ('За назвою', 'name'),
}

def index(request):
    """Каталог: пошук + категорія + сортування + пагінація (як index у блозі)."""
    products = Product.objects.filter(is_active=True).select_related('category')
    categories = Category.objects.all()

    selected_category = request.GET.get('category', '')
    query = request.GET.get('q', '').strip()
    sort = request.GET.get('sort', 'new')
    price_min = request.GET.get('min', '')
    price_max = request.GET.get('max', '')

    if selected_category:
        products = products.filter(category__slug=selected_category)
    if query:
        variants = {query, query.lower(), query.upper(), query.capitalize(), query.title()}
        found = Q()
        for variant in variants:
            found |= (Q(name__icontains=variant) | Q(description__icontains=variant)
                      | Q(short__icontains=variant))
        products = products.filter(found)
    for value, lookup in ((price_min, 'price__gte'), (price_max, 'price__lte')):
        if value:
            try:
                products = products.filter(**{lookup: Decimal(value)})
            except (InvalidOperation, ValueError):
                pass

    products = products.order_by(SORT_OPTIONS.get(sort, SORT_OPTIONS['new'])[1])

    paginator = Paginator(products, 6)
    page = paginator.get_page(request.GET.get('page'))

    params = request.GET.copy()
    params.pop('page', None)

    context = {
        'page': page,
        'products': page.object_list,
        'categories': categories,
        'selected_category': selected_category,
        'query': query,
        'sort': sort,
        'price_min': price_min,
        'price_max': price_max,
        'sort_options': SORT_OPTIONS,
        'querystring': params.urlencode(),
        'total_found': paginator.count,
        'featured': (Product.objects.filter(is_active=True, is_featured=True)
                     .order_by('category__sort', 'name')[:3]),
        'hero': Product.objects.filter(is_active=True, is_featured=True)
                                 .order_by('category__sort', 'name').first(),
    }
    return render(request, 'store/index.html', context)

def about(request):
    """Сторінка про кухню."""
    return render(request, 'store/about.html', {'page_title': 'Про кухню'})

def delivery(request):
    """Доставка, оплата, зони й тарифи."""
    return render(request, 'store/delivery.html', {'page_title': 'Доставка й оплата'})

def contacts(request):
    """Контакти, графік роботи, адреса."""
    return render(request, 'store/contacts.html', {'page_title': 'Контакти'})

def product_detail(request, slug):
    product = get_object_or_404(Product.objects.select_related('category'), slug=slug, is_active=True)
    related = Product.objects.filter(category=product.category, is_active=True).exclude(pk=product.pk)[:3]
    return render(request, 'store/product.html', {'product': product, 'related': related})

def cart_detail(request):
    return render(request, 'store/cart.html', {'cart': Cart(request)})

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    try:
        qty = int(request.POST.get('qty', 1))
    except ValueError:
        qty = 1
    cart.add(product, max(1, min(qty, 99)))
    if request.POST.get('next') == 'cart':
        return redirect('store:cart')
    return HttpResponseRedirect(request.POST.get('next_url') or reverse('store:cart'))

@require_POST
def cart_set(request, product_id):
    Cart(request).set_qty(product_id, request.POST.get('qty', 1))
    return redirect('store:cart')

@require_POST
def cart_remove(request, product_id):
    Cart(request).remove(product_id)
    return redirect('store:cart')

def register(request):
    """Реєстрація нового клієнта + автовхід."""
    if request.user.is_authenticated:
        return redirect('store:index')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, f'Вітаємо, {user.first_name or user.username}! Акаунт створено.')
            return redirect(request.GET.get('next') or 'store:index')
    else:
        form = SignUpForm()

    return render(request, 'store/register.html', {'form': form})

@login_required
def my_orders(request):
    """Історія замовлень поточного користувача."""
    orders = request.user.orders.prefetch_related('items')
    return render(request, 'store/my_orders.html', {'orders': orders})

@login_required
def checkout(request):
    cart = Cart(request)
    items = cart.items()
    if not items:
        return redirect('store:cart')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.total = cart.total
            order.save()

            OrderItem.objects.bulk_create([
                OrderItem(
                    order=order,
                    product=item['product'],
                    name=item['product'].name,
                    price=item['price'],
                    qty=item['qty'],
                )
                for item in items
            ])
            cart.clear()
            messages.success(request, f'Замовлення {order.number} прийнято в роботу.')
            return redirect('store:order_success', order_id=order.pk)
    else:
        last = request.user.orders.order_by('-created_at').first()
        form = CheckoutForm(initial={
            'name': request.user.first_name or request.user.username,
            'email': request.user.email,
            'phone': last.phone if last else '',
            'address': last.address if last else '',
        })

    return render(request, 'store/checkout.html', {'form': form, 'cart': cart})

def order_success(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if order.user_id != request.user.pk and not request.user.is_staff:
        raise Http404('Замовлення не знайдено')
    return render(request, 'store/success.html', {'order': order})
