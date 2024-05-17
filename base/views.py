from os import name
from typing import Protocol
import io
from io import StringIO
import subprocess
import json
from django.http import HttpResponse
from datetime import datetime, timedelta
from django.db.models import Count
from django.db.models.query_utils import Q
from django.http.response import FileResponse
from django.http.response import JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.core.paginator import Paginator, EmptyPage
from django.core.management import call_command
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.contrib.admin.models import LogEntry
from django.contrib.sites.shortcuts import get_current_site
from django.views.decorators.http import require_POST
from django.views.decorators.cache import cache_control
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

from .models import CustomUser, Medicamento, Farmacia, FarmaUser, FarmaciaMedicamento, TipoFarmacia, TurnoFarmacia, Municipio, Provincia, RestriccionMedicamento, ClasificacionMedicamento
from .forms import CustomUserCreationForm, FarmaUserCreationForm, UserLoginForm, SetPasswordForm, PasswordResetForm, UserProfileForm, UserUpdateForm, FarmaUserUpdateForm, FarmaUpdateForm, TipoFarmaciaUpdateForm, TurnoFarmaciaUpdateForm, MunicUpdateForm, ProvUpdateForm, MedicUpdateForm, RestriccionMedicamentoUpdateForm, ClasificacionMedicamentoUpdateForm
from .decorators import usuarios_permitidos, unauthenticated_user
from .tokens import account_activation_token
from FirstApp.tasks import send_activation_email
from django_tables2 import RequestConfig

# Librería ReportLab
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4, landscape
from io import BytesIO
from reportlab.lib.pagesizes import letter
from django.views.decorators.csrf import csrf_exempt


# Create your views here.

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def inicio(request):
    return render(request, "Inicio.html")


@login_required(login_url='/acceder')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def administrator(request):
    return render(request, "index.html")


@login_required(login_url='/acceder')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def farmaceutico(request):
    return render(request, "index_farmaceutico.html")


def backup_database(request):
    try:
        now = datetime.now()
        date_time = now.strftime("%Y-%m-%d %H:%M:%S")  #Formatear la fecha y hora
        call_command('dbbackup')
        with open('backup_log.txt', 'a') as f:
            f.write(f"Backup realizado el {date_time}\n")
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


def restore_database(request):
    try:
        now = datetime.now()
        date_time = now.strftime("%Y-%m-%d %H:%M:%S")  #Formatear la fecha y hora
        input_stream = StringIO('yes/n')
        process = subprocess.Popen(['python', 'manage.py', 'dbrestore'], stdin=subprocess.PIPE)
        process.communicate(input=input_stream.getvalue().encode())
        with open('restore_log.txt', 'a') as f:
            f.write(f"Restauración realizada el {date_time}\n")
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def salir(request):
    logout(request)
    messages.success(request, f"Su sesión se ha cerrado correctamente")
    return redirect('/acceder')


@unauthenticated_user
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def autenticar(request):
    if request.method == "POST":
        form = UserLoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            if user is not None:
                login(request, user)
                messages.success(request, f"Hola <b>{user.username}</b>! Usted se ha autenticado satisfactoriamente.")
                usuario = request.user
                grupo_admin = Group.objects.get(name='admin')
                grupo_clientes = Group.objects.get(name='clientes')
                if grupo_admin in usuario.groups.all():
                    return redirect('/gestionar_usuarios')
                elif grupo_clientes in usuario.groups.all():
                    return redirect('/')
                else:
                    return redirect('/gestionar_medicfarma')  
                     
       # else:
        #    for key, error in list(form.errors.items()):
        #        if key == 'captcha' and error[0] == 'This field is required.':
        #            messages.error(request, "You must pass the reCAPTCHA test")
        #            continue

         #       messages.error(request, error) 

    form = UserLoginForm()

    return render(
        request=request,
        template_name="acceder.html",
        context={"form": form}
        )
    

def activate(request, username, token):
    User = get_user_model()
    try:
        usernameDecode = force_str(urlsafe_base64_decode(username))
        user = User.objects.get(username=usernameDecode)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, "Gracias por confirmar su email. Ahora puede acceder.")
        return redirect('/acceder')
    else:
        messages.error(request, "Activación del link no válida!")

    return redirect('/acceder')


def activateEmail(request, user, to_email):
    send_activation_email.delay(
        domain=get_current_site(request).domain,
        username=user.username,
        tok=account_activation_token.make_token(user=user),
        email=to_email,
        protocol='https' if request.is_secure() else 'http'
    )


