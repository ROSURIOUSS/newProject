import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_order_user'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.PositiveSmallIntegerField(choices=[(1, '1 ★'), (2, '2 ★'), (3, '3 ★'), (4, '4 ★'), (5, '5 ★')], default=5, verbose_name='Оцінка')),
                ('text', models.TextField(verbose_name='Відгук')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Створено')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Оновлено')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='store.product', verbose_name='Страва')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to=settings.AUTH_USER_MODEL, verbose_name='Клієнт')),
            ],
            options={
                'verbose_name': 'Відгук',
                'verbose_name_plural': 'Відгуки',
                'ordering': ['-created_at'],
                'constraints': [models.UniqueConstraint(fields=('product', 'user'), name='one_review_per_client')],
            },
        ),
    ]
