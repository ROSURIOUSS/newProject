"""python manage.py load_menu — наповнює сайт меню «СМАК».

Категорії та страви створюються з фото: файли беруться зі static/store/menu/
і копіюються в media/products/, далі ними керує адмінка.

    python manage.py load_menu              # додати/оновити меню
    python manage.py load_menu --reset      # спочатку очистити меню
    python manage.py load_menu --photos     # перезалити тільки фото
"""
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from store.models import Category, Product

PHOTO_DIR = Path(settings.BASE_DIR) / 'static' / 'store' / 'menu'

CATEGORIES = [
    ('Піца', '🍕', 1),
    ('Суші', '🍣', 2),
    ('Бургери', '🍔', 3),
    ('Салати', '🥗', 4),
    ('Гаряче та перше', '🍲', 5),
    ('Десерти', '🍰', 6),
    ('Напої', '🥤', 7),
]

MENU = [
    {
        'slug': 'pizza-margherita', 'category': 'Піца', 'name': 'Піца Маргарита',
        'weight': '480 г', 'price': '235', 'stock': 18, 'is_featured': True,
        'short': 'Томати, моцарела, базилік',
        'description': 'Класика на тонкому тісті: томатний соус, моцарела й свіжий базилік. '
                       'Випікаємо 6 хвилин за 400 °C — тісто хрустить, а сир тягнеться.',
        'ingredients': 'Тісто, томатний соус, моцарела, базилік, оливкова олія, орегано',
    },
    {
        'slug': 'pizza-pepperoni', 'category': 'Піца', 'name': 'Піца Пепероні',
        'weight': '520 г', 'price': '265', 'old_price': '295', 'stock': 14, 'is_featured': False,
        'short': 'Подвійна пепероні та чилі-олія',
        'description': 'Для тих, хто любить гостріше: дві порції пепероні, моцарела й крапля '
                       'чилі-олії. Добре сходить із холодним лимонадом.',
        'ingredients': 'Тісто, томатний соус, моцарела, пепероні, чилі-олія, орегано',
    },
    {
        'slug': 'pizza-four-cheese', 'category': 'Піца', 'name': 'Піца «Чотири сири»',
        'weight': '500 г', 'price': '289', 'stock': 11, 'is_featured': False,
        'short': 'Дорблю, чеддер, моцарела, пармезан',
        'description': 'Без томатного соусу: вершкова основа й чотири сири. Дорблю додає '
                       'пікантності, пармезан — солону кірочку по краю.',
        'ingredients': 'Тісто, вершкова основа, моцарела, дорблю, чеддер, пармезан',
    },
    {
        'slug': 'pizza-cheri', 'category': 'Піца', 'name': 'Піца «Чері й базилік»',
        'weight': '470 г', 'price': '249', 'stock': 12, 'is_featured': False,
        'short': 'Томати чері, моцарела, песто',
        'description': 'Легший варіант: половинки чері, кульки моцарели й ложка песто. '
                       'Смак свіжіший і трохи травʼянистий.',
        'ingredients': 'Тісто, томатний соус, томати чері, моцарела, песто, базилік',
    },
    {
        'slug': 'set-philadelphia', 'category': 'Суші', 'name': 'Сет «Філадельфія»',
        'weight': '640 г / 16 шт', 'price': '449', 'old_price': '499', 'stock': 9,
        'is_featured': True,
        'short': '16 шматків: лосось, вугор, креветка',
        'description': 'Найпопулярніший сет на двох: класична філадельфія з лососем, рол із '
                       'вугром і креветка темпура. Подаємо із соєвим соусом, імбиром і васабі.',
        'ingredients': 'Рис, норі, лосось, вугор, креветка, вершковий сир, огірок, авокадо',
    },
    {
        'slug': 'set-tokyo', 'category': 'Суші', 'name': 'Сет «Токіо»',
        'weight': '900 г / 24 шт', 'price': '649', 'stock': 6, 'is_featured': False,
        'short': '24 шматки, чотири види ролів',
        'description': 'Великий сет на компанію: філадельфія, каліфорнія, рол із тунцем і '
                       'запечений рол. Крутимо після замовлення, не заздалегідь.',
        'ingredients': 'Рис, норі, лосось, тунець, креветка, краб, вершковий сир, авокадо, огірок',
    },
    {
        'slug': 'roll-spicy-salmon', 'category': 'Суші', 'name': 'Рол «Спайсі лосось»',
        'weight': '280 г / 8 шт', 'price': '219', 'stock': 16, 'is_featured': False,
        'short': 'Гострий соус, лосось, кунжут',
        'description': 'Лосось під соусом спайсі й кунжутом. Гострота середня — її добре '
                       'врівноважує вершковий сир.',
        'ingredients': 'Рис, норі, лосось, вершковий сир, соус спайсі, кунжут',
    },
    {
        'slug': 'roll-shrimp-tempura', 'category': 'Суші', 'name': 'Рол «Креветка темпура»',
        'weight': '300 г / 8 шт', 'price': '239', 'stock': 10, 'is_featured': False,
        'short': 'Гарячий рол у клярі',
        'description': 'Креветка в клярі темпура, сир і соус унагі. Подаємо гарячим — '
                       'найкраще зʼїсти одразу, поки кляр хрустить.',
        'ingredients': 'Рис, норі, креветка, кляр темпура, вершковий сир, соус унагі, кунжут',
    },
    {
        'slug': 'cheeseburger', 'category': 'Бургери', 'name': 'Чізбургер',
        'weight': '320 г', 'price': '185', 'stock': 22, 'is_featured': True,
        'short': 'Яловичина 150 г, чедер, солоні огірки',
        'description': 'Котлета з яловичини на грилі, чедер, солоні огірки, цибуля й соус. '
                       'Булочка бріош підсмажена на вершковому маслі.',
        'ingredients': 'Булочка бріош, яловичина, чедер, солоні огірки, цибуля, соус, салат',
    },
    {
        'slug': 'bacon-burger', 'category': 'Бургери', 'name': 'Бургер з беконом',
        'weight': '350 г', 'price': '205', 'stock': 15, 'is_featured': False,
        'short': 'Бекон, чеддер, карамелізована цибуля',
        'description': 'Копчений бекон, чеддер і карамелізована цибуля — солодко-солоний смак. '
                       'Подаємо з картоплею фрі.',
        'ingredients': 'Булочка бріош, яловичина, бекон, чеддер, карамелізована цибуля, соус',
    },
    {
        'slug': 'double-burger', 'category': 'Бургери', 'name': 'Дабл бургер',
        'weight': '420 г', 'price': '245', 'old_price': '265', 'stock': 8, 'is_featured': False,
        'short': 'Дві котлети, подвійний сир',
        'description': 'Для серйозного голоду: дві котлети по 100 г, два слайси чеддера й соус '
                       'барбекю. Їсти зручніше руками, серветки додаємо.',
        'ingredients': 'Булочка бріош, яловичина (2×100 г), чеддер, бекон, соус барбекю, цибуля',
    },
    {
        'slug': 'caesar-chicken', 'category': 'Салати', 'name': 'Цезар з куркою',
        'weight': '260 г', 'price': '175', 'stock': 20, 'is_featured': True,
        'short': 'Курка на грилі, пармезан, грінки',
        'description': 'Романо, курка на грилі, пелюстки пармезану й грінки з білого хліба. '
                       'Соус робимо самі — без майонезу з пакета.',
        'ingredients': 'Салат романо, курка, пармезан, грінки, соус цезар, томати чері',
    },
    {
        'slug': 'greek-salad', 'category': 'Салати', 'name': 'Грецький салат',
        'weight': '240 г', 'price': '155', 'stock': 18, 'is_featured': False,
        'short': 'Фета, оливки каламата, огірок',
        'description': 'Овочі, фета й оливки каламата з оливковою олією та орегано. '
                       'Без майонезу — легкий варіант до піци.',
        'ingredients': 'Огірок, томати, перець, червона цибуля, фета, оливки каламата, олія, орегано',
    },
    {
        'slug': 'salad-croutons', 'category': 'Салати', 'name': 'Салат з хрусткими грінками',
        'weight': '220 г', 'price': '149', 'stock': 17, 'is_featured': False,
        'short': 'Мікс салату, пармезан, гарячі грінки',
        'description': 'Свіжий мікс, пармезан і гарячі грінки. Простий салат, який добре йде '
                       'з пастою або супом.',
        'ingredients': 'Мікс салату, пармезан, грінки, соус, томати чері',
    },
    {
        'slug': 'borscht', 'category': 'Гаряче та перше', 'name': 'Борщ український',
        'weight': '350 г', 'price': '135', 'stock': 25, 'is_featured': True,
        'short': 'З квасолею, сметаною та пампушкою',
        'description': 'Варимо на яловичому бульйоні з квасолею, буряком і капустою. '
                       'Подаємо зі сметаною, зеленню та часниковою пампушкою.',
        'ingredients': 'Бульйон яловичий, буряк, капуста, картопля, квасоля, морква, цибуля, '
                       'томатна паста, сметана',
    },
    {
        'slug': 'mushroom-cream-soup', 'category': 'Гаряче та перше', 'name': 'Крем-суп з печериць',
        'weight': '300 г', 'price': '145', 'stock': 14, 'is_featured': False,
        'short': 'Вершковий, з трюфельною олією',
        'description': 'Печериці, обсмажені з цибулею, вершки й крапля трюфельної олії. '
                       'Подаємо з грінками й насінням.',
        'ingredients': 'Печериці, цибуля, вершки, картопля, трюфельна олія, грінки',
    },
    {
        'slug': 'pasta-carbonara', 'category': 'Гаряче та перше', 'name': 'Паста карбонара',
        'weight': '320 г', 'price': '189', 'stock': 13, 'is_featured': False,
        'short': 'Гуанчале, жовток, пекорино',
        'description': 'Спагеті аль денте, гуанчале, жовтки й пекорино романо. Без вершків — '
                       'соус тримається на яйці й сирі, як у Римі.',
        'ingredients': 'Спагеті, гуанчале, жовтки, пекорино романо, чорний перець',
    },
    {
        'slug': 'cheesecake-new-york', 'category': 'Десерти', 'name': 'Чізкейк «Нью-Йорк»',
        'weight': '140 г', 'price': '115', 'stock': 12, 'is_featured': False,
        'short': 'Класичний, на пісочній основі',
        'description': 'Щільний вершковий сир на пісочній основі, зверху — ягідний соус. '
                       'Тримаємо в холодильнику, подаємо холодним.',
        'ingredients': 'Вершковий сир, вершки, яйця, цукор, пісочна основа, ягідний соус',
    },
    {
        'slug': 'cheesecake-vanilla', 'category': 'Десерти', 'name': 'Чізкейк ванільний',
        'weight': '130 г', 'price': '125', 'stock': 0, 'is_featured': False,
        'short': 'Ніжний, з ваніллю бурбон',
        'description': 'Легший за «Нью-Йорк»: більше вершків і ваніль бурбон. Добре йде '
                       'з капучино. Сьогодні, на жаль, закінчився — буде завтра.',
        'ingredients': 'Вершковий сир, вершки, яйця, цукор, ваніль, пісочна основа',
    },
    {
        'slug': 'tiramisu', 'category': 'Десерти', 'name': 'Тірамісу',
        'weight': '150 г', 'price': '135', 'stock': 10, 'is_featured': True,
        'short': 'Савоярді, маскарпоне, еспресо',
        'description': 'Савоярді, змочені в еспресо, крем із маскарпоне й какао зверху. '
                       'Збираємо щодня, подаємо холодним.',
        'ingredients': 'Печиво савоярді, маскарпоне, яйця, цукор, еспресо, какао',
    },
    {
        'slug': 'lemonade-mint', 'category': 'Напої', 'name': 'Лимонад мʼятний',
        'weight': '0,5 л', 'price': '75', 'stock': 30, 'is_featured': False,
        'short': 'Лимон, мʼята, лід',
        'description': 'Свіжовичавлений лимон, мʼята й трохи цукру. Робимо щоранку, '
                       'без концентратів і барвників.',
        'ingredients': 'Вода, лимон, мʼята, цукор, лід',
    },
    {
        'slug': 'mojito', 'category': 'Напої', 'name': 'Мохіто безалкогольний',
        'weight': '0,4 л', 'price': '85', 'stock': 24, 'is_featured': False,
        'short': 'Лайм, мʼята, газована вода',
        'description': 'Безалкогольна версія: лайм, мʼята й газована вода. Добре освіжає '
                       'після гострої піци.',
        'ingredients': 'Вода газована, лайм, мʼята, цукор, лід',
    },
    {
        'slug': 'latte', 'category': 'Напої', 'name': 'Лате',
        'weight': '0,3 л', 'price': '65', 'stock': 40, 'is_featured': False,
        'short': 'Еспресо й молоко 1:3',
        'description': 'Подвійний еспресо й гаряче молоко з мʼякою пінкою. Зерно обсмажують '
                       'для нас у Харкові невеликими партіями.',
        'ingredients': 'Кава еспресо, молоко',
    },
    {
        'slug': 'cappuccino', 'category': 'Напої', 'name': 'Капучино',
        'weight': '0,25 л', 'price': '60', 'stock': 40, 'is_featured': False,
        'short': 'Еспресо й молоко 1:1, густа пінка',
        'description': 'Класична пропорція з густою пінкою. За бажанням додамо корицю.',
        'ingredients': 'Кава еспресо, молоко, кориця',
    },
]

