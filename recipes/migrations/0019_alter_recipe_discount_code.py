# Generated by Django 3.2.5 on 2021-08-16 09:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0018_recipe_discount_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='discount_code',
            field=models.CharField(blank=True, default=0, max_length=6),
        ),
    ]