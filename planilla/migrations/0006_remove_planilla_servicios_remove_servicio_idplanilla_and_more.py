# Generated by Django 5.1.2 on 2024-10-21 17:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planilla', '0005_planilla_guardia_operativa_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='planilla',
            name='servicios',
        ),
        migrations.RemoveField(
            model_name='servicio',
            name='IDPlanilla',
        ),
        migrations.AlterField(
            model_name='servicio',
            name='numero',
            field=models.IntegerField(blank=True, null=True, unique=True, verbose_name='Número'),
        ),
    ]
