# Generated by Django 5.0.7 on 2024-08-13 12:06

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('shop', '0003_translations'),
    ]

    operations = [
        migrations.AlterField(
            model_name='producttranslation',
            name='slug',
            field=models.SlugField(max_length=200),
        ),
    ]