@unauthenticated_user
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def registrar(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(data=request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            group = Group.objects.get(name='clientes')
            user.groups.add(group)
            to_email = form.cleaned_data.get('email')
            activateEmail(request, user, to_email)
            messages.success(request, f'<b>{user.first_name}</b>, por favor diríjase a su correo <b>{to_email}</b> y haga click en \
                             el link de activación recibido para confirmar su registro. <b>Nota:</b> Chequee su carpeta Spam.')
            return redirect('/')

        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    else:
        form = CustomUserCreationForm()

    return render(
        request=request,
        template_name="registrar_usuario.html",
        context={"form": form}
        )


@login_required(login_url='/acceder')
def cambiarPass(request):
    user = request.user
    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Su contraseña ha sido cambiada")
            return redirect('/acceder')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    form = SetPasswordForm(user)
    return render(request, 'cambiar_pass.html', {'form': form})


@unauthenticated_user
def restablecerPass(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data['email']
            associated_user = get_user_model().objects.filter(Q(email=user_email)).first()
            if associated_user:
                subject = "Restablecer contraseña"
                message = render_to_string("restablecer_pass.html", {
                    'user': associated_user,
                    'domain': get_current_site(request).domain,
                    'uid': urlsafe_base64_encode(force_bytes(associated_user.pk)),
                    'token': account_activation_token.make_token(associated_user),
                    "protocol": 'https' if request.is_secure() else 'http'
                })
                email = EmailMessage(subject, message, to=[associated_user.email])
                if email.send():
                    messages.success(request,
                        """
                        <p>
                            Le hemos enviado por correo electrónico instrucciones para cambiar su contraseña, si existe una cuenta con el correo que ingresó. 
                            Debería recibirlo en breve.<br> Si no recibe un correo electrónico asegúrese de haber introducido la dirección con la que se registró y compruebe su carpeta Spam.
                        </p>
                        """
                    )
                else:
                    messages.error(request, "Problema al enviar el correo para restablecer su contraseña, <b>PROBLEMA EN SERVIDOR</b>")

            return redirect('/')
        

        for key, error in list(form.errors.items()):
            if key == 'captcha' and error[0] == 'This field is required.':
                messages.error(request, "You must pass the reCAPTCHA test")
                continue

    form = PasswordResetForm()
    return render(
        request=request, 
        template_name="solicitar_restablecer_pass.html", 
        context={"form": form}
        )


def confirmarRestablecerPass(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Su contraseña ha sido cambiada. Ahora puede acceder.")
                return redirect('/acceder')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)

        form = SetPasswordForm(user)
        return render(request, 'cambiar_pass.html', {'form': form})
    else:
        messages.error(request, "Link is expired")

    messages.error(request, 'Algo salió mal, redirigiendo al Inicio')
    return redirect("/")


@login_required(login_url='/acceder')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def perfilUsuario(request, username):
    show_alert = False
    if request.method == "POST":
        user = request.user
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            user_form = form.save()
            show_alert = True
            return redirect('/perfil_de_usuario/'+ user_form.username)
        
        for error in list (form.errors.values()):
            messages.error(request, error)

    user = get_user_model().objects.get(username=username)
    if user:
        form = UserProfileForm(instance=user)
        return render(
            request=request,
            template_name="perfil_de_usuario.html",
            context = {"form": form, "show_alert": show_alert}
        )
    
    return redirect('/')


@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['admin'])
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def gestionarUsuarios(request):
    return render(request, "gestionar_usuarios.html")


def listaDeUsuarios(request):
    users = CustomUser.objects.all()

    paginator = Paginator(users, request.GET.get('length', 10))  # Cantidad de objetos por página
    start = int(request.GET.get('start', 0))
    page_number = start // paginator.per_page + 1  # Calcular el número de página basado en 'start'
    page_obj = paginator.get_page(page_number)

    users_list = []
    for index,user in enumerate(page_obj.object_list):

        groups = user.groups.values_list('name', flat=True)  
        first_group = groups.first() if groups else None 
        user_date_joined = user.date_joined.strftime('%Y-%m-%d %H:%M:%S') if user.date_joined else None
        user_last_login = user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else None

        user_data = {
            'index': index + 1,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username,
            'email': user.email,
            'date_joined': user_date_joined,
            'last_login': user_last_login,
            'first_group': first_group,
            'is_active': user.is_active,
            'is_superuser': user.is_superuser,
            'id': user.pk,
        }
        users_list.append(user_data)

    data = {
        "draw": int(request.GET.get('draw', 0)),
        'recordsTotal': paginator.count,
        'recordsFiltered': paginator.count,
        'data': users_list
    }
    return JsonResponse(data, safe=False)


@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['admin'])
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def registrarFarmaceutico(request):
    if request.method == 'POST':
        form = FarmaUserCreationForm(data=request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.farma = form.cleaned_data['farma_name']
            user = form.save()
            user.is_active=True
            user.save()
            group = Group.objects.get(name='farmaceuticos')
            user.groups.add(group)
            return redirect('/gestionar_usuarios')

        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    else:
        form = FarmaUserCreationForm()

    return render(
        request=request,
        template_name="registrar_farmaceutico.html",
        context={"form": form}
        )


def eliminarUsuario(request, username): 
    user = CustomUser.objects.get(username = username)   
    grupo_farmaceutico = Group.objects.get(name='farmaceuticos')
    user.is_active = False
    user.save()

    if grupo_farmaceutico in user.groups.all():
        farma_user = FarmaUser.objects.get(username = username)
        farma_user.id_farma = None
        farma_user.save()

    return JsonResponse({'status':'success'})


def activarUsuario(request, username):
    user = CustomUser.objects.get(username = username)   
    user.is_active = True
    user.save()
    return JsonResponse({'status':'success'})


def obtenerUsuario(request, username):
    user = CustomUser.objects.get(username = username) 
    grupo_farmaceuticos = Group.objects.get(name='farmaceuticos')
    if grupo_farmaceuticos in user.groups.all():
        farma = Farmacia.objects.all()
        farmaUser = FarmaUser.objects.get(username = username) 
        response_data = {
            'isFarmaUser': True,
            'username': farmaUser.username,
            'name': farmaUser.first_name,
            'lastname': farmaUser.last_name,
            'farmacias': [{'id_farma': obj.id_farma, 'nombre': obj.nombre} for obj in farma],
        }

        if farmaUser.id_farma and farmaUser.id_farma.id_farma:
            response_data['selected_farma_name'] = farmaUser.id_farma.id_farma

        return JsonResponse(response_data)
    
    else:
        return JsonResponse({
            'username': user.username,
            'name': user.first_name,
            'lastname': user.last_name,
        })


@login_required(login_url='/acceder')
@require_POST
def editarUsuario(request):
    user = CustomUser.objects.get(username=request.POST.get('username'))
    grupo_farmaceuticos = Group.objects.get(name='farmaceuticos')
    if grupo_farmaceuticos in user.groups.all():
        farmaUser = FarmaUser.objects.get(username=request.POST.get('username'))
        formFarma = FarmaUserUpdateForm(request.POST, instance=farmaUser)
        if formFarma.is_valid():
            formFarma.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': formFarma.errors})   
    else:
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
        

@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['admin'])
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def gestionarFarmacias(request):
    return render(request, "gestionar_farmacias.html")


def listaDeFarmacias(request):
    farmacias = Farmacia.objects.all()

    paginator = Paginator(farmacias, request.GET.get('length', 10))  # Cantidad de objetos por página
    start = int(request.GET.get('start', 0))
    page_number = start // paginator.per_page + 1  # Calcular el número de página basado en 'start'
    page_obj = paginator.get_page(page_number)

    farmacias_list = []
    for index,farma in enumerate(page_obj.object_list):

        usuario_asignado = FarmaUser.objects.filter(id_farma=farma.id_farma).first()
        if usuario_asignado:
            nombre_usuario_asignado = usuario_asignado.username
        else:
            nombre_usuario_asignado = "Ninguno"

        farma_data = {
            'index': index + 1,
            'id': farma.id_farma,
            'nombre': farma.nombre,
            'prov': farma.id_munic.id_prov.nombre,
            'munic': farma.id_munic.nombre,
            'direccion': farma.direccion,
            'telefono': farma.telefono,
            'tipo': farma.id_tipo.nombre,
            'turno': farma.id_turno.nombre,
            'usuario_asignado': nombre_usuario_asignado
        }
        farmacias_list.append(farma_data)

    data = {
        "draw": int(request.GET.get('draw', 0)),
        'recordsTotal': paginator.count,
        'recordsFiltered': paginator.count,
        'data': farmacias_list
    }
    return JsonResponse(data, safe=False)


@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['admin'])
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def registrarFarmacia(request):
    if request.method =='POST':
        form = FarmaUpdateForm(data=request.POST)
        if form.is_valid():
            farma = form.save(commit=False)
            farma.id_turno = form.cleaned_data['id_turno']
            farma.id_tipo = form.cleaned_data['id_tipo']
            farma.id_munic = form.cleaned_data['id_munic']
            farma.save()
            return redirect('/gestionar_farmacias')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
    else:
        form = FarmaUpdateForm()
    
    return render(
        request=request,
        template_name="registrar_farmacia.html",
        context={"form": form}
    )


