# Generated by Django 3.2.5 on 2021-08-14 10:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0014_recipe_recipe_box'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='vote_count',
        ),
    ]