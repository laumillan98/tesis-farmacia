from os import name
import os
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
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.core.paginator import Paginator, EmptyPage
from django.core.management import call_command
from django.contrib import messages
from django.contrib.gis.geos import Point
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from django.contrib.sites.shortcuts import get_current_site
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.decorators.cache import cache_control
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.utils.timezone import localtime
from django.contrib.contenttypes.models import ContentType

from easyaudit.models import CRUDEvent, LoginEvent, RequestEvent
from base.pdf_utils import header_footer

from .models import CustomUser, Medicamento, Farmacia, FarmaUser, FarmaciaMedicamento, Entrada, Salida, TipoFarmacia, TurnoFarmacia, Municipio, Provincia, RestriccionMedicamento, ClasificacionMedicamento, FormatoMedicamento, TareaExistencia, Notificacion
from .forms import CustomUserCreationForm, FarmaUserCreationForm, UserLoginForm, SetPasswordForm, PasswordResetForm, UserProfileForm, UserUpdateForm, FarmaUserUpdateForm, FarmaUpdateForm, TipoFarmaciaUpdateForm, TurnoFarmaciaUpdateForm, MunicUpdateForm, ProvUpdateForm, MedicUpdateForm, RestriccionMedicamentoUpdateForm, ClasificacionMedicamentoUpdateForm, FormatoMedicamentoUpdateForm, EntradaMedicamentoCreateForm
from .decorators import usuarios_permitidos, unauthenticated_user
from .tokens import account_activation_token
from FirstApp.tasks import send_activation_email
from django_tables2 import RequestConfig

# Librería ReportLab
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Paragraph
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4, landscape
from io import BytesIO
from reportlab.lib.pagesizes import letter
from django.views.decorators.csrf import csrf_exempt
from .pdf_utils import header_footer

from django.contrib.gis.geos import Point

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
        date_time = now.strftime("%Y-%m-%d %H:%M:%S")  # Formatear la fecha y hora
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

        # Actualizar la variable de entorno PATH para incluir el directorio Scripts del entorno virtual
        python_executable = r'C:\Users\ceper\Downloads\Python\my-env\Scripts\python.exe'

        process = subprocess.Popen([python_executable, 'manage.py', 'dbrestore'], stdin=subprocess.PIPE)
        process.communicate(input=input_stream.getvalue().encode())
        with open('restore_log.txt', 'a') as f:
            f.write(f"Restauración realizada el {date_time}\n")
        return JsonResponse({'status': 'success'})
    except Exception as e:
        print(e)
        return JsonResponse({'status': 'error', 'message': str(e)})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def salir(request):
    logout(request)
    return redirect('/acceder/')


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
                usuario = request.user
                grupo_admin = Group.objects.get(name='admin')
                grupo_clientes = Group.objects.get(name='clientes')
                grupo_farmaceuticos = Group.objects.get(name='farmacéuticos')
                grupo_especialista = Group.objects.get(name='especialista')
                if grupo_admin in usuario.groups.all():
                    return redirect('/gestionar_usuarios/')
                elif grupo_clientes in usuario.groups.all():
                    return redirect('/visualizar_tabla_medicamentos/')
                elif grupo_farmaceuticos in usuario.groups.all():
                    return redirect('/gestionar_medicfarma/')
                elif grupo_especialista in usuario.groups.all():
                    return redirect('/gestionar_farmacias/')  
            else:
                messages.error(request, "Nombre de usuario o contraseña incorrectos")
        else:
            messages.error(request, "Nombre de usuario o contraseña incorrectos")
                     
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
@usuarios_permitidos(roles_permitidos=['admin'])
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def perfilAdmin(request, username):
    show_alert = False
    if request.method == "POST":
        user = request.user
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            user_form = form.save()
            show_alert = True
            return redirect('/perfil_admin/' + user_form.username)
        
        for error in list(form.errors.values()):
            messages.error(request, error)

    user = get_user_model().objects.get(username=username)
    if user:
        form = UserProfileForm(instance=user)
        return render(
            request=request,
            template_name="perfil_admin.html",
            context={"form": form, "show_alert": show_alert}
        )
    
    return redirect('/')


@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['especialista'])
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def perfilEspecialista(request, username):
    show_alert = False
    if request.method == "POST":
        user = request.user
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            user_form = form.save()
            show_alert = True
            return redirect('/perfil_especialista/' + user_form.username)
        
        for error in list(form.errors.values()):
            messages.error(request, error)

    user = get_user_model().objects.get(username=username)
    if user:
        form = UserProfileForm(instance=user)
        return render(
            request=request,
            template_name="perfil_especialista.html",
            context={"form": form, "show_alert": show_alert}
        )
    
    return redirect('/')


@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['clientes'])
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def perfilCliente(request, username):
    show_alert = False
    if request.method == "POST":
        user = request.user
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            user_form = form.save()
            show_alert = True
            return redirect('/perfil_cliente/' + user_form.username)
        
        for error in list(form.errors.values()):
            messages.error(request, error)

    user = get_user_model().objects.get(username=username)
    if user:
        form = UserProfileForm(instance=user)
        return render(
            request=request,
            template_name="perfil_cliente.html",
            context={"form": form, "show_alert": show_alert}
        )
    
    return redirect('/')


@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['farmacéuticos'])
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def perfilFarmaceutico(request, username):
    show_alert = False
    if request.method == "POST":
        user = request.user
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            user_form = form.save()
            show_alert = True
            return redirect('/perfil_farmaceutico/' + user_form.username)
        
        for error in list(form.errors.values()):
            messages.error(request, error)

    user = get_user_model().objects.get(username=username)
    if user:
        form = UserProfileForm(instance=user)
        return render(
            request=request,
            template_name="perfil_farmaceutico.html",
            context={"form": form, "show_alert": show_alert}
        )
    
    return redirect('/')


@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['admin'])
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def gestionarUsuarios(request):
    return render(request, "gestionar_usuarios.html")


def filterUsers(users, search_value):
    if search_value:
        return users.filter(
            Q(first_name__icontains=search_value) |
            Q(last_name__icontains=search_value) |
            Q(username__icontains=search_value) |
            Q(email__icontains=search_value) |
            Q(groups__name__icontains=search_value) |
            Q(date_joined__icontains=search_value) |
            Q(last_login__icontains=search_value)
        )
    return users


def orderUsers(users, order_column_index, order_direction):
    order_column_mapping = {
        '1': 'first_name',
        '2': 'last_name',
        '3': 'username',
        '4': 'email',
        '5': 'groups__name',  
        '6': 'date_joined',
        '7': 'last_login',
    }
    if order_column_index in order_column_mapping:
        order_column = order_column_mapping[order_column_index]
        if order_direction == 'desc':
            order_column = '-' + order_column
        users = users.order_by(order_column)
    
    return users


def listaDeUsuarios(request):
    users = CustomUser.objects.all()

    order_column_index = request.GET.get("order[0][column]", "")
    order_direction = request.GET.get("order[0][dir]", "")
    search_value = request.GET.get("search[value]", "")

    users = filterUsers(users, search_value)
    users = orderUsers(users, order_column_index, order_direction)

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
            'index': start + index + 1,
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
            user.id_farma = form.cleaned_data['id_farma']
            user = form.save()
            user.is_active=True
            user.save()
            group = Group.objects.get(name='farmacéuticos')
            user.groups.add(group)
            return redirect('/gestionar_usuarios/')

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


@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['admin'])
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def registrarEspecialista(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(data=request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user = form.save()
            user.is_active=True
            user.save()
            group = Group.objects.get(name='especialista')
            user.groups.add(group)
            return redirect('/gestionar_usuarios/')

        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    else:
        form = CustomUserCreationForm()

    return render(
        request=request,
        template_name="registrar_especialista.html",
        context={"form": form}
        )


@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['admin'])
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def registrarAdministrador(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(data=request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user = form.save()
            user.is_active=True
            user.save()
            group = Group.objects.get(name='admin')
            user.groups.add(group)
            return redirect('/gestionar_usuarios/')

        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    else:
        form = CustomUserCreationForm()

    return render(
        request=request,
        template_name="registrar_administrador.html",
        context={"form": form}
        )


def eliminarUsuario(request, username): 
    user = CustomUser.objects.get(username = username)   
    grupo_farmaceutico = Group.objects.get(name='farmacéuticos')
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
    grupo_farmaceuticos = Group.objects.get(name='farmacéuticos')
    if grupo_farmaceuticos in user.groups.all():
        farma = Farmacia.objects.all()
        farmaUser = FarmaUser.objects.get(username = username) 
        response_data = {
            'isFarmaUser': True,
            'username': farmaUser.username,
            'name': farmaUser.first_name,
            'lastname': farmaUser.last_name,
            'description': farmaUser.description,
            'email': farmaUser.email,
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
            'description': user.description,
            'email': user.email,
        })


@login_required(login_url='/acceder')
@require_POST
def editarUsuario(request):
    user = CustomUser.objects.get(username=request.POST.get('username'))
    grupo_farmaceuticos = Group.objects.get(name='farmacéuticos')
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
        

"""@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['admin'])
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def gestionarRolesUsuarios(request):
    return render(request, "gestionar_roles.html")


def listaDeRolesUsuarios(request):
    roles = Group.objects.all()
    roles_list = []
    for index,rol in enumerate(roles):
        rol_data = {
            'index': index + 1,
            'name': rol.name,
        }
        roles_list.append(rol_data)
    data = {'data': roles_list}
    return JsonResponse(data, safe=False)


@login_required(login_url='/acceder')
@require_POST
def registrarRolUsuario(request):
    print('entro1')
    if request.method == 'POST':
        print('entro2')
        form = RolUsuarioUpdateForm(data=request.POST)
        if form.is_valid():
            print('entro3')
            rol = form.save(commit=False)
            rol.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'errors': 'Invalid request method'})


def obtenerRolUsuario(request, name):
    rol = Group.objects.get(name = name)
    return JsonResponse({
        'name': rol.name,
    })


@login_required(login_url='/acceder')
@require_POST
def editarRolUsuario(request):
    rol = Group.objects.get(name = name)
    form = RolUsuarioUpdateForm(request.POST, instance=rol)
    if form.is_valid():
        form.save()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'errors': form.errors})"""


##################################################################################################################################
#####################################################  PROVINCIA  ################################################################


@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['especialista'])
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
@require_POST
def registrarProvincia(request):
    if request.method == 'POST':
        form = ProvUpdateForm(data=request.POST)
        if form.is_valid():
            prov = form.save(commit=False)
            prov.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'errors': 'Invalid request method'})


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
    