def obtenerFarmacia(request, uuid):
    turno = TurnoFarmacia.objects.all()
    tipo = TipoFarmacia.objects.all()
    munic = Municipio.objects.all()
    farma = Farmacia.objects.get(id_farma = uuid)   
    return JsonResponse({
        'id': farma.id_farma,
        'nombre': farma.nombre,
        'direccion': farma.direccion,
        'telefono': farma.telefono,
        'selected_turno_name': farma.id_turno.id_turno_farmacia,
        'selected_tipo_name': farma.id_tipo.id_tipo_farmacia,
        'selected_munic_name': farma.id_munic.id_munic,
        'turnos': [{'id_turno': obj.id_turno_farmacia, 'nombre': obj.nombre} for obj in turno],
        'tipos': [{'id_tipo': obj.id_tipo_farmacia, 'nombre': obj.nombre} for obj in tipo],
        'municipios': [{'id_munic': obj.id_munic, 'nombre': obj.nombre} for obj in munic],
    })


@login_required(login_url='/acceder')
@require_POST
def editarFarmacia(request):
    farma = Farmacia.objects.get(id_farma=request.POST.get('id'))
    form = FarmaUpdateForm(request.POST, instance=farma)
    if form.is_valid():
        form.save()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'errors': form.errors})
    

@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['admin'])
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def gestionarTiposFarmacias(request):
    return render(request, "gestionar_tipos_de_farmacias.html")


def listaDeTiposDeFarmacias(request):
    tipos = TipoFarmacia.objects.all()
    tipos_list = []
    for index,tipo in enumerate(tipos):
        tipo_data = {
            'index': index + 1,
            'id': tipo.id_tipo_farmacia,
            'nombre': tipo.nombre,
        }
        tipos_list.append(tipo_data)
    data = {'data': tipos_list}
    return JsonResponse(data, safe=False)


@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['admin'])
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def registrarTipoFarmacia(request):
    if request.method =='POST':
        form = TipoFarmaciaUpdateForm(data=request.POST)
        if form.is_valid():
            tipo = form.save(commit=False)
            tipo.save()
            return redirect('/gestionar_tipos_de_farmacias')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
    else:
        form = TipoFarmaciaUpdateForm()
    
    return render(
        request=request,
        template_name="registrar_tipo_de_farmacia.html",
        context={"form": form}
    )


def obtenerTipoFarmacia(request, uuid):
    tipo = TipoFarmacia.objects.get(id_tipo_farmacia = uuid)
    return JsonResponse({
        'id': tipo.id_tipo_farmacia,
        'name': tipo.nombre,
    })


@login_required(login_url='/acceder')
@require_POST
def editarTipoFarmacia(request):
    tipo = TipoFarmacia.objects.get(id_tipo_farmacia = request.POST.get('id'))
    form = TipoFarmaciaUpdateForm(request.POST, instance=tipo)
    if form.is_valid():
        form.save()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'errors': form.errors})


@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['admin'])
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def gestionarTurnosFarmacias(request):
    return render(request, "gestionar_turnos_de_farmacias.html")


