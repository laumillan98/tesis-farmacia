# Generated by Django 5.0.4 on 2024-05-12 02:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='farmaciamedicamento',
            name='id_farmacia',
        ),
    ]
