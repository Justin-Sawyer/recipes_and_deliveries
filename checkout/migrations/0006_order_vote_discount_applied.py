# Generated by Django 3.2.5 on 2021-08-17 13:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0005_order_user_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='vote_discount_applied',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