##################################################################################################################################
######################################################  MUNICIPIO  ###############################################################


@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['especialista'])
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
@require_POST
def registrarMunicipio(request):
    if request.method == 'POST':
        form = MunicUpdateForm(data=request.POST)
        if form.is_valid():
            munic = form.save(commit=False)
            munic.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'errors': 'Invalid request method'})


def obtenerProvMunicipio(request):
    provincias = Provincia.objects.all()
    data = [{'id_prov': prov.id_prov, 'nombre': prov.nombre} for prov in provincias]
    return JsonResponse({'provincias': data})


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


##################################################################################################################################
######################################################  FARMACIA  ################################################################

        
@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['especialista'])
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def gestionarFarmacias(request):
    #Codigo para poder seleccionar de las listas siguientes en el filtrado para exportar la tabla
    provincias = Provincia.objects.all()
    municipios = Municipio.objects.all()
    tipos = TipoFarmacia.objects.all()
    turnos = TurnoFarmacia.objects.all()
    context = {
        'provincias': provincias,
        'municipios': municipios,
        'tipos': tipos,
        'turnos': turnos
    }
    return render(request, "gestionar_farmacias.html", context)


def filterFarmas(farmacias, search_value):
    if search_value:
        return farmacias.filter(
            Q(nombre__icontains=search_value) |
            Q(id_munic__id_prov__nombre__icontains=search_value) |
            Q(id_munic__nombre__icontains=search_value) |
            Q(direccion__icontains=search_value) |
            Q(telefono__icontains=search_value) |
            Q(id_turno__nombre__icontains=search_value) |
            Q(id_tipo__nombre__icontains=search_value)
        )
    return farmacias


def orderFarmas(farmacias, order_column_index, order_direction):
    order_column_mapping = {
        '1': 'nombre',
        '2': 'id_munic__id_prov__nombre',
        '3': 'id_munic__nombre',
        '4': 'direccion',
        '5': 'telefono',
        '6': 'id_tipo__nombre',
        '7': 'id_turno__nombre',
    }
    if order_column_index in order_column_mapping:
        order_column = order_column_mapping[order_column_index]
        if order_direction == 'desc':
            order_column = '-' + order_column
        farmacias = farmacias.order_by(order_column)
    return farmacias


def listaDeFarmacias(request):
    farmacias = Farmacia.objects.all()
   
    order_column_index = request.GET.get("order[0][column]", "")
    order_direction = request.GET.get("order[0][dir]", "")
    search_value = request.GET.get("search[value]", "")

    farmacias = filterFarmas(farmacias, search_value)
    farmacias = orderFarmas(farmacias, order_column_index, order_direction)
   
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
            'index': start + index + 1,
            'id': farma.id_farma,
            'nombre': farma.nombre,
            'prov': farma.id_munic.id_prov.nombre,
            'munic': farma.id_munic.nombre,
            'direccion': farma.direccion,
            'telefono': farma.telefono,
            'tipo': farma.id_tipo.nombre,
            'turno': farma.id_turno.nombre,
            'usuario_asignado': nombre_usuario_asignado,
            'latitud': farma.ubicacion.y if farma.ubicacion else None,
            'longitud': farma.ubicacion.x if farma.ubicacion else None,
        }
        farmacias_list.append(farma_data)

    data = {
        "draw": int(request.GET.get('draw', 0)),
        "draw": int(request.GET.get('draw', 0)),
        'recordsTotal': paginator.count,
        'recordsFiltered': paginator.count,
        'data': farmacias_list
    }
    return JsonResponse(data, safe=False)


@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['especialista'])
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
@usuarios_permitidos(roles_permitidos=['especialista'])
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@require_POST
def editarUbicacionFarmacia(request, uuid):
    farmacia = Farmacia.objects.get(id_farma=uuid)
    latitud = request.POST.get('latitud')
    longitud = request.POST.get('longitud')
    flat = float(latitud)
    flon = float(longitud)
    print(flat)
    print(flon)
    if farmacia is not None and latitud is not None and longitud is not None:
        farmacia.ubicacion = Point(flon, flat)
        farmacia.save()
        return JsonResponse({'success': True}, status=200)
    else:
        JsonResponse({'error': 'Invalid request'}, status=400)
    

@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['especialista'])
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
@require_POST
def registrarTipoFarmacia(request):
    if request.method == 'POST':
        form = TipoFarmaciaUpdateForm(data=request.POST)
        if form.is_valid():
            tipo = form.save(commit=False)
            tipo.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'errors': 'Invalid request method'})


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
@usuarios_permitidos(roles_permitidos=['especialista'])
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
@require_POST
def registrarTurnoFarmacia(request):
    if request.method == 'POST':
        form = TurnoFarmaciaUpdateForm(data=request.POST)
        if form.is_valid():
            turno = form.save(commit=False)
            turno.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'errors': 'Invalid request method'})


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


############################################################################################################################
###############################################   MEDICAMENTOS   ###########################################################


@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['especialista'])
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def gestionarMedicamentos(request): 
    #Codigo para poder seleccionar de las listas siguientes en el filtrado para exportar la tabla
    formatos = FormatoMedicamento.objects.all()
    restricciones = RestriccionMedicamento.objects.all()
    clasificaciones = ClasificacionMedicamento.objects.all()
    context = {
        'formatos': formatos,
        'restricciones': restricciones,
        'clasificaciones': clasificaciones,
    }
    return render(request, "gestionar_medicamentos.html", context)


def listaDeMedicamentos(request):
    medicamentos = Medicamento.objects.all()

    order_column_index = request.GET.get("order[0][column]", "")
    order_direction = request.GET.get("order[0][dir]", "")
    search_value = request.GET.get("search[value]", "")

    medicamentos = filterMedics(medicamentos, search_value)
    medicamentos = orderMedics(medicamentos, order_column_index, order_direction)

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
            'index': start + index + 1,
            'id': medic.id_medic,
            'nombre': medic.nombre,
            'description': medic.description,
            'cant_max': cant_max_texto,
            'precio_unidad': f'{medic.precio_unidad} CUP/u',
            'origen': origen_texto,
            'restriccion': medic.id_restriccion.nombre if medic.id_restriccion else None,
            'clasificacion': medic.id_clasificacion.nombre if medic.id_clasificacion else None,
            'formato': medic.id_formato.nombre if medic.id_formato else None,
            'reacciones': medic.reacciones,
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
@usuarios_permitidos(roles_permitidos=['especialista']) 
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def registrarMedicamento(request):
    if request.method == 'POST':
        form = MedicUpdateForm(data=request.POST)
        if form.is_valid():
            medic = form.save(commit=False)
            medic.id_restriccion = form.cleaned_data['id_restriccion']
            medic.id_clasificacion = form.cleaned_data['id_clasificacion']
            medic.id_formato = form.cleaned_data['id_formato']
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


def obtenerReacciones(request, uuid):
    medic = Medicamento.objects.get(id_medic = uuid)   
    return JsonResponse({
        'id': medic.id_medic,
        'reacciones': medic.reacciones,
    })


def obtenerMedicamento(request, uuid):
    restriccion = RestriccionMedicamento.objects.all()
    clasificacion = ClasificacionMedicamento.objects.all()
    formato = FormatoMedicamento.objects.all()
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
        'selected_formato_name': medic.id_formato.id_formato,
        'formatos': [{'id_formato': obj.id_formato, 'nombre': obj.nombre} for obj in formato],
        'reacciones': medic.reacciones,
    })


@login_required(login_url='/acceder')
@require_POST
def editarMedicamento(request):
    medic = Medicamento.objects.get(id_medic=request.POST.get('id'))
    form = MedicUpdateForm(request.POST, instance=medic)
    if form.is_valid():
        medic = form.save(commit=False)
        medic.origen_natural = bool(request.POST.get('origen', False))
        medic.save()
        return JsonResponse({'success': True})
    else:
        print(form.errors)
        return JsonResponse({'success': False, 'errors': form.errors})


@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['especialista'])
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
@require_POST
def registrarRestriccionMedicamento(request):
    if request.method == 'POST':
        form = RestriccionMedicamentoUpdateForm(data=request.POST)
        if form.is_valid():
            rest = form.save(commit=False)
            rest.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'errors': 'Invalid request method'})


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
@usuarios_permitidos(roles_permitidos=['especialista'])
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
@require_POST
def registrarClasificacionMedicamento(request):
    if request.method == 'POST':
        form = ClasificacionMedicamentoUpdateForm(data=request.POST)
        if form.is_valid():
            clasif = form.save(commit=False)
            clasif.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'errors': 'Invalid request method'})


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


@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['especialista'])
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def gestionarFormatosMedicamentos(request):
    return render(request, "gestionar_formatos_de_medicamentos.html")


def listaDeFormatosDeMedicamentos(request):
    formatos = FormatoMedicamento.objects.all()
    formatos_list = []
    for index,format in enumerate(formatos):
        restric_data = {
            'index': index + 1,
            'id': format.id_formato,
            'nombre': format.nombre,
        }
        formatos_list.append(restric_data)
    data = {'data': formatos_list}
    return JsonResponse(data, safe=False)


@login_required(login_url='/acceder')
@require_POST
def registrarFormatoMedicamento(request):
    if request.method == 'POST':
        form = FormatoMedicamentoUpdateForm(data=request.POST)
        if form.is_valid():
            formato = form.save(commit=False)
            formato.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'errors': 'Invalid request method'})


