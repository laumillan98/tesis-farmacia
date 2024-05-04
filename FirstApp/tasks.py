import time
from celery import shared_task
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from base.tokens import account_activation_token

@shared_task
def send_email_task(subject, message, from_email, recipient_list):
    send_mail(subject, message, from_email, recipient_list)

@shared_task
def add_and_print_numbers_with_delay(a, b):
    print("Entro")
    time.sleep(10)  # Simula un procesamiento largo con una demora de 10 segundos
    result = a + b
    print(f"The sum of {a} and {b} is {result}")
    return result

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