def listaDeTurnosDeFarmacias(request):
    turnos = TurnoFarmacia.objects.all()
    turnos_list = []
    for index,turno in enumerate(turnos):
        turno_data = {
            'index': index + 1,
            'id': turno.id_turno_farmacia,
            'nombre': turno.nombre,
        }
        turnos_list.append(turno_data)
    data = {'data': turnos_list}
    return JsonResponse(data, safe=False)


@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['admin'])
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def registrarTurnoFarmacia(request):
    if request.method =='POST':
        form = TurnoFarmaciaUpdateForm(data=request.POST)
        if form.is_valid():
            turno = form.save(commit=False)
            turno.save()
            return redirect('/gestionar_turnos_de_farmacias')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
    else:
        form = TurnoFarmaciaUpdateForm()
    
    return render(
        request=request,
        template_name="registrar_turno_de_farmacia.html",
        context={"form": form}
    )


def obtenerTurnoFarmacia(request, uuid):
    turno = TurnoFarmacia.objects.get(id_turno_farmacia = uuid)
    return JsonResponse({
        'id': turno.id_turno_farmacia,
        'name': turno.nombre,
    })


@login_required(login_url='/acceder')
@require_POST
def editarTurnoFarmacia(request):
    turno = TurnoFarmacia.objects.get(id_turno_farmacia = request.POST.get('id'))
    form = TurnoFarmaciaUpdateForm(request.POST, instance=turno)
    if form.is_valid():
        form.save()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'errors': form.errors})


@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['admin'])
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def gestionarMunicipios(request):
    return render(request, "gestionar_municipios.html")


def listaDeMunicipios(request):
    municipios = Municipio.objects.all()
    municipios_list = []
    for index,munic in enumerate(municipios):
        munic_data = {
            'index': index + 1,
            'id': munic.id_munic,
            'nombre': munic.nombre,
            'provincia': munic.id_prov.nombre,
        }
        municipios_list.append(munic_data)
    data = {'data': municipios_list}
    return JsonResponse(data, safe=False)


@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['admin'])
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def registrarMunicipio(request):
    if request.method =='POST':
        form = MunicUpdateForm(data=request.POST)
        if form.is_valid():
            munic = form.save(commit=False)
            munic.id_prov = form.cleaned_data['id_prov']
            munic.save()
            return redirect('/gestionar_municipios')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
    else:
        form = MunicUpdateForm()
    
    return render(
        request=request,
        template_name="registrar_municipio.html",
        context={"form": form}
    )


def obtenerMunicipio(request, uuid):
    prov = Provincia.objects.all()
    munic = Municipio.objects.get(id_munic = uuid)
    return JsonResponse({
        'id': munic.id_munic,
        'name': munic.nombre,
        'selected_prov_name': munic.id_prov.id_prov,
        'provincias': [{'id_prov': obj.id_prov, 'nombre': obj.nombre} for obj in prov],
    })


@login_required(login_url='/acceder')
@require_POST
def editarMunicipio(request):
    munic = Municipio.objects.get(id_munic = request.POST.get('id'))
    form = MunicUpdateForm(request.POST, instance=munic)
    if form.is_valid():
        form.save()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'errors': form.errors})
    

@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['admin'])
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def gestionarProvincias(request):
    return render(request, "gestionar_provincias.html")


def listaDeProvincias(request):
    provincias = Provincia.objects.all()
    provincias_list = []
    for index,prov in enumerate(provincias):
        prov_data = {
            'index': index + 1,
            'id': prov.id_prov,
            'nombre': prov.nombre,
        }
        provincias_list.append(prov_data)
    data = {'data': provincias_list}
    return JsonResponse(data, safe=False)


@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['admin'])
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def registrarProvincia(request):
    if request.method =='POST':
        form = ProvUpdateForm(data=request.POST)
        if form.is_valid():
            prov = form.save(commit=False)
            prov.save()
            return redirect('/gestionar_provincias')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
    else:
        form = ProvUpdateForm()
    
    return render(
        request=request,
        template_name="registrar_provincia.html",
        context={"form": form}
    )


def obtenerProvincia(request, uuid):
    prov = Provincia.objects.get(id_prov = uuid)
    return JsonResponse({
        'id': prov.id_prov,
        'name': prov.nombre,
    })


@login_required(login_url='/acceder')
@require_POST
def editarProvincia(request):
    prov = Provincia.objects.get(id_prov = request.POST.get('id'))
    form = ProvUpdateForm(request.POST, instance=prov)
    if form.is_valid():
        form.save()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'errors': form.errors})
    

############################################################################################################################
###############################################   MEDICAMENTOS   ###########################################################


@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['farmaceuticos'])
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def gestionarMedicFarma(request): 
    return render(request, "gestionar_medicfarma.html")


def listaDeMedicFarma(request): 
    if request.user.is_authenticated:
        try:
            farmaceutico = FarmaUser.objects.get(username=request.user.username)
            farmacia_del_farmaceutico = farmaceutico.id_farma
            farmacia_medicamento = FarmaciaMedicamento.objects.filter(id_farma=farmacia_del_farmaceutico)
            medicamentos_list = []
            for index, farmaMedic in enumerate(farmacia_medicamento):
                medic = farmaMedic.id_medic

                if medic.cant_max == 1:
                    cant_max_texto = f'{medic.cant_max} unidad'
                else:
                    cant_max_texto = f'{medic.cant_max} unidades'

                origen_texto = "Natural" if medic.origen_natural else "Fármaco"
                medic_data = {
                    'index': index + 1,
                    'id': str(medic.id_medic),
                    'farma': farmaMedic.id_farma.nombre,
                    'nombre': medic.nombre,
                    'descripcion': medic.description,
                    'cant_max': cant_max_texto,
                    'precio': f'{medic.precio_unidad} CUP/u',
                    'origen': origen_texto,
                    'restriccion': medic.id_restriccion.nombre if medic.id_restriccion else None,
                    'clasificacion': medic.id_clasificacion.nombre if medic.id_clasificacion else None,
                    'existencia': farmaMedic.existencia,
                }
                medicamentos_list.append(medic_data)
            data = {'data': medicamentos_list}
            return JsonResponse(data, safe=False)
        
        except FarmaUser.DoesNotExist:
            return JsonResponse({'error': 'Usuario farmacéutico no encontrado'}, status=404)
    
    return JsonResponse({'error': 'Usuario no autenticado'}, status=401)