def obtenerFormatoMedicamento(request, uuid):
    formato = FormatoMedicamento.objects.get(id_formato = uuid)
    return JsonResponse({
        'id': formato.id_formato,
        'name': formato.nombre,
    })


@login_required(login_url='/acceder')
@require_POST
def editarFormatoMedicamento(request):
    formato = FormatoMedicamento.objects.get(id_formato = request.POST.get('id'))
    form = FormatoMedicamentoUpdateForm(request.POST, instance=formato)
    if form.is_valid():
        form.save()
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'errors': form.errors})
    

################################################################################################################################
###############################################   FARMACIA MEDICAMENTOS   ######################################################


@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['farmacéuticos'])
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def gestionarMedicFarma(request): 
    # Obtener nombre de la Farmacia del farmaceutico actual
    farmaceutico = FarmaUser.objects.get(username=request.user.username)
    farmacia_del_farmaceutico = farmaceutico.id_farma.nombre
    # Codigo para poder seleccionar de las listas siguientes en el filtrado para exportar la tabla
    formatos = FormatoMedicamento.objects.all()
    restricciones = RestriccionMedicamento.objects.all()
    clasificaciones = ClasificacionMedicamento.objects.all()
    context = {
        'farmacia_id': farmaceutico.id_farma.id_farma,
        'farmacia_del_farmaceutico': farmacia_del_farmaceutico,
        'formatos': formatos,
        'restricciones': restricciones,
        'clasificaciones': clasificaciones
    }
    return render(request, "gestionar_medicfarma.html", context)


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
                    'id_farma_medic': farmaMedic.id,
                    'id': str(medic.id_medic),
                    'farma': farmaMedic.id_farma.nombre,
                    'nombre': medic.nombre,
                    'formato': medic.id_formato.nombre,
                    'descripcion': medic.description,
                    'cant_max': cant_max_texto,
                    'precio': f'{medic.precio_unidad} CUP/u',
                    'origen': origen_texto,
                    'restriccion': medic.id_restriccion.nombre if medic.id_restriccion else None,
                    'clasificacion': medic.id_clasificacion.nombre if medic.id_clasificacion else None,
                    'existencia': farmaMedic.existencia,
                    'id_farmaMedic': farmaMedic.id,
                }
                medicamentos_list.append(medic_data)
            data = {'data': medicamentos_list}
            return JsonResponse(data, safe=False)
        
        except FarmaUser.DoesNotExist:
            return JsonResponse({'error': 'Usuario farmacéutico no encontrado'}, status=404)
    
    return JsonResponse({'error': 'Usuario no autenticado'}, status=401)
    

@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['farmacéuticos'])
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def gestionarMedicamentosDisponibles(request):
    restricciones = RestriccionMedicamento.objects.all()
    clasificaciones = ClasificacionMedicamento.objects.all()
    formatos = FormatoMedicamento.objects.all()

    context = {
        'restricciones': restricciones,
        'clasificaciones': clasificaciones,
        'formatos': formatos
    }

    return render(request, "gestionar_medicamentos_disponibles.html", context)


def filterMedics(medicamentos, search_value):
    if search_value:
        search_value_lower = search_value.lower()

        origen_natural_search = None
        if search_value_lower == 'natural':
            origen_natural_search = True
        elif search_value_lower == 'fármaco' or search_value_lower == 'farmaco':
            origen_natural_search = False

        medicamentos = medicamentos.filter(
            Q(nombre__icontains=search_value) |
            Q(id_formato__nombre__icontains=search_value) |
            Q(cant_max__icontains=search_value) |
            Q(precio_unidad__icontains=search_value) |
            Q(id_restriccion__nombre__icontains=search_value) |
            Q(id_clasificacion__nombre__icontains=search_value) |
            Q(origen_natural=origen_natural_search)
        )
    return medicamentos


def orderMedics(medicamentos, order_column_index, order_direction):
    order_column_mapping = {
        '1': 'nombre',
        '2': 'id_formato__nombre',
        '3': 'cant_max',
        '4': 'precio_unidad',
        '5': 'origen_natural',
        '6': 'id_restriccion__nombre',
        '7': 'id_clasificacion__nombre',
    }
    if order_column_index in order_column_mapping:
        order_column = order_column_mapping[order_column_index]
        if order_direction == 'desc':
            order_column = '-' + order_column
        medicamentos = medicamentos.order_by(order_column)
    return medicamentos


def listaDeMedicamentosDisponibles(request):
    usuario = request.user
    farmaceutico = FarmaUser.objects.get(username=usuario.username)
    farmacia = farmaceutico.id_farma
    # Obtén los IDs de los medicamentos que ya están en la farmacia del usuario actual
    medicamentos_en_farmacia = FarmaciaMedicamento.objects.filter(id_farma=farmacia).values_list('id_medic', flat=True)
    # Filtra los medicamentos disponibles excluyendo los que ya están en la farmacia del usuario
    medicamentos = Medicamento.objects.exclude(id_medic__in=medicamentos_en_farmacia)

    order_column_index = request.GET.get("order[0][column]", "")
    order_direction = request.GET.get("order[0][dir]", "")
    search_value = request.GET.get("search[value]", "")

    medicamentos = filterMedics(medicamentos, search_value)
    medicamentos = orderMedics(medicamentos, order_column_index, order_direction)

    paginator = Paginator(medicamentos, request.GET.get('length', 10))  # Cantidad de objetos por página
    start = int(request.GET.get('start', 0))
    page_number = start // paginator.per_page + 1  # Calcular el número de página basado en 'start'
    page_obj = paginator.get_page(page_number)

    medicamentos_list = []

    for index, medic in enumerate(page_obj.object_list):
        if medic.cant_max == 1:
            cant_max_texto = f'{medic.cant_max} unidad'
        else:
            cant_max_texto = f'{medic.cant_max} unidades'
        origen_texto = "Natural" if medic.origen_natural else "Fármaco"
        medic_data = {
            'index': start + index + 1,
            'id': medic.id_medic,
            'nombre': medic.nombre,
            'description': medic.description,
            'cant_max': cant_max_texto,
            'precio_unidad': f'{medic.precio_unidad} CUP/u',
            'origen': origen_texto,
            'restriccion': medic.id_restriccion.nombre if medic.id_restriccion else None,
            'clasificacion': medic.id_clasificacion.nombre if medic.id_clasificacion else None,
            'formato': medic.id_formato.nombre if medic.id_formato else None,
        }
        medicamentos_list.append(medic_data)

    data = {
        "draw": int(request.GET.get('draw', 0)),
        'recordsTotal': paginator.count,
        'recordsFiltered': paginator.count,
        'data': medicamentos_list
    }
    return JsonResponse(data, safe=False)


@csrf_exempt
def exportarMedicamento(request, uuid):
    if request.method == 'POST':
        try:
            medicamento = Medicamento.objects.get(id_medic=uuid)
            usuario = request.user
            farmaceutico = FarmaUser.objects.get(username=usuario.username)
            farmacia = farmaceutico.id_farma

            if farmacia:
                # Verificar si el medicamento ya está en la farmacia
                if FarmaciaMedicamento.objects.filter(id_medic=medicamento, id_farma=farmacia).exists():
                    return JsonResponse({'status': 'error', 'message': 'El medicamento ya está en tu farmacia.'}, status=400)

                FarmaciaMedicamento.objects.create(
                    id_medic=medicamento,
                    id_farma=farmacia,
                    existencia=0  
                )
                return JsonResponse({'status': 'success'}, status=200)
            else:
                return JsonResponse({'status': 'error', 'message': 'Farmacia no encontrada'}, status=400)
        except Medicamento.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Medicamento no encontrado'}, status=404)
        except FarmaUser.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Usuario no encontrado'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)


@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['farmacéuticos'])
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def gestionarEntradasMedicamento(request):
    farmacia_actual = request.user.farmauser.id_farma  # Obteniendo la farmacia del usuario actual
    farmaciaMedicamentos = FarmaciaMedicamento.objects.filter(id_farma=farmacia_actual)
    return render(request, "gestionar_entradas_medicamento.html", {
        'farmacia_actual': farmacia_actual, 
        'farmaciaMedicamentos': farmaciaMedicamentos
    })


def filterEntries(entradas, search_value):
    if search_value:
        entradas = entradas.filter(
            Q(factura__icontains=search_value) |
            Q(numero_lote__icontains=search_value) |
            Q(cantidad__icontains=search_value) |
            Q(fecha_creacion__icontains=search_value) |
            Q(fecha_elaboracion__icontains=search_value) |
            Q(fecha_vencimiento__icontains=search_value) |
            Q(id_farmaciaMedicamento__id_medic__nombre__icontains=search_value)
        )
    return entradas


def orderEntries(entradas, order_column_index, order_direction):
    order_column_mapping = {
        '1': 'factura',
        '2': 'numero_lote',
        '3': 'cantidad',
        '4': 'fecha_creacion',
        '5': 'fecha_elaboracion',
        '6': 'fecha_vencimiento',
        '7': 'id_farmaciaMedicamento__id_medic__nombre',
    }
    if order_column_index in order_column_mapping:
        order_column = order_column_mapping[order_column_index]
        if order_direction == 'desc':
            order_column = '-' + order_column
        entradas = entradas.order_by(order_column)
    return entradas


