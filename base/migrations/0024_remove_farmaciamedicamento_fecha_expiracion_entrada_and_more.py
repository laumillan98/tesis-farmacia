# Generated by Django 5.0.3 on 2024-06-05 00:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0023_alter_farmacia_telefono'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='farmaciamedicamento',
            name='fecha_expiracion',
        ),
        migrations.CreateModel(
            name='Entrada',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('factura', models.CharField(max_length=100)),
                ('numero_lote', models.CharField(max_length=100)),
                ('cantidad', models.IntegerField()),
                ('fecha_elaboracion', models.DateField()),
                ('fecha_vencimiento', models.DateField()),
                ('id_farmaciaMedicamento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.farmaciamedicamento')),
            ],
        ),
        migrations.CreateModel(
            name='Salida',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.IntegerField()),
                ('fecha_movimiento', models.DateField(auto_now_add=True)),
                ('id_farmaciaMedicamento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.farmaciamedicamento')),
            ],
        ),
    ]
