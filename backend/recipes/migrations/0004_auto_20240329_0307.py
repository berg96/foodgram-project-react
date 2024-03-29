# Generated by Django 3.2.3 on 2024-03-29 01:07

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_auto_20240328_1326'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='shoppingcart',
            options={'default_related_name': '%(class)ss', 'ordering': ('user',), 'verbose_name': 'Рецепт в списке покупок', 'verbose_name_plural': 'Рецепты в списках покупок'},
        ),
        migrations.RemoveConstraint(
            model_name='favorite',
            name='unique_author_title',
        ),
        migrations.AlterField(
            model_name='shoppingcart',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shoppingcarts', to='recipes.recipe', verbose_name='Рецепт'),
        ),
        migrations.AlterField(
            model_name='shoppingcart',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shoppingcarts', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
        migrations.AddConstraint(
            model_name='favorite',
            constraint=models.UniqueConstraint(fields=('recipe', 'user'), name='unique_recipe_user_favorite'),
        ),
        migrations.AddConstraint(
            model_name='shoppingcart',
            constraint=models.UniqueConstraint(fields=('recipe', 'user'), name='unique_recipe_user_shoppingcart'),
        ),
    ]