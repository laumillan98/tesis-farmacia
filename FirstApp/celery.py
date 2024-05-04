from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Establecer el módulo de configuración predeterminado de Django para el programa 'celery'.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FirstApp.settings')

app = Celery('FirstApp')

# Usar una cadena aquí significa que el trabajador no necesita serializar
# el objeto de configuración a los procesos secundarios.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Cargar módulos de tareas de todas las configuraciones de aplicaciones registradas en Django.
app.autodiscover_tasks()