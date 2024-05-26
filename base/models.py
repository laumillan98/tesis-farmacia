from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models as gis_models
import uuid
# Create your models here.

class CustomUser(AbstractUser):
    description = models.TextField('Description', max_length=600, default='', blank=True) 

    def __str__(self):
        return self.username
    

class TipoFarmacia(models.Model):
    id_tipo_farmacia = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=20)

    def __str__(self):
        return self.nombre
    

class TurnoFarmacia(models.Model):
    id_turno_farmacia = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=20)

    def __str__(self):
        return self.nombre


class RestriccionMedicamento(models.Model):
    id_restriccion = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=20)

    def __str__(self):
        return self.nombre 


class ClasificacionMedicamento(models.Model):
    id_clasificacion = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=20)

    def __str__(self):
        return self.nombre    
    

class FormatoMedicamento(models.Model):
    id_formato = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=20)

    def __str__(self):
        return self.nombre    
   

class Provincia(models.Model):
    id_prov = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=20)

    def __str__(self):
        return self.nombre


class Municipio(models.Model):
    id_munic = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=25, unique=True)
    id_prov = models.ForeignKey(Provincia, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre


class Medicamento(models.Model):
    id_medic = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)
    cant_max = models.IntegerField(default=0)
    precio_unidad = models.FloatField(default=0)
    origen_natural = models.BooleanField(default=False)
    id_restriccion = models.ForeignKey(RestriccionMedicamento, on_delete=models.RESTRICT, null=True, blank=True, to_field='id_restriccion')
    id_clasificacion = models.ForeignKey(ClasificacionMedicamento, on_delete=models.RESTRICT, null=True, blank=True, to_field='id_clasificacion')
    id_formato = models.ForeignKey(FormatoMedicamento, on_delete=models.RESTRICT, null=True, blank=True, to_field='id_formato')
    
    def __str__(self):
        return self.nombre      


class Farmacia(models.Model):
    id_farma = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    telefono = models.IntegerField(null=True, blank=True) 
    id_turno = models.ForeignKey(TurnoFarmacia, on_delete=models.RESTRICT, null=True)
    id_tipo = models.ForeignKey(TipoFarmacia, on_delete=models.RESTRICT)
    id_munic = models.ForeignKey(Municipio, on_delete=models.RESTRICT)
    ubicacion = gis_models.PointField(geography=True, blank=True, null=True)

    def __str__(self):
        return self.nombre
    

class FarmaUser(CustomUser):
    id_farma = models.ForeignKey(Farmacia, on_delete=models.RESTRICT, null=True, blank=True, to_field='id_farma')

    def __str__(self):
        return self.username 

    class Meta:
        verbose_name = 'Farmaceutico'


class FarmaciaMedicamento(models.Model):
    id_medic = models.ForeignKey(Medicamento, on_delete=models.RESTRICT, null=True, blank=True, to_field='id_medic')
    id_farma = models.ForeignKey(Farmacia, on_delete=models.RESTRICT, null=True, blank=True, to_field='id_farma')
    existencia = models.IntegerField(default=0)

    def __str__(self):
        return self.id_medic.nombre + ' ' + self.id_farma.nombre + str(self.existencia)