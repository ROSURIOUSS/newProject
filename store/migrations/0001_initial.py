
import django.db.models.deletion
from django.db import migrations, models

class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Назва')),
                ('slug', models.SlugField(blank=True, max_length=120, unique=True)),
                ('emoji', models.CharField(blank=True, help_text='Один емодзі, напр. 🍕', max_length=8, verbose_name='Іконка')),
                ('sort', models.PositiveIntegerField(default=0, help_text='Менше число — вище в списку', verbose_name='Порядок')),
            ],
            options={
                'verbose_name': 'Категорія',
                'verbose_name_plural': 'Категорії',
                'ordering': ['sort', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120, verbose_name='Імʼя')),
                ('phone', models.CharField(max_length=30, verbose_name='Телефон')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='Email')),
                ('delivery', models.CharField(choices=[('delivery', 'Доставка курʼєром'), ('pickup', 'Самовивіз')], default='delivery', max_length=20, verbose_name='Спосіб отримання')),
                ('address', models.CharField(blank=True, help_text='Вулиця, будинок, квартира, підʼїзд', max_length=250, verbose_name='Адреса')),
                ('time_slot', models.CharField(choices=[('asap', 'Якнайшвидше (40–60 хв)'), ('hour', 'Протягом години'), ('later', 'На пізніший час')], default='asap', max_length=20, verbose_name='Час')),
                ('payment', models.CharField(choices=[('cash', 'Готівкою курʼєру'), ('card', 'Карткою курʼєру'), ('online', 'Онлайн-оплата')], default='cash', max_length=20, verbose_name='Оплата')),
                ('comment', models.TextField(blank=True, verbose_name='Коментар')),
                ('status', models.CharField(choices=[('new', 'Нове'), ('cooking', 'Готується'), ('delivering', 'Везе курʼєр'), ('done', 'Виконано'), ('cancelled', 'Скасовано')], default='new', max_length=20, verbose_name='Статус')),
                ('total', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Сума, ₴')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Створено')),
            ],
            options={
                'verbose_name': 'Замовлення',
                'verbose_name_plural': 'Замовлення',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Назва')),
                ('slug', models.SlugField(blank=True, max_length=220, unique=True)),
                ('short', models.CharField(blank=True, help_text='Показується на картці, 1 рядок', max_length=160, verbose_name='Короткий опис')),
                ('description', models.TextField(verbose_name='Опис')),
                ('ingredients', models.TextField(blank=True, help_text='Через кому: тісто, томати, моцарела', verbose_name='Склад')),
                ('weight', models.CharField(blank=True, help_text='Напр. 550 г або 0,5 л', max_length=40, verbose_name='Вага / обʼєм')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Ціна, ₴')),
                ('old_price', models.DecimalField(blank=True, decimal_places=2, help_text='Заповніть, якщо є знижка', max_digits=10, null=True, verbose_name='Стара ціна, ₴')),
                ('stock', models.PositiveIntegerField(default=0, help_text='0 — показати «Немає» і вимкнути кнопку', verbose_name='Порцій на кухні')),
                ('image', models.FileField(blank=True, upload_to='products/', verbose_name='Фото')),
                ('is_featured', models.BooleanField(default=False, verbose_name='Хіт меню')),
                ('is_active', models.BooleanField(default=True, verbose_name='Показувати в меню')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Додано')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='products', to='store.category', verbose_name='Категорія')),
            ],
            options={
                'verbose_name': 'Страва',
                'verbose_name_plural': 'Меню',
                'ordering': ['-is_featured', '-created_at'],
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Назва')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Ціна, ₴')),
                ('qty', models.PositiveIntegerField(default=1, verbose_name='Кількість')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='store.order', verbose_name='Замовлення')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='store.product', verbose_name='Страва')),
            ],
            options={
                'verbose_name': 'Позиція замовлення',
                'verbose_name_plural': 'Позиції замовлення',
            },
        ),
    ]
