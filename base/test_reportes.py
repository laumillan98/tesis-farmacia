from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User, Group
from .models import CustomUser, Farmacia, FarmaUser, TipoFarmacia, Municipio, Provincia, TurnoFarmacia
from django.contrib.admin.models import LogEntry
from .views import generar_reporte_pdf
from datetime import datetime
import io
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4, landscape
from io import BytesIO
from reportlab.lib.pagesizes import letter
from django.views.decorators.csrf import csrf_exempt
from .pdf_utils import header_footer
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType


class GenerarReportePDFTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='testuser', password='12345')
        self.custom_user1 = CustomUser.objects.create(
            username='user1', first_name='Test', last_name='User', email='user1@example.com',
            date_joined=datetime(2023, 1, 1), is_active=True
        )
        self.custom_user2 = CustomUser.objects.create(
            username='user2', first_name='Test2', last_name='User2', email='user2@example.com',
            date_joined=datetime(2023, 2, 1), is_active=False
        )
        group = Group.objects.create(name='admin')
        self.custom_user1.groups.add(group)

        # Crear algunos objetos Farmacia para las pruebas
        self.provincia = Provincia.objects.create(nombre='TestProvincia')
        self.municipio = Municipio.objects.create(nombre='TestMunicipio', id_prov=self.provincia)
        self.tipo_farmacia = TipoFarmacia.objects.create(nombre='TestTipo')
        self.turno_farmacia = TurnoFarmacia.objects.create(nombre='TestTurno')
        self.farmacia1 = Farmacia.objects.create(
            nombre='Farmacia1', id_munic=self.municipio, direccion='Calle 123', telefono='123456789',
            id_tipo=self.tipo_farmacia, id_turno=self.turno_farmacia
        )
        self.farma_user = FarmaUser.objects.create(username='farmauser1', id_farma=self.farmacia1)

        # Obtener ContentType para CustomUser
        custom_user_content_type = ContentType.objects.get_for_model(CustomUser)
        # Crear algunos LogEntry para las pruebas
        self.log_entry1 = LogEntry.objects.create(
            user=self.user,
            action_time=datetime(2023, 1, 1, 10, 0),
            content_type=custom_user_content_type,
            object_id=self.custom_user1.id,
            object_repr=str(self.custom_user1),
            action_flag=1
        )

    def test_generar_reporte_pdf_custom_user(self):
        factory = RequestFactory()
        request = factory.post('/generar_reporte_pdf/', {
            'tipo_objeto': 'usuario',
            'username': 'user1',
            'fecha_inicio': '2023-01-01',
            'fecha_fin': '2023-12-31',
            'rol': 'admin',
            'activo': 'True'
        })
        request.user = self.user
        response = generar_reporte_pdf(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_generar_reporte_pdf_farmacia(self):
        factory = RequestFactory()
        request = factory.post('/generar_reporte_pdf/', {
            'tipo_objeto': 'farmacia',
            'nombre': 'Farmacia1',
            'provincia': 'TestProvincia',
            'municipio': 'TestMunicipio',
            'tipo': 'TestTipo',
            'turno': 'TestTurno'
        })
        request.user = self.user
        response = generar_reporte_pdf(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_generar_reporte_pdf_traza(self):
        factory = RequestFactory()
        request = factory.post('/generar_reporte_pdf/', {
            'tipo_objeto': 'traza',
            'usuario': 'testuser',
            'fecha_inicio': '2023-01-01',
            'fecha_fin': '2023-12-31',
            'tipo_accion': '1',
            'contenido': 'user1'
        })
        request.user = self.user
        response = generar_reporte_pdf(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_generar_reporte_pdf_tipo_objeto_no_valido(self):
        factory = RequestFactory()
        request = factory.post('/generar_reporte_pdf/', {
            'tipo_objeto': 'no_valido'
        })
        request.user = self.user
        response = generar_reporte_pdf(request)
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'error': 'Tipo de objeto no válido'})

    def test_generar_reporte_pdf_sin_datos(self):
        factory = RequestFactory()
        request = factory.post('/generar_reporte_pdf/', {
            'tipo_objeto': 'usuario',
            'username': 'no_existe'
        })
        request.user = self.user
        response = generar_reporte_pdf(request)
        self.assertEqual(response.status_code, 404)
        self.assertJSONEqual(response.content, {'error': 'No se encontraron datos para generar el reporte.'})

    def test_metodo_no_permitido(self):
        factory = RequestFactory()
        request = factory.get('/generar_reporte_pdf/')
        request.user = self.user
        response = generar_reporte_pdf(request)
        self.assertEqual(response.status_code, 405)
        self.assertJSONEqual(response.content, {'error': 'Método no permitido'})