def listaDeEntradasMedicamento(request): 
    farmacia_id = request.GET.get('farmacia_id')
    entradas = Entrada.objects.filter(id_farmaciaMedicamento__id_farma=farmacia_id)

    order_column_index = request.GET.get("order[0][column]", "")
    order_direction = request.GET.get("order[0][dir]", "")
    search_value = request.GET.get("search[value]", "")

    entradas = filterEntries(entradas, search_value)
    entradas = orderEntries(entradas, order_column_index, order_direction)

    paginator = Paginator(entradas, request.GET.get('length', 10))  # Cantidad de objetos por página
    start = int(request.GET.get('start', 0))
    page_number = start // paginator.per_page + 1  # Calcular el número de página basado en 'start'
    page_obj = paginator.get_page(page_number)

    entradas_list = []

    for index, ent in enumerate(page_obj.object_list):
        medicamento_nombre = ent.id_farmaciaMedicamento.id_medic.nombre if ent.id_farmaciaMedicamento.id_medic else ''
        formato_nombre = ent.id_farmaciaMedicamento.id_medic.id_formato.nombre if ent.id_farmaciaMedicamento.id_medic.id_formato else ''
        medicamento_formato = f"{medicamento_nombre} - {formato_nombre}"
        
        ent_data = {
            'index': start + index + 1,
            'id': ent.id,
            'factura': ent.factura,
            'numero_lote': ent.numero_lote,
            'cantidad': ent.cantidad,
            'fecha_creacion': ent.fecha_creacion.strftime('%Y-%m-%d'),
            'fecha_elaboracion': ent.fecha_elaboracion.strftime('%Y-%m-%d'),
            'fecha_vencimiento': ent.fecha_vencimiento.strftime('%Y-%m-%d'),
            'medicamento_formato': medicamento_formato,
        }
        entradas_list.append(ent_data)
    data = {
        "draw": int(request.GET.get('draw', 0)),
        'recordsTotal': paginator.count,
        'recordsFiltered': paginator.count,
        'data': entradas_list
    }
    return JsonResponse(data, safe=False)


def registrarEntradaMedicamento(request):
    form = EntradaMedicamentoCreateForm(request.POST)
    if form.is_valid():
        entrada = form.save(commit=False)
        entrada.fecha_creacion = timezone.now().date()
        entrada.save()
        # Actualizar la existencia en FarmaciaMedicamento
        farmacia_medicamento = entrada.id_farmaciaMedicamento
        farmacia_medicamento.existencia += entrada.cantidad
        farmacia_medicamento.save()

        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'errors': form.errors})


@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['farmacéuticos'])
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def realizarCierreFarmacia(request):
    # Obtener nombre de la Farmacia del farmaceutico actual
    farmaceutico = FarmaUser.objects.get(username=request.user.username)
    farmacia_del_farmaceutico = farmaceutico.id_farma.nombre
    
    context = {
        'farmacia_del_farmaceutico': farmacia_del_farmaceutico,
    }
    return render(request, "realizar_cierre_farmacia.html", context)


def filterCierre(farmacia_medicamento, search_value):
    if search_value:
        farmacia_medicamento = farmacia_medicamento.filter(
            Q(id_medic__nombre__icontains=search_value) |
            Q(id_medic__id_formato__nombre__icontains=search_value) |
            Q(id_medic__precio_unidad__icontains=search_value) 
        )
    return farmacia_medicamento


def orderCierre(farmacia_medicamento, order_column_index, order_direction):
    order_column_mapping = {
        '1': 'id_medic__nombre',
        '2': 'id_medic__id_formato__nombre',
        '3': 'id_medic__precio_unidad',
    }
    if order_column_index in order_column_mapping:
        order_column = order_column_mapping[order_column_index]
        if order_direction == 'desc':
            order_column = '-' + order_column
        farmacia_medicamento = farmacia_medicamento.order_by(order_column)
    return farmacia_medicamento


def listaDeCierreFarmacia(request): 
    farmaceutico = FarmaUser.objects.get(username=request.user.username)
    farmacia_del_farmaceutico = farmaceutico.id_farma
    farmacia_medicamento = FarmaciaMedicamento.objects.filter(id_farma=farmacia_del_farmaceutico)

    order_column_index = request.GET.get("order[0][column]", "")
    order_direction = request.GET.get("order[0][dir]", "")
    search_value = request.GET.get("search[value]", "")

    farmacia_medicamento = filterCierre(farmacia_medicamento, search_value)
    farmacia_medicamento = orderCierre(farmacia_medicamento, order_column_index, order_direction)

    paginator = Paginator(farmacia_medicamento, request.GET.get('length', 10))  # Cantidad de objetos por página
    start = int(request.GET.get('start', 0))
    page_number = start // paginator.per_page + 1  # Calcular el número de página basado en 'start'
    page_obj = paginator.get_page(page_number)

    medicamentos_list = []

    for index, farmaMedic in enumerate(page_obj.object_list):

        farmaMedic_data = {
            'index': start + index + 1,
            'medicamento': farmaMedic.id_medic.nombre,
            'formato': farmaMedic.id_medic.id_formato.nombre,
            'precio': f'{farmaMedic.id_medic.precio_unidad} CUP/u',
            'existencia': farmaMedic.existencia,
            'id_farmaMedic':farmaMedic.id,
        }
        medicamentos_list.append(farmaMedic_data)
    data = {
        "draw": int(request.GET.get('draw', 0)),
        'recordsTotal': paginator.count,
        'recordsFiltered': paginator.count,
        'data': medicamentos_list
    }
    return JsonResponse(data, safe=False)


@login_required(login_url='/acceder')
@require_POST
def guardarVentas(request):
    ventas = json.loads(request.body)
    print(ventas)
    for venta in ventas:
        print(venta)
        print(venta['id'])
        farmacia_medicamento = FarmaciaMedicamento.objects.get(id=venta['id'])
        cantidad = int(venta['cantidad'])
        if cantidad <= farmacia_medicamento.existencia:
            farmacia_medicamento.existencia -= cantidad
            farmacia_medicamento.save()
            Salida.objects.create(
                id_farmaciaMedicamento=farmacia_medicamento,
                cantidad=cantidad,
                fecha_movimiento=timezone.now()
            )
        else:
            return JsonResponse({'success': False, 'error': 'La cantidad de ventas no puede ser mayor a la existencia'})
    return JsonResponse({'success': True})


@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['farmacéuticos'])
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def gestionarSalidasMedicamento(request):
    farmacia_actual = request.user.farmauser.id_farma  # Obteniendo la farmacia del usuario actual
    salidas = Salida.objects.filter(id_farmaciaMedicamento__id_farma=farmacia_actual, fecha_movimiento=timezone.now().date())

    return render(request, "gestionar_salidas_medicamento.html", {
        'farmacia_actual': farmacia_actual, 
        'salidas': salidas
    })


def filterExits(salidas, search_value):
    if search_value:
        salidas = salidas.filter(
            Q(id_farmaciaMedicamento__id_medic__nombre__icontains=search_value) |
            Q(id_farmaciaMedicamento__id_medic__id_formato__nombre__icontains=search_value) |
            Q(cantidad__icontains=search_value) |
            Q(fecha_movimiento__icontains=search_value)
        )
    return salidas


def orderExits(salidas, order_column_index, order_direction):
    order_column_mapping = {
        '1': 'id_farmaciaMedicamento__id_medic__nombre',
        '2': 'id_farmaciaMedicamento__id_medic__id_formato__nombre',
        '3': 'cantidad',
        '5': 'fecha_movimiento',
    }
    if order_column_index in order_column_mapping:
        order_column = order_column_mapping[order_column_index]
        if order_direction == 'desc':
            order_column = '-' + order_column
        salidas = salidas.order_by(order_column)
    return salidas


def listaDeSalidasMedicamento(request): 
    farmacia_id = request.GET.get('farmacia_id')
    salidas = Salida.objects.filter(id_farmaciaMedicamento__id_farma=farmacia_id, fecha_movimiento=timezone.now().date())

    order_column_index = request.GET.get("order[0][column]", "")
    order_direction = request.GET.get("order[0][dir]", "")
    search_value = request.GET.get("search[value]", "")

    salidas = filterExits(salidas, search_value)
    salidas = orderExits(salidas, order_column_index, order_direction)

    paginator = Paginator(salidas, request.GET.get('length', 10))  # Cantidad de objetos por página
    start = int(request.GET.get('start', 0))
    page_number = start // paginator.per_page + 1  # Calcular el número de página basado en 'start'
    page_obj = paginator.get_page(page_number)

    salidas_list = []

    for index, sal in enumerate(page_obj.object_list):

        if sal.cantidad == 1:
            cantidad_texto = f'{sal.cantidad} unidad'
        else:
            cantidad_texto = f'{sal.cantidad} unidades'

        precio_medic = sal.id_farmaciaMedicamento.id_medic.precio_unidad
        monto_total = precio_medic * sal.cantidad
        
        sal_data = {
            'index': start + index + 1,
            'id': sal.id,
            'medicamento': sal.id_farmaciaMedicamento.id_medic.nombre,
            'formato': sal.id_farmaciaMedicamento.id_medic.id_formato.nombre,
            'cantidad': cantidad_texto,
            'monto_total': f'{monto_total} CUP',
            'fecha_movimiento': sal.fecha_movimiento.strftime('%Y-%m-%d')
        }
        salidas_list.append(sal_data)
    data = {
        "draw": int(request.GET.get('draw', 0)),
        'recordsTotal': paginator.count,
        'recordsFiltered': paginator.count,
        'data': salidas_list
    }
    return JsonResponse(data, safe=False)


################################################################################################################################
#######################################################   CLIENTES   ###########################################################


@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['clientes'])
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def visualizarTablaMedicamentos(request):
    return render(request, "visualizar_tabla_medicamentos.html")


def buscarInfoMedicamento(request):
    if request.method == 'GET':
        nombre_medicamento = request.GET.get('nombre_medicamento', '')

        if nombre_medicamento:
            medicamentos = Medicamento.objects.filter(nombre__icontains=nombre_medicamento)
            has_interactions = any(medicamento.reacciones for medicamento in medicamentos)
            resultados = []

            for medicamento in medicamentos:
                if medicamento.cant_max == 1:
                    cant_max_texto = f'{medicamento.cant_max} unidad'
                else:
                    cant_max_texto = f'{medicamento.cant_max} unidades'
                origen_texto = "Natural" if medicamento.origen_natural else "Fármaco"
                resultados.append({
                    'id': medicamento.id_medic,
                    'nombre': medicamento.nombre,
                    'description': medicamento.description,
                    'reacciones': medicamento.reacciones,
                    'cant_max': cant_max_texto,
                    'precio_unidad': f'{medicamento.precio_unidad} CUP/u',
                    'origen': origen_texto,
                    'restriccion': medicamento.id_restriccion.nombre if medicamento.id_restriccion else None,
                    'clasificacion': medicamento.id_clasificacion.nombre if medicamento.id_clasificacion else None,
                    'formato': medicamento.id_formato.nombre if medicamento.id_formato else None,
                })
            return JsonResponse({'has_interactions': has_interactions, 'result': resultados}, safe=False)
        else:
            return JsonResponse({'error': 'Debe ingresar un nombre de medicamento.'}, status=400)

    return JsonResponse({'error': 'Método no permitido.'}, status=405)


