# Generated by Django 5.0.3 on 2024-05-26 07:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0012_formatomedicamento_medicamento_id_formato'),
    ]

    operations = [
        migrations.AlterField(
            model_name='medicamento',
            name='nombre',
            field=models.CharField(max_length=50),
        ),
    ]
