import time
from celery import shared_task
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from celery.utils.log import get_task_logger

from base.models import FarmaciaMedicamento, TareaExistencia

logger = get_task_logger(__name__)

@shared_task
def send_activation_email(domain, username, tok, email, protocol):
    mail_subject = "Activar cuenta de usuario."
    message = render_to_string("activar_cuenta.html", {
        'user': username,
        'domain': domain,
        'uid': urlsafe_base64_encode(force_bytes(username)), 
        'token': tok,
        'protocol': protocol
    })
    email_message = EmailMessage(mail_subject, message, to=[email])
    result = email_message.send()
    if result:
        print(f"Email sent successfully to {email}")
    else:
        print(f"Failed to send email to {email}")

@shared_task
def check_stock_for_pills():
   notificar_existencias()
   print("Tarea programada")
   logger.info("tarea programada")

def notificar_existencias():
    print("notificar_existencias")
    tareas = TareaExistencia.objects.all()
    farma_medicamentos = FarmaciaMedicamento.objects.all()
    for tarea in tareas:
        filtered = farma_medicamentos.filter(id_medic=tarea.medicamento, existencia__gt=0)
        result = []
        for item in filtered:
            print(f'{tarea.medicamento.nombre} - {item.existencia} - {item.id_farma.nombre}')
            result.append({
                'medicamento': tarea.medicamento.nombre,
                'existencias': 'Altas' if item.existencia > 10 else 'Bajas',
                'farmacia': item.id_farma.nombre,
            })
            # el listado result tiene todas las farmacias donde existe ese medicamento con existencia, 
        if len(result) > 0:
            print(result)
            print(result[0]['medicamento'])
            mail_subject = "Restauracion de existencia de "+ result[0]['medicamento']
            message = render_to_string("existencia_medicamento.html", {
                'user': tarea.user.username,
                'result': result
            })
            email_message = EmailMessage(mail_subject, message, to=[tarea.user.email])
            try:
                email_message.send()
                tarea.delete()
            except Exception as e:
                print(e)
            
            
       