def buscarMedicamento(request):
    if request.method == 'GET':
        id_medicamento = request.GET.get('id_medicamento', '')

        if id_medicamento:
            medicamentos = Medicamento.objects.filter(id_medic=id_medicamento)
            resultados = []

            for medicamento in medicamentos:
                farmacias = FarmaciaMedicamento.objects.filter(id_medic=medicamento, existencia__gt=0)
                has_task = TareaExistencia.objects.filter(id_medic=medicamento, id_user=request.user)
                for farmacia in farmacias:
                    resultados.append({
                        'id_medic': medicamento.id_medic,
                        'medicamento': medicamento.nombre,
                        'reacciones': medicamento.reacciones,
                        'nombre_farmacia': farmacia.id_farma.nombre,
                        'direccion': farmacia.id_farma.direccion,
                        'telefono': farmacia.id_farma.telefono,
                        'existencia': farmacia.existencia,
                        'nombre_municipio': farmacia.id_farma.id_munic.nombre,
                        'nombre_provincia': farmacia.id_farma.id_munic.id_prov.nombre,
                        'tipo': farmacia.id_farma.id_tipo.nombre,
                        'turno': farmacia.id_farma.id_turno.nombre,
                        'latitud': farmacia.id_farma.ubicacion.y if farmacia.id_farma.ubicacion else None,
                        'longitud': farmacia.id_farma.ubicacion.x if farmacia.id_farma.ubicacion else None,
                        'notificacion_activa': has_task.count() > 0
                    })
            return JsonResponse({'result': resultados}, safe=False)
        else:
            return JsonResponse({'error': 'Debe ingresar un nombre de medicamento.'}, status=400)

    return JsonResponse({'error': 'Método no permitido.'}, status=405)


@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['clientes'])
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def visualizarTablaFarmacias(request):
    return render(request, "visualizar_tabla_farmacias.html")


def buscarFarmacia(request):
    if request.method == 'GET':
        nombre_municipio = request.GET.get('nombre_municipio', '')

        if nombre_municipio:
            farmacias = Farmacia.objects.filter(id_munic__nombre__icontains=nombre_municipio)
            resultados = []

            for farmacia in farmacias:
                resultados.append({
                    'nombre_farmacia': farmacia.nombre,
                    'direccion': farmacia.direccion,
                    'telefono': farmacia.telefono,
                    'nombre_provincia': farmacia.id_munic.id_prov.nombre,
                    'nombre_municipio': farmacia.id_munic.nombre,
                    'tipo': farmacia.id_tipo.nombre,
                    'turno': farmacia.id_turno.nombre,
                    'latitud': farmacia.ubicacion.y if farmacia.ubicacion else None,
                    'longitud': farmacia.ubicacion.x if farmacia.ubicacion else None,
                })
            return JsonResponse(resultados, safe=False)
        else:
            return JsonResponse({'error': 'Debe ingresar un nombre de municipio.'}, status=400)

    return JsonResponse({'error': 'Método no permitido.'}, status=405)



##############################################################################################################################
###############################################   TRAZAS   ###################################################################


@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['admin'])
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def visualizarTrazasCrud(request):
    return render(request, "visualizar_trazas_crud.html")


def filterTrazasCrud(trazas, search_value):
    if search_value:
        event_type_mapping = {
            'adición': CRUDEvent.CREATE,
            'modificación': CRUDEvent.UPDATE,
            'eliminación': CRUDEvent.DELETE,
        }
        
        search_value_lower = search_value.lower()
        event_type = event_type_mapping.get(search_value_lower, None)
        
        search_filter = Q(datetime__icontains=search_value) | \
                        Q(user__username__icontains=search_value) | \
                        Q(content_type__model__icontains=search_value) | \
                        Q(object_repr__icontains=search_value) | \
                        Q(changed_fields__icontains=search_value)
        
        if event_type is not None:
            search_filter |= Q(event_type=event_type)
        
        trazas = trazas.filter(search_filter)
    return trazas


def orderTrazasCrud(trazas, order_column_index, order_direction):
    order_column_mapping = {
        '1': 'datetime',
        '2': 'user__username',
        '4': 'content_type__model',
        '5': 'object_repr',
        '6': 'event_type',
        '7': 'changed_fields',
    }
    if order_column_index in order_column_mapping:
        order_column = order_column_mapping[order_column_index]
        if order_direction == 'desc':
            order_column = '-' + order_column
        trazas = trazas.order_by(order_column)
    return trazas


def listaDeTrazasCrud(request):
    try:
        eventos = CRUDEvent.objects.all()  # Obtener todos los eventos de CRUDEvent
        login_events = {event.user_id: event.remote_ip for event in LoginEvent.objects.all()}  # Obtener todos los eventos de LoginEvent y mapear user_id a remote_ip

        order_column_index = request.GET.get("order[0][column]", "")
        order_direction = request.GET.get("order[0][dir]", "")
        search_value = request.GET.get("search[value]", "")

        trazas = filterTrazasCrud(eventos, search_value)
        trazas = orderTrazasCrud(trazas, order_column_index, order_direction)

        paginator = Paginator(trazas, request.GET.get('length', 10))  # Cantidad de objetos por página
        start = int(request.GET.get('start', 0))
        page_number = start // paginator.per_page + 1  # Calcular el número de página basado en 'start'
        page_obj = paginator.get_page(page_number)

        trazas_list = []
        for index, traza in enumerate(page_obj.object_list):

            if traza.event_type == CRUDEvent.CREATE:
                event_type_display = 'Adición'
            elif traza.event_type == CRUDEvent.UPDATE:
                event_type_display = 'Modificación'
            elif traza.event_type == CRUDEvent.DELETE:
                event_type_display = 'Eliminación'
            else:
                event_type_display = traza.get_event_type_display()

            ip_address = login_events.get(traza.user_id, "No disponible")  # Obtener la IP del usuario si existe
                
            traza_data = {
                'index': start + index + 1,
                'id': traza.id,
                'action_time': localtime(traza.datetime).strftime('%Y-%m-%d %H:%M:%S'),
                'user': traza.user.username if traza.user else 'System',
                'content_type': str(traza.content_type),
                'object_repr': traza.object_repr,
                'action_flag': traza.get_event_type_display(),
                'change_message': traza.object_json_repr if hasattr(traza, 'object_json_repr') else "Sin cambios",
                'remote_addr': traza.remote_addr if hasattr(traza, 'remote_addr') else "No disponible",
                'additional_data': traza.additional_data if hasattr(traza, 'additional_data') else "No disponible",
                'action_flag': event_type_display,
                'change_message': traza.changed_fields if traza.changed_fields else "Sin cambios",
                'ip_address': ip_address
            }
            trazas_list.append(traza_data)

        data = {
            "draw": int(request.GET.get('draw', 0)),
            'recordsTotal': paginator.count,
            'recordsFiltered': paginator.count,
            'data': trazas_list
        }
        return JsonResponse(data, safe=False)
    except Exception as e:
        print(e)
        return JsonResponse({'error': str(e)}, status=500)

    

@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['admin'])
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def visualizarTrazasSistema(request):
    return render(request, "visualizar_trazas_sistema.html")


def translate_action_flag(action_flag):
    action_flag_map = {
        1: 'Adición',
        2: 'Modificación',
        3: 'Eliminación',
    }
    return action_flag_map.get(action_flag, 'Desconocido')


def filterTrazasSist(trazas, search_value):
    if search_value:
        translated_action_flags = {
            'Adición': 1,
            'Modificación': 2,
            'Eliminación': 3,
        }
        
        search_value_action_flag = [flag for flag, value in translated_action_flags.items() if search_value.lower() in flag.lower()]

        q_objects = Q(action_time__icontains=search_value) | \
                    Q(user__username__icontains=search_value) | \
                    Q(content_type__app_label__icontains=search_value) | \
                    Q(content_type__model__icontains=search_value) | \
                    Q(object_repr__icontains=search_value) | \
                    Q(change_message__icontains=search_value)

        if search_value_action_flag:
            q_objects |= Q(action_flag__in=[translated_action_flags[flag] for flag in search_value_action_flag])

        trazas = trazas.filter(q_objects)
    return trazas


def orderTrazasSist(trazas, order_column_index, order_direction):
    order_column_mapping = {
        '1': 'action_time',
        '2': 'user__username',
        '3': 'content_type__app_label',
        '4': 'object_repr',
        '5': 'action_flag',
        '6': 'change_message',
    }
    if order_column_index in order_column_mapping:
        order_column = order_column_mapping[order_column_index]
        if order_direction == 'desc':
            order_column = '-' + order_column
        trazas = trazas.order_by(order_column)
    return trazas


