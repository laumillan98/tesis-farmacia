import time
from celery import shared_task
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

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