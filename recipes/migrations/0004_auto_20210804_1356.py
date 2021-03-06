# Generated by Django 3.2.5 on 2021-08-04 13:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0003_alter_ingredient_preparation'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='author',
            field=models.ForeignKey(blank=True, default='', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='recipe_posts', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='recipe',
            name='date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='recipe',
            name='date_edited',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='recipe',
            name='date_posted',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, null=True),
        ),
        migrations.AddField(
            model_name='recipe',
            name='directions',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='recipe',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
        migrations.AddField(
            model_name='recipe',
            name='image_credit',
            field=models.CharField(blank=True, default='', max_length=254),
        ),
        migrations.AddField(
            model_name='recipe',
            name='total_time',
            field=models.CharField(default=2, max_length=20),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='recipe',
            name='cook_time',
            field=models.CharField(blank=True, default='', max_length=20),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='prep_time',
            field=models.CharField(max_length=20),
        ),
    ]