def listaDeTrazasSistema(request):
    trazas = LogEntry.objects.all()  # Obtener todas las trazas de LogEntry (acciones registradas por Django)

    order_column_index = request.GET.get("order[0][column]", "")
    order_direction = request.GET.get("order[0][dir]", "")
    search_value = request.GET.get("search[value]", "")

    trazas = filterTrazasSist(trazas, search_value)
    trazas = orderTrazasSist(trazas, order_column_index, order_direction)

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

        action_flag_display = translate_action_flag(traza.action_flag)

        traza_data = {
            'index': start + index + 1,
            'id': traza.id,
            'action_time': traza.action_time.strftime('%Y-%m-%d %H:%M:%S'),
            'user': traza.user.username if traza.user else 'System',
            'content_type': str(traza.content_type),
            'object_repr': traza.object_repr,
            'action_flag': action_flag_display,
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


def generar_lote_farmacias(request):
    turno = TurnoFarmacia.objects.get(id_turno_farmacia="d331dd6a-9436-48f6-8c1a-ca83cf9707b2")
    tipo = TipoFarmacia.objects.get(id_tipo_farmacia="a6e903a9-e962-4fcd-98bb-4c5dd2779964")
    mun = Municipio.objects.get(id_munic="efa53364-32d2-4a33-ac33-dd30c985bb5f")
    for i in range(1, 300):
        farmacia = Farmacia(
            nombre = f'Farmacia {i}',
            direccion = f'Direccion random {i}',
            telefono = 6440141, 
            id_turno = turno,
            id_tipo = tipo,
            id_munic = mun,
        )
        farmacia.save()
    return JsonResponse({'success': True})

def borrar_lote_farmacias(request):
    farmacias = Farmacia.objects.all()
    farmacias.delete()
    return JsonResponse({'success': True})

##############################################################################################################################
################################################    REPORTES    ##################################################################


def generate_user_report(request, objetos):
    username = request.POST.get('username')
    fecha_inicio = request.POST.get('fecha_inicio')
    fecha_fin = request.POST.get('fecha_fin')
    rol = request.POST.get('rol')
    activo = request.POST.get('activo')

    if fecha_inicio:
        try:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            objetos = objetos.filter(date_joined__gte=fecha_inicio_dt)
        except ValueError:
            pass
    if fecha_fin:
        try:
            fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')
            objetos = objetos.filter(date_joined__lte=fecha_fin_dt)
        except ValueError:
            pass
    if username:
        objetos = objetos.filter(username__icontains=username)
    if rol:
        objetos = objetos.filter(groups__name__icontains=rol.lower())
    if activo:
        is_active = True if activo == 'True' else False
        objetos = objetos.filter(is_active=is_active)
    if not objetos.exists():
        return None  # Return None if no objects are found
    
    data = [
        ['#', 'Nombre', 'Apellidos', 'Usuario', 'Correo', 'Roles', 'Fecha de registro', 'Último acceso', 'Activo']
    ]
    for index, objeto in enumerate(objetos):
        roles = ', '.join([group.name for group in objeto.groups.all()])
        data.append([
            index + 1,
            objeto.first_name,
            objeto.last_name,
            objeto.username,
            objeto.email,
            roles,
            objeto.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
            objeto.last_login.strftime('%Y-%m-%d %H:%M:%S') if objeto.last_login else 'N/A',
            'Sí' if objeto.is_active else 'No'
        ])
    return data


def generate_farmacia_report(request, objetos):
    nombre = request.POST.get('nombre')
    provincia = request.POST.get('provincia')
    municipio = request.POST.get('municipio')
    tipo = request.POST.get('tipo')
    turno = request.POST.get('turno')

    if nombre:
        objetos = objetos.filter(nombre__icontains=nombre)
    if provincia:
        objetos = objetos.filter(id_munic__id_prov__nombre=provincia)
    if municipio:
        objetos = objetos.filter(id_munic__nombre=municipio)
    if tipo:
        objetos = objetos.filter(id_tipo__nombre=tipo)
    if turno:
        objetos = objetos.filter(id_turno__nombre=turno)
    if not objetos.exists():
        return None  # Return None if no objects are found
    
    data = [
        ['#', 'Nombre', 'Provincia', 'Municipio', 'Direccion', 'Telefono', 'Tipo', 'Turno', 'Farmacéutico']
    ]
    for index, objeto in enumerate(objetos):
        farmaceutico = FarmaUser.objects.filter(id_farma=objeto.id_farma).first()
        farmaceutico_username = farmaceutico.username if farmaceutico else 'N/A'
        data.append([
            index + 1,
            objeto.nombre,
            objeto.id_munic.id_prov.nombre,
            objeto.id_munic.nombre,
            objeto.direccion,
            objeto.telefono,
            objeto.id_tipo.nombre,
            objeto.id_turno.nombre,
            farmaceutico_username
        ])
    return data


def generate_traza_crud_report(request, objetos):
    login_events = {event.user_id: event.remote_ip for event in LoginEvent.objects.all()}
    usuario = request.POST.get('usuario')
    fecha_inicio = request.POST.get('fecha_inicio')
    fecha_fin = request.POST.get('fecha_fin')
    tipo_accion = request.POST.get('tipo_accion')
    contenido = request.POST.get('contenido')

    if usuario:
        objetos = objetos.filter(user__username__icontains=usuario)
    if fecha_inicio:
        try:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            objetos = objetos.filter(datetime__gte=fecha_inicio_dt)
        except ValueError as e:
            print(f"Error al convertir fecha_inicio: {e}")
    if fecha_fin:
        try:
            fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')
            objetos = objetos.filter(datetime__lte=fecha_fin_dt)
        except ValueError as e:
            print(f"Error al convertir fecha_fin: {e}")
    if tipo_accion:
        try:
            tipo_accion_int = int(tipo_accion)
            objetos = objetos.filter(event_type=tipo_accion_int)
        except ValueError as e:
            print(f"Error al convertir tipo_accion: {e}")
    if contenido:
        objetos = objetos.filter(object_repr__icontains=contenido)
    if not objetos.exists():
        return None 
    
    max_char_length = 40

    data = [
        ['#', 'Fecha y Hora', 'IP Remota', 'Usuario', 'Tipo de Objeto', 'Objeto', 'Acción']
    ]
    for index, objeto in enumerate(objetos):
        ip_remota = login_events.get(objeto.user_id, "No disponible")
        accion = 'Adición' if objeto.event_type == 1 else 'Modificación' if objeto.event_type == 2 else 'Eliminación'
        # Truncar el contenido del objeto si excede el límite
        object_repr_truncated = (objeto.object_repr[:max_char_length] + '...') if len(objeto.object_repr) > max_char_length else objeto.object_repr
        data.append([
            index + 1,
            objeto.datetime.strftime('%Y-%m-%d %H:%M:%S'),
            ip_remota,
            objeto.user.username if objeto.user else 'System',
            str(objeto.content_type),
            object_repr_truncated,
            accion
        ])
    return data


def generate_traza_sistema_report(request, objetos):
    usuario = request.POST.get('usuario')
    fecha_inicio = request.POST.get('fecha_inicio')
    fecha_fin = request.POST.get('fecha_fin')
    tipo_accion = request.POST.get('tipo_accion')
    contenido = request.POST.get('contenido')

    if usuario:
        objetos = objetos.filter(user__username__icontains=usuario)
    if fecha_inicio:
        try:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, '%Y-%m-%d')
            objetos = objetos.filter(action_time__gte=fecha_inicio_dt)
        except ValueError as e:
            print(f"Error al convertir fecha_inicio: {e}")
    if fecha_fin:
        try:
            fecha_fin_dt = datetime.strptime(fecha_fin, '%Y-%m-%d')
            objetos = objetos.filter(action_time__lte=fecha_fin_dt)
        except ValueError as e:
            print(f"Error al convertir fecha_fin: {e}")
    if tipo_accion:
        try:
            tipo_accion_int = int(tipo_accion)
            objetos = objetos.filter(action_flag=tipo_accion_int)
        except ValueError as e:
            print(f"Error al convertir tipo_accion: {e}")
    if contenido:
        objetos = objetos.filter(object_repr__icontains=contenido)
    if not objetos.exists():
        return None  
    
    max_char_length = 40

    data = [
        ['#', 'Fecha y Hora', 'Usuario', 'Tipo de Objeto', 'Objeto', 'Acción']
    ]
    for index, objeto in enumerate(objetos):
        # Truncar el contenido del objeto si excede el límite
        object_repr_truncated = (objeto.object_repr[:max_char_length] + '...') if len(objeto.object_repr) > max_char_length else objeto.object_repr
        data.append([
            index + 1,
            objeto.action_time.strftime('%Y-%m-%d %H:%M:%S'),
            objeto.user.username if objeto.user else 'System',
            str(objeto.content_type) if objeto.content_type else 'N/A',
            object_repr_truncated,
            {ADDITION: 'Adición', CHANGE: 'Modificación', DELETION: 'Eliminación'}.get(objeto.action_flag, ''),
        ])
    return data


def generate_medicamento_report(request, objetos):
    nombre = request.POST.get('nombre')
    formato = request.POST.get('formato')
    restriccion = request.POST.get('restriccion')
    clasificacion = request.POST.get('clasificacion')
    origen = request.POST.get('origen')

    if nombre:
        objetos = objetos.filter(nombre__icontains=nombre)
    if formato:
        objetos = objetos.filter(id_formato__nombre=formato)
    if restriccion:
        objetos = objetos.filter(id_restriccion__nombre=restriccion)
    if clasificacion:
        objetos = objetos.filter(id_clasificacion__nombre=clasificacion)
    if origen:
        if origen == '1':
            objetos = objetos.filter(origen_natural=True)
        elif origen == '0':
            objetos = objetos.filter(origen_natural=False)
    if not objetos.exists():
        return None  

    data = [
        ['#', 'Nombre', 'Formato', 'Restriccion', 'Clasificacion', 'Origen', 'Precio', 'Cantidad Max']
    ]
    for index, objeto in enumerate(objetos):
        origen_texto = "Natural" if objeto.origen_natural else "Fármaco"
        precio_text = f'{objeto.precio_unidad} CUP/u'
        cant_max_texto = f"{objeto.cant_max} unidad" if objeto.cant_max == 1 else f"{objeto.cant_max} unidades"

        data.append([
            index + 1,
            objeto.nombre,
            objeto.id_formato.nombre,
            objeto.id_restriccion.nombre,
            objeto.id_clasificacion.nombre,
            origen_texto,
            precio_text,
            cant_max_texto
        ])
    return data


