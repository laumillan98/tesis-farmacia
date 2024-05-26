# Generated by Django 5.0.4 on 2024-05-20 00:13

import django.contrib.auth.models
import django.contrib.auth.validators
import django.contrib.gis.db.models.fields
import django.db.models.deletion
import django.utils.timezone
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('description', models.TextField(blank=True, default='', max_length=600, verbose_name='Description')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='ClasificacionMedicamento',
            fields=[
                ('id_clasificacion', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Farmacia',
            fields=[
                ('id_farma', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=100)),
                ('direccion', models.CharField(max_length=200)),
                ('telefono', models.IntegerField(blank=True, null=True)),
                ('ubicacion', django.contrib.gis.db.models.fields.PointField(blank=True, geography=True, null=True, srid=4326)),
            ],
        ),
        migrations.CreateModel(
            name='Municipio',
            fields=[
                ('id_munic', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=25, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Provincia',
            fields=[
                ('id_prov', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='RestriccionMedicamento',
            fields=[
                ('id_restriccion', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='TipoFarmacia',
            fields=[
                ('id_tipo_farmacia', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='TurnoFarmacia',
            fields=[
                ('id_turno_farmacia', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Medicamento',
            fields=[
                ('id_medic', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=50, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('cant_max', models.IntegerField(default=0)),
                ('precio_unidad', models.FloatField(default=0)),
                ('origen_natural', models.BooleanField(default=False)),
                ('id_clasificacion', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='base.clasificacionmedicamento')),
                ('id_restriccion', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='base.restriccionmedicamento')),
            ],
        ),
        migrations.CreateModel(
            name='FarmaciaMedicamento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('existencia', models.IntegerField(default=0)),
                ('id_farma', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='base.farmacia')),
                ('id_medic', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='base.medicamento')),
            ],
        ),
        migrations.AddField(
            model_name='farmacia',
            name='id_munic',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='base.municipio'),
        ),
        migrations.AddField(
            model_name='municipio',
            name='id_prov',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.provincia'),
        ),
        migrations.AddField(
            model_name='farmacia',
            name='id_tipo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='base.tipofarmacia'),
        ),
        migrations.AddField(
            model_name='farmacia',
            name='id_turno',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, to='base.turnofarmacia'),
        ),
        migrations.CreateModel(
            name='FarmaUser',
            fields=[
                ('customuser_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('id_farma', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='base.farmacia')),
            ],
            options={
                'verbose_name': 'Farmaceutico',
            },
            bases=('base.customuser',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