#def listaDeMedic(request):
    if request.user.is_authenticated:
        try:
            farmaceutico = FarmaUser.objects.get(username=request.user.username)
            farmacia_del_farmaceutico = farmaceutico.id_farma
            farmacia_medicamento = FarmaciaMedicamento.objects.filter(id_farma=farmacia_del_farmaceutico)
            medicamentos_list = []

            for index, farmaMedic in enumerate(farmacia_medicamento):
                medic = farmaMedic.id_medic

                if medic.cant_max == 1:
                    cant_max_texto = f'{medic.cant_max} unidad'
                else:
                    cant_max_texto = f'{medic.cant_max} unidades'

                origen_texto = "Natural" if medic.origen_natural else "Fármaco"
                medic_data = {
                    'index': index + 1,
                    'id': str(medic.id_medic),
                    'farma': farmaMedic.id_farma.nombre,
                    'nombre': medic.nombre,
                    'descripcion': medic.description,
                    'cant_max': cant_max_texto,
                    'precio': f'{medic.precio_unidad} CUP/u',
                    'origen': origen_texto,
                    'restriccion': medic.id_restriccion.nombre if medic.id_restriccion else None,
                    'clasificacion': medic.id_clasificacion.nombre if medic.id_clasificacion else None,
                    'existencia': farmaMedic.existencia,
                }
                medicamentos_list.append(medic_data)

            # Crear el contexto con los datos de los medicamentos
            context = {
                'medicamentos_list': medicamentos_list  # Pasar la lista de medicamentos al contexto
            }

            # Renderizar la plantilla con el contexto
            return render(
                request=request,
                template_name="gestionar_medicfarma.html", 
                context={"farmacia_del_farmaceutico": farmacia_del_farmaceutico}
                )
        
        except FarmaUser.DoesNotExist:
            return JsonResponse({'error': 'Usuario farmacéutico no encontrado'}, status=404)
    
    return JsonResponse({'error': 'Usuario no autenticado'}, status=401)

@require_POST
def actualizarExistencia(request):
    id_medic = request.POST.get('id_medic')
    existencia = request.POST.get('existencia')

    try:
        farmacia_medicamento = FarmaciaMedicamento.objects.get(id_medic=id_medic)
        farmacia_medicamento.existencia = existencia
        farmacia_medicamento.save()
        return JsonResponse({'message': 'Existencia actualizada correctamente'}, status=200)
    except FarmaciaMedicamento.DoesNotExist:
        return JsonResponse({'error': 'Medicamento no encontrado'}, status=404)


@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['farmaceuticos'])
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def agregarMedicFarma(request):
    if request.method == 'POST':
        try:
            farmaceutico = FarmaUser.objects.get(username=request.user.username)
            idfarma_del_farmaceutico = farmaceutico.id_farma.id_farma
        except FarmaUser.DoesNotExist:
            return redirect('/')

        # Obtener lista de IDs de medicamentos seleccionados del formulario
        selected_medicamento_ids = request.POST.getlist('medicamentos')
    
        for id_medic in selected_medicamento_ids:
            try:
                # Obtener el objeto del medicamento y la farmacia
                medicamento = Medicamento.objects.get(id_medic=id_medic)
                farmacia = Farmacia.objects.get(id_farma=idfarma_del_farmaceutico)
                # Verificar si ya existe la relación para este medicamento y farmacia
                farmacia_medicamento, created = FarmaciaMedicamento.objects.get_or_create(
                    id_medic=medicamento,
                    id_farma=farmacia,
                    defaults={'existencia': 0} 
                )
                # Guardar la relación en la base de datos
                #farmacia_medicamento.save()
            except Medicamento.DoesNotExist:
                pass

        return redirect('/gestionar_medicfarma')

    try:
        farmaceutico = FarmaUser.objects.get(username=request.user.username)
        id_farma = farmaceutico.id_farma.id_farma

        medicamentos_disponibles = Medicamento.objects.exclude(
            farmaciamedicamento__id_farma=id_farma
        ).order_by('nombre') 

    except FarmaUser.DoesNotExist:
        medicamentos_disponibles = Medicamento.objects.none()  # Devolver queryset vacío

    return render(
        request=request,
        template_name="agregar_medicfarma.html",
        context={"medicamentos": medicamentos_disponibles}
    )


@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['farmaceuticos'])
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def gestionarMedicamentos(request): 
    return render(request, "gestionar_medicamentos.html")


def listaDeMedicamentos(request):
    medicamentos = Medicamento.objects.all()

    paginator = Paginator(medicamentos, request.GET.get('length', 10))  # Cantidad de objetos por página
    start = int(request.GET.get('start', 0))
    page_number = start // paginator.per_page + 1  # Calcular el número de página basado en 'start'
    page_obj = paginator.get_page(page_number)

    medicamentos_list = []

    for index,medic in enumerate(page_obj.object_list):
        if medic.cant_max == 1:
            cant_max_texto = f'{medic.cant_max} unidad'
        else:
            cant_max_texto = f'{medic.cant_max} unidades'
        origen_texto = "Natural" if medic.origen_natural else "Fármaco"
        medic_data = {
            'index': index + 1,
            'id': medic.id_medic,
            'nombre': medic.nombre,
            'description': medic.description,
            'cant_max': cant_max_texto,
            'precio_unidad': f'{medic.precio_unidad} CUP/u',
            'origen': origen_texto,
            'restriccion': medic.id_restriccion.nombre if medic.id_restriccion else None,
            'clasificacion': medic.id_clasificacion.nombre if medic.id_clasificacion else None,
        }
        medicamentos_list.append(medic_data)
    data = {
        "draw": int(request.GET.get('draw', 0)),
        'recordsTotal': paginator.count,
        'recordsFiltered': paginator.count,
        'data': medicamentos_list
    }
    return JsonResponse(data, safe=False)


