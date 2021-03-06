# Generated by Django 3.2.5 on 2021-08-04 15:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_alter_recipe_total_time'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=254)),
                ('friendly_name', models.CharField(blank=True, default='', max_length=254)),
                ('sku', models.CharField(blank=True, default='', max_length=254)),
            ],
            options={
                'verbose_name_plural': 'Categories',
                'ordering': ('sku',),
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tagname', models.CharField(max_length=254)),
            ],
            options={
                'verbose_name_plural': 'Tags',
                'ordering': ('tagname',),
            },
        ),
        migrations.AddField(
            model_name='recipe',
            name='category',
            field=models.ManyToManyField(blank=True, to='recipes.Category'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='tag',
            field=models.ManyToManyField(blank=True, to='recipes.Tag'),
        ),
    ]
