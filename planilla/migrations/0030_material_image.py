# Generated by Django 5.1.2 on 2025-01-21 11:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planilla', '0029_alter_material_nombre'),
    ]

    operations = [
        migrations.AddField(
            model_name='material',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='media/planilla/images/'),
        ),
    ]