@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['farmaceuticos']) #farmaveutico o admin? consultar ya que la lista de medicamentos seria un nomenclador
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def registrarMedicamento(request):
    if request.method =='POST':
        form = MedicUpdateForm(data=request.POST)
        if form.is_valid():
            medic = form.save(commit=False)
            medic.id_restriccion = form.cleaned_data['id_restriccion']
            medic.id_clasificacion = form.cleaned_data['id_clasificacion']
            medic.save()
            return redirect('/gestionar_medicamentos')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
    else:
        form = MedicUpdateForm()
    
    return render(
        request=request,
        template_name="registrar_medicamento.html",
        context={"form": form}
    )


def obtenerDescripcion(request, uuid):
    medic = Medicamento.objects.get(id_medic = uuid)   
    return JsonResponse({
        'id': medic.id_medic,
        'description': medic.description,
    })


def obtenerMedicamento(request, uuid):
    restriccion = RestriccionMedicamento.objects.all()
    clasificacion = ClasificacionMedicamento.objects.all()
    medic = Medicamento.objects.get(id_medic = uuid)   
    return JsonResponse({
        'id': medic.id_medic,
        'nombre': medic.nombre,
        'description': medic.description,
        'cant_max': medic.cant_max,
        'precio_unidad': medic.precio_unidad,
        'origen': medic.origen_natural,
        'selected_restriccion_name': medic.id_restriccion.id_restriccion,
        'restricciones': [{'id_restriccion': obj.id_restriccion, 'nombre': obj.nombre} for obj in restriccion],
        'selected_clasificacion_name': medic.id_clasificacion.id_clasificacion,
        'clasificaciones': [{'id_clasificacion': obj.id_clasificacion, 'nombre': obj.nombre} for obj in clasificacion],
    })


@login_required(login_url='/acceder')
@require_POST
def editarMedicamento(request):
    print('entro aquiiiii 1')
    medic = Medicamento.objects.get(id_medic=request.POST.get('id'))
    form = MedicUpdateForm(request.POST, instance=medic)
    if form.is_valid():
        print('entro aquiiiii 2')
        medic = form.save(commit=False)
        medic.origen_natural = bool(request.POST.get('origen', False))
        medic.save()
        return JsonResponse({'success': True})
    else:
        print(form.errors)
        return JsonResponse({'success': False, 'errors': form.errors})


@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['farmaceuticos'])
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def gestionarRestriccionesMedicamentos(request):
    return render(request, "gestionar_restricciones_de_medicamentos.html")


def listaDeRestriccionesDeMedicamentos(request):
    restricciones = RestriccionMedicamento.objects.all()
    restricciones_list = []
    for index,restric in enumerate(restricciones):
        restric_data = {
            'index': index + 1,
            'id': restric.id_restriccion,
            'nombre': restric.nombre,
        }
        restricciones_list.append(restric_data)
    data = {'data': restricciones_list}
    return JsonResponse(data, safe=False)


@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['farmaceuticos'])
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def registrarRestriccionMedicamento(request):
    if request.method =='POST':
        form = RestriccionMedicamentoUpdateForm(data=request.POST)
        if form.is_valid():
            restriccion = form.save(commit=False)
            restriccion.save()
            return redirect('/gestionar_restricciones_de_medicamentos')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
    else:
        form = RestriccionMedicamentoUpdateForm()
    
    return render(
        request=request,
        template_name="registrar_restriccion_de_medicamento.html",
        context={"form": form}
    )


def obtenerRestriccionMedicamento(request, uuid):
    restriccion = RestriccionMedicamento.objects.get(id_restriccion = uuid)
    return JsonResponse({
        'id': restriccion.id_restriccion,
        'name': restriccion.nombre,
    })


@login_required(login_url='/acceder')
@require_POST
def editarRestriccionMedicamento(request):
    restriccion = RestriccionMedicamento.objects.get(id_restriccion = request.POST.get('id'))
    form = RestriccionMedicamentoUpdateForm(request.POST, instance=restriccion)
    if form.is_valid():
        form.save()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'errors': form.errors})


@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['farmaceuticos'])
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def gestionarClasificacionesMedicamentos(request):
    return render(request, "gestionar_clasificaciones_de_medicamentos.html")


def listaDeClasificacionesDeMedicamentos(request):
    clasificaciones = ClasificacionMedicamento.objects.all()
    clasificaciones_list = []
    for index,clasific in enumerate(clasificaciones):
        restric_data = {
            'index': index + 1,
            'id': clasific.id_clasificacion,
            'nombre': clasific.nombre,
        }
        clasificaciones_list.append(restric_data)
    data = {'data': clasificaciones_list}
    return JsonResponse(data, safe=False)


@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['farmaceuticos'])
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def registrarClasificacionMedicamento(request):
    if request.method =='POST':
        form = ClasificacionMedicamentoUpdateForm(data=request.POST)
        if form.is_valid():
            clasificacion = form.save(commit=False)
            clasificacion.save()
            return redirect('/gestionar_clasificaciones_de_medicamentos')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
    else:
        form = ClasificacionMedicamentoUpdateForm()
    
    return render(
        request=request,
        template_name="registrar_clasificacion_de_medicamento.html",
        context={"form": form}
    )