def generate_medicfarma_report(request, objetos):
    # Obtener la farmacia del usuario actual
    usuario = request.user
    try:
        farmaceutico = FarmaUser.objects.get(username=usuario.username)
        farmacia = farmaceutico.id_farma
        objetos = objetos.filter(id_farma=farmacia)  # Filtrar por la farmacia del usuario actual
    except FarmaUser.DoesNotExist:
        return "Sin farmacia", None  # Devuelve dos valores aunque no se encuentren datos

    nombre = request.POST.get('nombre')
    formato = request.POST.get('formato')
    restriccion = request.POST.get('restriccion')
    clasificacion = request.POST.get('clasificacion')
    origen = request.POST.get('origen')

    if nombre:
        objetos = objetos.filter(id_medic__nombre__icontains=nombre)
    if formato:
        objetos = objetos.filter(id_medic__id_formato__nombre=formato)
    if restriccion:
        objetos = objetos.filter(id_medic__id_restriccion__nombre=restriccion)
    if clasificacion:
        objetos = objetos.filter(id_medic__id_clasificacion__nombre=clasificacion)
    if origen:
        if origen == '1':
            objetos = objetos.filter(id_medic__origen_natural=True)
        elif origen == '0':
            objetos = objetos.filter(id_medic__origen_natural=False)
    if not objetos.exists():
        return "Sin farmacia", None  # Devuelve dos valores aunque no se encuentren datos

    farmacia_nombre = farmacia.nombre if farmacia else "Desconocida" 

    data = [
        ['#', 'Nombre', 'Formato', 'Restriccion', 'Clasificacion', 'Origen', 'Precio', 'Cantidad Max', 'Existencias']
    ]
    for index, objeto in enumerate(objetos):
        origen_texto = "Natural" if objeto.id_medic.origen_natural else "Fármaco"
        precio_text = f'{objeto.id_medic.precio_unidad} CUP/u'
        cant_max_texto = f"{objeto.id_medic.cant_max} unidad" if objeto.id_medic.cant_max == 1 else f"{objeto.id_medic.cant_max} unidades"

        data.append([
            index + 1,
            objeto.id_medic.nombre,
            objeto.id_medic.id_formato.nombre,
            objeto.id_medic.id_restriccion.nombre,
            objeto.id_medic.id_clasificacion.nombre,
            origen_texto,
            precio_text,
            cant_max_texto,
            objeto.existencia
        ])
    return farmacia_nombre, data


def generate_entrada_report(request, objetos):
    # Obtener las entradas del usuario actual
    usuario = request.user
    try:
        farmaceutico = FarmaUser.objects.get(username=usuario.username)
        farmacia = farmaceutico.id_farma
        objetos = objetos.filter(id_farmaciaMedicamento__id_farma=farmacia)  # Filtrar por la farmacia del usuario actual
    except FarmaUser.DoesNotExist:
        return "Sin farmacia", []

    factura = request.POST.get('factura')
    lote = request.POST.get('lote')
    medicamento = request.POST.get('medicamento')
    fecha_creacion = request.POST.get('fecha_creacion')
    fecha_elaboracion = request.POST.get('fecha_elaboracion')
    fecha_vencimiento = request.POST.get('fecha_vencimiento')

    if factura:
        objetos = objetos.filter(factura__icontains=factura)
    if lote:
        objetos = objetos.filter(numero_lote__icontains=lote)
    if medicamento:
        objetos = objetos.filter(id_farmaciaMedicamento__id_medic__nombre__icontains=medicamento)
    if fecha_creacion:
        try:
            fecha_creacion_dt = datetime.strptime(fecha_creacion, '%Y-%m-%d')
            objetos = objetos.filter(fecha_creacion__gte=fecha_creacion_dt)
        except ValueError:
            pass
    if fecha_elaboracion:
        try:
            fecha_elaboracion_dt = datetime.strptime(fecha_elaboracion, '%Y-%m-%d')
            objetos = objetos.filter(fecha_elaboracion__gte=fecha_elaboracion_dt)
        except ValueError:
            pass
    if fecha_vencimiento:
        try:
            fecha_vencimiento_dt = datetime.strptime(fecha_vencimiento, '%Y-%m-%d')
            objetos = objetos.filter(fecha_vencimiento__lte=fecha_vencimiento_dt)
        except ValueError:
            pass

    data = [
        ['#', 'Factura', 'Lote', 'Cantidad', 'Fecha Creación', 'Fecha Elaboración', 'Fecha Vencimiento', 'Medicamento']
    ]
    if not objetos.exists():
        return farmacia.nombre, data  # Retornar nombre de farmacia y sólo la fila de encabezados

    for index, objeto in enumerate(objetos):
        medicamento_nombre = objeto.id_farmaciaMedicamento.id_medic.nombre

        data.append([
            index + 1,
            objeto.factura,
            objeto.numero_lote,
            objeto.cantidad,
            objeto.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S'),
            objeto.fecha_elaboracion.strftime('%Y-%m-%d %H:%M:%S') if objeto.fecha_elaboracion else '',
            objeto.fecha_vencimiento.strftime('%Y-%m-%d %H:%M:%S') if objeto.fecha_vencimiento else '',
            medicamento_nombre
        ])
    return farmacia.nombre, data


def generate_salida_report(request, objetos):
    # Obtener las salidas del usuario actual
    usuario = request.user
    try:
        farmaceutico = FarmaUser.objects.get(username=usuario.username)
        farmacia = farmaceutico.id_farma
        objetos = objetos.filter(id_farmaciaMedicamento__id_farma=farmacia, fecha_movimiento=timezone.now().date())  # Filtrar por la farmacia del usuario actual y las salidas del día
    except FarmaUser.DoesNotExist:
        return "Sin farmacia", []  # Devuelve dos valores aunque no se encuentren datos
    
    if not objetos.exists():
        return farmacia.nombre, []  # Return None if no objects are found

    data = [
        ['#', 'Medicamento', 'Formato', 'Cantidad Vendida', 'Monto Total', 'Fecha Movimiento']
    ]
    for index, objeto in enumerate(objetos):
        medicamento_nombre = objeto.id_farmaciaMedicamento.id_medic.nombre
        formato_nombre = objeto.id_farmaciaMedicamento.id_medic.id_formato.nombre
        precio_medic = objeto.id_farmaciaMedicamento.id_medic.precio_unidad
        cantidad_vendida = objeto.cantidad
        monto_total = precio_medic * cantidad_vendida

        data.append([
            index + 1,
            medicamento_nombre,
            formato_nombre,
            cantidad_vendida,
            monto_total,
            objeto.fecha_movimiento.strftime('%Y-%m-%d %H:%M:%S'),
        ])
    return farmacia.nombre, data


@csrf_exempt
def generar_reporte_pdf(request):
    if request.method == 'POST':
        entity = ''
        buffer = io.BytesIO()

        tipo_objeto = request.POST.get('tipo_objeto')

        # Definir el estilo de tabla una vez
        style_table = TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONT', (0, 1), (-1, -1), 'Helvetica'),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.gray)
        ])

        if tipo_objeto == 'usuario':
            objetos = CustomUser.objects.all()
            data = generate_user_report(request, objetos)
            filename = 'reporte_usuarios.pdf'
            report_title = "Lista de Usuarios en el Sistema"
            entity = 'Usuario'
        elif tipo_objeto == 'farmacia':
            objetos = Farmacia.objects.all()
            data = generate_farmacia_report(request, objetos)
            filename = 'reporte_farmacias.pdf'
            report_title = "Lista de Farmacias en La Habana"
            entity = 'Farmacias'
        elif tipo_objeto == 'trazaCrud':
            objetos = CRUDEvent.objects.all()
            data = generate_traza_crud_report(request, objetos)
            filename = 'reporte_trazas_crud.pdf'
            report_title = "Lista de Trazas CRUD"
            entity = 'Trazas'
        elif tipo_objeto == 'trazaSistema':
            objetos = LogEntry.objects.all()
            data = generate_traza_sistema_report(request, objetos)
            filename = 'reporte_trazas_sistema.pdf'
            report_title = "Lista de Trazas del Sistema"
            entity = 'Trazas'
        elif tipo_objeto == 'medicamento':
            objetos = Medicamento.objects.all()
            data = generate_medicamento_report(request, objetos)
            filename = 'reporte_medicamentos.pdf'
            report_title = "Lista de Medicametos"
            entity = 'Medicamentos'
        elif tipo_objeto == 'medicfarma':
            objetos = FarmaciaMedicamento.objects.all()
            farmacia_nombre, data = generate_medicfarma_report(request, objetos)
            filename = 'reporte_medicfarma.pdf'
            report_title = f"Lista de Medicamentos en la Farmacia: {farmacia_nombre}"
            entity = f'Farmacia {farmacia_nombre}'
        elif tipo_objeto == 'entrada':  
            objetos = Entrada.objects.all()
            farmacia_nombre, data = generate_entrada_report(request, objetos)
            filename = 'reporte_entradas.pdf'
            report_title = f"Lista de Entradas en la Farmacia: {farmacia_nombre}"
            entity = f'Entradas en {farmacia_nombre}'
        elif tipo_objeto == 'salida':
            objetos = Salida.objects.all()
            farmacia_nombre, data = generate_salida_report(request, objetos)
            filename = 'reporte_salidas.pdf'
            report_title = f"Lista de Salidas en la Farmacia: {farmacia_nombre}"
            entity = f'Salidas en {farmacia_nombre}'
        else:
            return JsonResponse({'error': 'Tipo de objeto no válido'}, status=400)

        if not data or len(data) <= 1:
            return JsonResponse({'error': 'No se encontraron datos para generar el reporte.'}, status=400)

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), topMargin=125)
        elements = []

        # Añadir el título
        styles = getSampleStyleSheet()
        title_style = styles['Title']
        title = Paragraph(report_title, title_style)
        elements.append(title)
        elements.append(Spacer(1, 12))  # Añadir espacio entre el título y la tabla

        table = Table(data)
        table.setStyle(style_table)
        elements.append(table)
        user = request.user.username
        doc.build(elements, onFirstPage=lambda c, d: header_footer(c, d, user, entity),
          onLaterPages=lambda c, d: header_footer(c, d, user, entity))
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=filename)

    return JsonResponse({'error': 'Método no permitido'}, status=405)


