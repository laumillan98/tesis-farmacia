# Generated by Django 5.0.3 on 2024-06-02 20:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0019_rename_medicamento_tareaexistencia_id_medic_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clasificacionmedicamento',
            name='nombre',
            field=models.CharField(max_length=20, unique=True),
        ),
        migrations.AlterField(
            model_name='farmacia',
            name='nombre',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='formatomedicamento',
            name='nombre',
            field=models.CharField(max_length=20, unique=True),
        ),
        migrations.AlterField(
            model_name='provincia',
            name='nombre',
            field=models.CharField(max_length=20, unique=True),
        ),
        migrations.AlterField(
            model_name='restriccionmedicamento',
            name='nombre',
            field=models.CharField(max_length=20, unique=True),
        ),
        migrations.AlterField(
            model_name='tipofarmacia',
            name='nombre',
            field=models.CharField(max_length=20, unique=True),
        ),
        migrations.AlterField(
            model_name='turnofarmacia',
            name='nombre',
            field=models.CharField(max_length=20, unique=True),
        ),
    ]