def obtenerClasificacionMedicamento(request, uuid):
    clasificacion = ClasificacionMedicamento.objects.get(id_clasificacion = uuid)
    return JsonResponse({
        'id': clasificacion.id_clasificacion,
        'name': clasificacion.nombre,
    })


@login_required(login_url='/acceder')
@require_POST
def editarClasificacionMedicamento(request):
    clasificacion = ClasificacionMedicamento.objects.get(id_clasificacion = request.POST.get('id'))
    form = ClasificacionMedicamentoUpdateForm(request.POST, instance=clasificacion)
    if form.is_valid():
        form.save()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'errors': form.errors})


#def actualizarCantidad(request):
    if request.method == 'POST':
        farmacia = request.POST['farmacia']
        medicamento = request.POST['medicamento']
        cantidad = request.POST['cantidad']
        farmacia_medicamento = FarmaciaMedicamento.objects.get(
            id_medic=medicamento, id_farma=farmacia)
        farmacia_medicamento.existencia = cantidad
        farmacia_medicamento.save()
        return JsonResponse({'status': 'Cantidad actualizada'})
    return redirect('/gestionar/')


################################################################################################################################
#############################################     CLIENTES    ##################################################################


@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['clientes'])
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def farmaciasTabla(request):
    farmacia = Farmacia.objects.all()
    return render(request, "farmacias_tabla.html", {"farmacia": farmacia, })


@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['clientes'])
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def medicamentosTabla(request):
    medic = Medicamento.objects.all()
    return render(request, "medicamentos_tabla.html", {"medic": medic})


@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['clientes'])
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def existenciasTabla(request):
    return render(request, "existencias_tabla.html")


def buscarMedicamento(request):
    terminoDeBusqueda = request.GET['termino']
    payload = []
    if terminoDeBusqueda:
        result = Medicamento.objects.filter(
            nombre__icontains=terminoDeBusqueda)
        for res in result:
            payload.append(res.nombre)
    return JsonResponse({'status': 200, 'data': payload})


class Disponibilidad(object):

    def __init__(self, nombre, telefono, existencia):
        self.nombre = nombre
        self.telefono = telefono
        self.existencia = existencia

    def to_dict(self):
        return {"nombre": self.nombre, "telefono": self.telefono, "existencia": self.existencia}


def buscarDisponibilidad(request):
    terminoDeBusqueda = request.GET['termino']
    payload = []
    if terminoDeBusqueda:
        medicamento = Medicamento.objects.get(nombre=terminoDeBusqueda)
        disponibilidad = FarmaciaMedicamento.objects.filter(
            id_medic=medicamento.id_medic)
        for dis in disponibilidad:
            payload.append(Disponibilidad(nombre=dis.id_farma.nombre,
                           telefono=dis.id_farma.telefono, existencia=dis.existencia).to_dict())
    return JsonResponse(payload, safe=False)

####################################################################################################################


def buscarMunicipio(request):
    terminoDeBusqueda = request.GET['termino']
    payload = []
    if terminoDeBusqueda:
        result = Municipio.objects.filter(nombre__icontains=terminoDeBusqueda)
        for res in result:
            payload.append(res.nombre)
    print(payload)
    return JsonResponse({'status': 200, 'data': payload})


class DisponibilidadFarmacia(object):

    def __init__(self, nombre, direccion, telefono, id_turno, id_tipo):
        self.nombre = nombre
        self.direccion = direccion
        self.telefono = telefono
        self.id_turno = id_turno
        self.id_tipo = id_tipo

    def to_dict(self):
        return {"nombre": self.nombre, "direccion": self.direccion, "telefono": self.telefono, "id_turno": self.id_turno, "id_tipo": self.id_tipo}


def buscarDisponibilidadFarmacia(request):
    terminoDeBusqueda = request.GET['termino']
    payload = []
    if terminoDeBusqueda:
        municipio = Municipio.objects.get(nombre=terminoDeBusqueda)
        disponibilidad = Farmacia.objects.filter(id_munic=municipio)
        for dis in disponibilidad:
            payload.append(DisponibilidadFarmacia(nombre=dis.nombre, direccion=dis.direccion,
                           telefono=dis.telefono, id_turno=dis.id_turno.nombre, id_tipo=dis.id_tipo.nombre).to_dict())
    print(payload)
    return JsonResponse(payload, safe=False)

############################################################################################################################


class DescripcionMedicamento(object):

    def __init__(self, nombre, description):
        self.nombre = nombre
        self.description = description

    def to_dict(self):
        return {"nombre": self.nombre, "description": self.description}


def buscarDescripcionMedicamento(request):
    terminoDeBusqueda = request.GET['termino']
    payload = []
    if terminoDeBusqueda:
        descripcion = Medicamento.objects.get(nombre=terminoDeBusqueda)
        payload.append(DescripcionMedicamento(nombre=descripcion.nombre, description=descripcion.description).to_dict())
    print(payload)
    return JsonResponse(payload, safe=False)




##############################################################################################################################
#############################################     TRAZAS    ##################################################################


@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['admin'])
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def visualizarTrazas(request):
    return render(request, "visualizar_trazas.html")


