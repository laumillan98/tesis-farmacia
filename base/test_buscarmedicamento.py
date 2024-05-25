from django.test import TestCase, Client
from django.urls import reverse
from .models import Farmacia, CustomUser, Medicamento, FarmaciaMedicamento, Provincia, Municipio, TipoFarmacia, TurnoFarmacia

class SimpleTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.provincia = Provincia.objects.create(nombre='Provincia Test')
        self.municipio = Municipio.objects.create(nombre='Municipio Test', id_prov=self.provincia)
        self.tipo_farmacia = TipoFarmacia.objects.create(nombre='Tipo Test')
        self.turno_farmacia = TurnoFarmacia.objects.create(nombre='Turno Test')
        self.farmacia = Farmacia.objects.create(
            nombre='Farmacia Test', 
            direccion='Dirección Test', 
            telefono=123456789, 
            id_turno=self.turno_farmacia, 
            id_tipo=self.tipo_farmacia, 
            id_munic=self.municipio
        )
        self.user = CustomUser.objects.create_user(username='testuser', password='12345')
        self.medicamento = Medicamento.objects.create(nombre='Medicamento Test', precio_unidad=10.0)
        self.farmacia_medicamento = FarmaciaMedicamento.objects.create(id_farma=self.farmacia, id_medic=self.medicamento, existencia=15)

    def test_farmacia_exists(self):
        farmacia = Farmacia.objects.get(nombre='Farmacia Test')
        self.assertEqual(farmacia.direccion, 'Dirección Test')

    def test_medicamento_exists(self):
        medicamento = Medicamento.objects.get(nombre='Medicamento Test')
        self.assertEqual(medicamento.precio_unidad, 10.0)

    def test_get_farmacias_with_medicamento(self):
        response = self.client.get(reverse('buscar_medicamento'), {'nombre_medicamento': 'Medicamento Test'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Farmacia Test')

    def test_404_page(self):
        response = self.client.get('/una-url-que-no-existe/')
        self.assertEqual(response.status_code, 404)