##############################################################################################################################
################################################    ALERTAS    ##################################################################


def crearTareaNotificacion(request):
    if request.method == 'GET':
        id_medicamento = request.GET.get('medicamento')
        medicamento = Medicamento.objects.get(id_medic=id_medicamento)
        tarea = TareaExistencia(id_medic=medicamento, id_user=request.user)
        try:
            tarea.save()
            return JsonResponse({'task': 'creada'}, status=200)
        except Exception as e:
            print(e)
            return JsonResponse({'error': 'Invalid request'}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['especialista'])
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@require_POST
def editarUbicacionFarmacia(request, uuid):
    farmacia = Farmacia.objects.get(id_farma=uuid)
    latitud = request.POST.get('latitud')
    longitud = request.POST.get('longitud')
    flat = float(latitud)
    flon = float(longitud)
    print(flat)
    print(flon)
    if farmacia is not None and latitud is not None and longitud is not None:
        farmacia.ubicacion = Point(flon, flat)
        farmacia.save()
        return JsonResponse({'success': True}, status=200)
    else:
        JsonResponse({'error': 'Invalid request'}, status=400)


def obtenerNotificaciones(request):
    data = [
        {
            'id_notificacion': "test",
            'mensaje': "Mensaje prueba",
            'fecha': "fecha prueba"
        },
        {
            'id_notificacion': "test 2",
            'mensaje': "Mensaje prueba",
            'fecha': "fecha prueba 2"
        }
    ]
    return JsonResponse({'notificaciones': data}, safe=False)
    #if request.user.is_authenticated:
    #    notificaciones = Notificacion.objects.filter(user=request.user, leido=False).order_by('-fecha')
    #    data = [{'id_notificacion': n.id, 'mensaje': n.mensaje, 'fecha': n.fecha.strftime('%Y-%m-%d %H:%M:%S')} for n in notificaciones]
    #    return JsonResponse({'notificaciones': data}, safe=False)
    #else:
    #    return JsonResponse({'error': 'No autorizado'}, status=403)


@csrf_exempt
def marcarNotificacionLeida(request):
    if request.method == 'POST':
        notificacion_id = request.POST.get('id')
        if not notificacion_id:
            return JsonResponse({'status': 'error', 'message': 'ID de notificación no proporcionado'}, status=400)
        
        try:
            notificacion_id = int(notificacion_id)  # Asegurarse de que el ID sea un número entero
        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'ID de notificación no válido'}, status=400)

        try:
            notificacion = Notificacion.objects.get(id=notificacion_id)
            notificacion.leido = True
            notificacion.save()
            return JsonResponse({'status': 'success'}, status=200)
        except Notificacion.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Notificación no encontrada'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)


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
    labels = ['clientes', 'farmacéuticos', 'admin']
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

 # Agregar importaciones necesarias al inicio del archivo
from django.utils.timezone import now
from django.db.models.functions import TruncDay, TruncMonth
from django.db.models import Sum, F, FloatField    
from django.db.models.functions import Coalesce   
import datetime 

@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['farmacéuticos'])
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def ventaGraficaFarmacia(request, farmacia_id):
    total_existencias = FarmaciaMedicamento.objects.filter(id_farma=farmacia_id)
    top_mas_vendidos = []
    for item in total_existencias:
        resultado = Salida.objects.filter(id_farmaciaMedicamento=item.pk).aggregate(total_cantidad=Coalesce(Sum('cantidad'), 0))['total_cantidad']
        print(resultado)
        # Calcular el porcentaje, evitando la división por cero
        if item.existencia + resultado > 0:
            porciento = (resultado / (item.existencia + resultado)) * 100
        else:
            porciento = 0

        top_mas_vendidos.append(
            {
                'medicamento': item.id_medic.nombre,
                'existencia': item.existencia,
                'vendidos': resultado,
                'porciento': f"{porciento}%"  # Formatear como string con un signo de porcentaje
            }
        )

    top_mas_vendidos.sort(key=lambda x: x['vendidos'], reverse=True)  # Añadir reverse=True para ordenar de mayor a menor


    # Filtrar las ventas del mes actual
    ventas_mes = Salida.objects.filter(
        fecha_movimiento__year=now().year,
        fecha_movimiento__month=now().month,
        id_farmaciaMedicamento__id_farma = farmacia_id
    ).annotate(
        dia=TruncDay('fecha_movimiento')).values('dia').annotate(total=Sum('cantidad')).order_by('dia')

      # Preparar los datos para el gráfico
    fechas = [venta['dia'].strftime('%Y-%m-%d') for venta in ventas_mes]
    cantidades = [venta['total'] for venta in ventas_mes]
    
    # Pasar los datos al template
    contexto = {
        'fechas': fechas,
        'cantidades': cantidades,
        'top_vendidos': top_mas_vendidos[:5]
    }

    print(contexto)

    return render(request, "visualizar_charts.html", contexto)

@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['farmacéuticos'])
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def ventaGraficaFarmaciaV2(request, farmacia_id):
    
    contexto24h = graficos24h(farmacia_id)
    contextoGeneral = graficosGeneral(farmacia_id)
    # Pasar los datos al template
   
    contexto = {
        'contexto_24h': contexto24h,
        'contexto_general': contextoGeneral
    }

    print(contexto)
    return render(request, "visualizar_charts.html", contexto)

def graficos24h(farmacia_id):
    total_existencias = FarmaciaMedicamento.objects.filter(id_farma=farmacia_id)
    top_mas_vendidos = []
    ahora = timezone.now()
    # Calcular la fecha y hora de hace 24 horas
    hace_24_horas = ahora - timedelta(hours=24)
    # Filtrar las ventas de las últimas 24 horas
    ventas_ultimas_24_horas = Salida.objects.filter(
        fecha_movimiento__gte=hace_24_horas,
        id_farmaciaMedicamento__id_farma=farmacia_id
    ).annotate(
        total_por_salida=Sum(F('cantidad') * F('id_farmaciaMedicamento__id_medic__precio_unidad'), output_field=FloatField())
    )
    # Calcular el total recaudado en las últimas 24 horas
    total_recaudado_24_horas = ventas_ultimas_24_horas.aggregate(
        total_recaudado=Coalesce(Sum('total_por_salida', output_field=FloatField()), 0.0)
    )['total_recaudado']
    total_de_entradas = 0

    for item in total_existencias:
        resultado = Salida.objects.filter(id_farmaciaMedicamento=item.pk).aggregate(total_cantidad=Coalesce(Sum('cantidad'), 0))['total_cantidad']
        porciento = (resultado / (item.existencia + resultado)) * 100 if item.existencia + resultado > 0 else 0
        total_de_entradas = total_de_entradas + (resultado+item.existencia)
        top_mas_vendidos.append({
            'medicamento': item.id_medic.nombre,
            'existencia': item.existencia,
            'vendidos': resultado,
            'porciento': f"{porciento}%"
        })

    top_mas_vendidos.sort(key=lambda x: x['vendidos'], reverse=True)

    # Filtrar las ventas del mes actual y calcular el total recaudado
    ventas_mes = Salida.objects.filter(
        fecha_movimiento__year=now().year,
        fecha_movimiento__month=now().month,
        id_farmaciaMedicamento__id_farma=farmacia_id
    ).annotate(
        dia=TruncDay('fecha_movimiento'),
        total_por_salida=Sum(F('cantidad') * F('id_farmaciaMedicamento__id_medic__precio_unidad'), output_field=FloatField()),
        total=F('cantidad')
    ).values('dia', 'total_por_salida', 'total').order_by('dia')

    total_recaudado_mes = ventas_mes.aggregate(total_recaudado=Coalesce(Sum('total_por_salida', output_field=FloatField()), 0.0))['total_recaudado']

   
    # Preparar los datos para el gráfico
    ventas_por_dia = ventas_mes.values('dia').annotate(total_vendido=Sum('cantidad')).order_by('dia')
    fechas = [venta['dia'].strftime('%Y-%m-%d') for venta in ventas_por_dia]
    cantidades = [venta['total_vendido'] for venta in ventas_por_dia]
    
    # Pasar los datos al template
    contexto = {
        'fechas': fechas,
        'cantidades': cantidades,
        'top_vendidos': top_mas_vendidos[:5],
        'total_recaudado': total_recaudado_mes,
        'total_unidades': sum(cantidades),
        'total_24': total_recaudado_24_horas,
        'total_entradas': total_de_entradas
    }
    
    return contexto

def graficosGeneral(farmacia_id):
    # Obtener el año actual
    year = now().year

    # Crear una lista de todos los meses del año actual
    meses_del_ano = [datetime.date(year, month, 1) for month in range(1, 13)]

    # Filtrar las ventas del año actual y calcular el total recaudado por mes
    ventas_ano = Salida.objects.filter(
        fecha_movimiento__year=year,
        id_farmaciaMedicamento__id_farma=farmacia_id
    ).annotate(
        mes=TruncMonth('fecha_movimiento'),
        total_por_salida=F('cantidad') * F('id_farmaciaMedicamento__id_medic__precio_unidad')
    ).values('mes').annotate(total_mes=Sum('total_por_salida')).order_by('mes')

    # Convertir QuerySet a diccionario para acceso rápido
    ventas_por_mes = {venta['mes']: venta['total_mes'] for venta in ventas_ano}

    # Preparar los datos para el gráfico, asegurándose de que los meses sin ventas tengan un valor de 0
    totales_mes = [ventas_por_mes.get(mes, 0) for mes in meses_del_ano]

    # Formatear los meses para las etiquetas del gráfico
    meses = [mes.strftime('%Y-%m') for mes in meses_del_ano]

    # Pasar los datos al template
    contexto = {
        'meses': meses,
        'totales_mes': totales_mes,
    }
    
    return contexto
