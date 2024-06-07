# Generated by Django 5.0.2 on 2024-06-07 04:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assistant', '0004_rename_contactform_contactforms'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogsection',
            name='title',
            field=models.CharField(blank=True, max_length=2000, null=True),
        ),
        migrations.AlterField(
            model_name='history',
            name='prompt',
            field=models.CharField(blank=True, max_length=3000, null=True),
        ),
        migrations.AlterField(
            model_name='history',
            name='slug',
            field=models.SlugField(blank=True, max_length=1000, null=True, unique=True),
        ),
    ]