class Command(BaseCommand):
    help = 'Завантажує меню (7 категорій, 24 страви) і копіює фото в media/'

    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true', help='Спочатку очистити меню')
        parser.add_argument('--photos', action='store_true', help='Перезалити фото страв')

    def handle(self, *args, **options):
        if options['reset']:
            Product.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write('  меню очищено')

        categories = {}
        for name, emoji, sort in CATEGORIES:
            cat, _ = Category.objects.update_or_create(
                name=name, defaults={'emoji': emoji, 'sort': sort}
            )
            categories[name] = cat

        created = updated = 0
        for item in MENU:
            data = {k: v for k, v in item.items() if k not in ('slug', 'category')}
            product, is_new = Product.objects.get_or_create(
                slug=item['slug'],
                defaults={'category': categories[item['category']], **data},
            )
            if not is_new:
                for field, value in data.items():
                    setattr(product, field, value)
                product.category = categories[item['category']]
                product.save()
                updated += 1
            else:
                created += 1

            photo = PHOTO_DIR / f"{item['slug']}.jpg"
            if photo.is_file() and (options['photos'] or not product.image):
                product.image.save(photo.name, ContentFile(photo.read_bytes()), save=True)

        self.stdout.write(self.style.SUCCESS(
            f'Меню готове: {len(categories)} категорій, '
            f'{created} нових страв, {updated} оновлено.'
        ))