def listaDeTrazas(request):
    trazas = LogEntry.objects.all()  # Obtener todas las trazas de LogEntry (acciones registradas por Django)

    # Si se solicita un reporte PDF
    if 'reporte_pdf' in request.GET:
        buffer = BytesIO()
        generar_reporte_pdf(trazas, buffer)
        buffer.seek(0)
        response = JsonResponse({'pdf_url': buffer.getvalue()})
        response['Content-Disposition'] = 'attachment; filename="reporte_trazas.pdf"'
        return response

    paginator = Paginator(trazas, request.GET.get('length', 10))  # Cantidad de objetos por página
    start = int(request.GET.get('start', 0))
    page_number = start // paginator.per_page + 1  # Calcular el número de página basado en 'start'
    page_obj = paginator.get_page(page_number)

    trazas_list = []
    for index, traza in enumerate(page_obj.object_list):
        # Verificar si change_message es una lista no vacía antes de intentar acceder al primer elemento
        if traza.change_message:
            try:
                change_message_data = json.loads(traza.change_message)
                if isinstance(change_message_data, list) and len(change_message_data) > 0:
                    change_message = change_message_data[0]
                else:
                    change_message = {}
            except json.JSONDecodeError:
                change_message = {}  # Manejo seguro en caso de que no se pueda decodificar como JSON
        else:
            change_message = {}  # Manejo seguro en caso de que change_message sea None o vacío

        traza_data = {
            'index': index + 1,
            'id': traza.id,
            'action_time': traza.action_time.strftime('%Y-%m-%d %H:%M:%S'),
            'user': traza.user.username if traza.user else 'System',
            'content_type': str(traza.content_type),
            'object_repr': traza.object_repr,
            'action_flag': traza.get_action_flag_display(),
            'change_message': change_message
        }
        trazas_list.append(traza_data)

    data = {
        "draw": int(request.GET.get('draw', 0)),
        'recordsTotal': paginator.count,
        'recordsFiltered': paginator.count,
        'data': trazas_list
    }
    return JsonResponse(data, safe=False)
    

#################################################################################################################################
#############################################     GRAFICOS     ##################################################################


@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['admin'])
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def visualizarCharts(request):
    return render(request, "visualizar_charts.html")


def usuariosXGruposChart(request):
    # Obtener el recuento de usuarios por grupo
    group_counts = CustomUser.objects.values('groups').annotate(count=Count('id'))

    # Definir los nombres de los grupos y los contadores
    labels = ['clientes', 'farmaceuticos', 'admin']
    counts = [0, 0, 0]  # Inicializar contadores para cada grupo

    # Asignar los recuentos reales a los contadores correspondientes
    for item in group_counts:
        group_name = item['groups']
        user_count = item['count']
        if group_name == '1':
            counts[0] = user_count
        elif group_name == '2':
            counts[1] = user_count
        elif group_name == '3':
            counts[2] = user_count

    # Pasar datos al contexto de la plantilla
    context = {
        'labels': labels,
        'counts': counts,
    }

    return JsonResponse(context)


##############################################################################################################################
################################################    MAPA    ##################################################################


def map_view(request):
    return render(request, 'mapa.html')


##############################################################################################################################
################################################    REPORTES    ##################################################################

@csrf_exempt
def generar_reporte_pdf(request):
    if request.method == 'POST':
        # Crear un buffer para el PDF
        buffer = io.BytesIO()

        # Obtener los datos del formulario de filtro
        usuario = request.POST.get('usuario')
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')
        tipo_accion = request.POST.get('tipo_accion')
        contenido = request.POST.get('contenido')

        print('Usuario:', usuario)  # Mensaje de depuración
        print('Fecha Inicio:', fecha_inicio)  # Mensaje de depuración
        print('Fecha Fin:', fecha_fin)  # Mensaje de depuración
        print('Tipo de Acción:', tipo_accion)  # Mensaje de depuración
        print('Contenido:', contenido)  # Mensaje de depuración

        # Filtrar las trazas según los datos del formulario
        trazas = LogEntry.objects.all()

        if usuario:
            trazas = trazas.filter(user__username__icontains=usuario)
        if fecha_inicio:
            try:
                fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
                trazas = trazas.filter(action_time__gte=fecha_inicio_dt)
            except ValueError as e:
                print(f"Error al convertir fecha_inicio: {e}")
        if fecha_fin:
            try:
                fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')
                trazas = trazas.filter(action_time__lte=fecha_fin_dt)
            except ValueError as e:
                print(f"Error al convertir fecha_fin: {e}")
        if tipo_accion:
            try:
                tipo_accion_int = int(tipo_accion)
                trazas = trazas.filter(action_flag=tipo_accion_int)
            except ValueError as e:
                print(f"Error al convertir tipo_accion: {e}")
        if contenido:
            trazas = trazas.filter(object_repr__icontains=contenido)

        print('Trazas encontradas:', trazas.count())  # Mensaje de depuración

        # Generar el reporte PDF
        doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
        elements = []

        style_table = TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONT', (0, 1), (-1, -1), 'Helvetica'),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.gray)
        ])

        # Datos para la tabla
        data = [
            ['#', 'ID', 'Fecha y Hora', 'Usuario', 'Tipo de Objeto', 'Objeto', 'Acción', 'Detalles']
        ]

        for index, traza in enumerate(trazas):
            change_message = json.loads(traza.change_message) if traza.change_message else {}
            data.append([
                index + 1,
                traza.id,
                traza.action_time.strftime('%Y-%m-%d %H:%M:%S'),
                traza.user.username if traza.user else 'System',
                str(traza.content_type),
                traza.object_repr,
                traza.get_action_flag_display(),
                change_message.get('message', '')
            ])

        print('Datos para la tabla:', data)  # Mensaje de depuración

        table = Table(data)
        table.setStyle(style_table)
        elements.append(table)

        doc.build(elements)

        # Devolver el reporte PDF al frontend
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename='reporte_trazas.pdf')

    return JsonResponse({'error': 'Método no permitido'}, status=405)