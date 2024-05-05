from os import name
from typing import Protocol
from django.http.response import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import CustomUser, Medicamento, TipoMedicamento, Farmacia, FarmaUser, FarmaciaMedicamento, TipoFarmacia, TurnoFarmacia, Municipio, Provincia
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.contrib.auth.models import Group, User
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.db.models.query_utils import Q
from django.core.validators import RegexValidator
from django.views.generic.edit import UpdateView
from django.views.decorators.http import require_POST

from .forms import CustomUserCreationForm, FarmaUserCreationForm, UserLoginForm, SetPasswordForm, PasswordResetForm, UserProfileForm, UserUpdateForm, FarmaUserUpdateForm, FarmaUpdateForm, MunicUpdateForm, ProvUpdateForm
from .decorators import usuarios_permitidos, unauthenticated_user
from .tokens import account_activation_token
from FirstApp.tasks import send_activation_email

# Create your views here.

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def inicio(request):
    return render(request, "Inicio.html")


@login_required(login_url='/acceder')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def administrator(request):
    return render(request, "index.html")


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
                    return redirect('/gestionar')  
                     
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
    users_list = []
    for index,user in enumerate(users):
        groups = user.groups.values_list('name', flat=True)  
        first_group = groups.first() if groups else None 
        user_data = {
            'index': index + 1,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username,
            'email': user.email,
            'first_group': first_group,
            'is_active': user.is_active,
            'is_superuser': user.is_superuser,
            'id': user.pk,
        }
        users_list.append(user_data)
    data = {'data': users_list}
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
        farma_user.farma = None
        farma_user.save()

    return JsonResponse({'status':'success'})


def activarUsuario(request, username):
    user = CustomUser.objects.get(username = username)   
    user.is_active = True
    user.save()
    return JsonResponse({'status':'success'})


# Funcion para obtener los datos del usuario que se va a editar
def obtenerUsuario(request, username):
    user = CustomUser.objects.get(username = username) 
    return JsonResponse({
        'username': user.username,
        'name': user.first_name,
        'lastname': user.last_name,
        })


@login_required(login_url='/acceder')
@require_POST
def editarUsuario(request):
    user = CustomUser.objects.get(username=request.POST.get('username'))
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
    farmacias_list = []
    for index,farma in enumerate(farmacias):
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
            'is_active': farma.is_active,
        }
        farmacias_list.append(farma_data)
    data = {'data': farmacias_list}
    return JsonResponse(data, safe=False)


@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['admin'])
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def registrarFarmacia(request):
    if request.method =='POST':
        return redirect('/')


# no funciona aun
def eliminarFarmacia(request, uuid):
    farma = Farmacia.objects.get(id_farma = uuid)   
    farma.is_active = False
    farma.save()
    return JsonResponse({'status':'success'})


def activarFarmacia(request, uuid):
    farma = Farmacia.objects.get(id_farma = uuid)   
    farma.is_active = True
    farma.save()
    return JsonResponse({'status':'success'})


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


# Completarrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr
def registrarMunicipio(request):
    return redirect('/')


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


# completarrrrrrrrrrrrrrr
@usuarios_permitidos(roles_permitidos=['admin'])
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def registrarProvincia(request):
    if request.method =='POST':
        return redirect('/')


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


@login_required(login_url='/acceder')
@usuarios_permitidos(roles_permitidos=['farmaceuticos'])
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def gestionarMedicamentos(request):
    print('Entro aqui 1')
    if request.user.is_authenticated:
        print('Entro aqui 2')

        farmaceutico = FarmaUser.objects.get(username=request.user.username)
        farmacia_del_farmaceutico = farmaceutico.farma
        
        farmacia_medicamento = FarmaciaMedicamento.objects.filter(
            id_farmacia=farmacia_del_farmaceutico.pk)
        lista_tipo_medicamentos = TipoMedicamento.objects.all()
        print(farmacia_medicamento)
        return render(
            request, "gestionar_medicamentos.html",
            {
                "farmacia": farmacia_del_farmaceutico,
                "medicamentos": farmacia_medicamento,
                "tipo_medicamento": lista_tipo_medicamentos
            }
        )
    else:
        return redirect('/acceder')


def registrarMedicamento(request):
    id_farmacia = request.POST['idFarmacia']
    nombre = request.POST['txtNombre']
    description = request.POST['txtDescription']
    cantidad = request.POST['numCantidad']
    precio = request.POST['txtPrecio']
    restriccion = request.POST['txtRestriccion']
    origen = request.POST['radioOrigen']

    farmacia = Farmacia.objects.get(pk=id_farmacia)
    tipo_medicamento = TipoMedicamento.objects.get(pk=restriccion)
    medicamento = Medicamento.objects.create(nombre=nombre, description=description,
                                             cant_max=cantidad, precio_unidad=precio, origen_natural=origen, id_restriccion=tipo_medicamento)
    farmacia_medicamento = FarmaciaMedicamento.objects.create(
        id_medic=medicamento, id_farmacia=farmacia, existencia=0)

    messages.success(request, 'Medicamento registrado :)')

    return redirect('/gestionar/')


@usuarios_permitidos(roles_permitidos=['farmaceuticos'])
def editarMedicamento(request, uuid):
    medicamento = Medicamento.objects.get(pk=uuid)
    lista_tipo_medicamentos = TipoMedicamento.objects.all()
    return render(request, "editar_medicamento.html", {"medicamento": medicamento, "tipo_medicamento": lista_tipo_medicamentos})


def edicionMedicamento(request):
    uuid = request.POST['uuid']
    nombre = request.POST['txtNombre']
    description = request.POST['txtDescription']
    cantidad = request.POST['numCantidad']
    precio = request.POST['txtPrecio']
    restriccion = request.POST['txtRestriccion']
    origen = request.POST['radioOrigen']

    tipo_medicamento = TipoMedicamento.objects.get(pk=restriccion)
    medicamento = Medicamento.objects.get(pk=uuid)
    medicamento.nombre = nombre
    medicamento.description = description
    medicamento.cant_max = cantidad
    medicamento.precio_unidad = precio
    medicamento.id_restriccion = tipo_medicamento
    medicamento.origen_natural = origen
    medicamento.save()

    messages.success(request, 'Medicamento actualizado :)')

    return redirect('/gestionar/')


def eliminarMedicamento(request, uuid):
    medicamento = Medicamento.objects.get(pk=uuid)
    medicamento.delete()

    messages.success(request, 'Medicamento elminado :)')

    return redirect('/gestionar')


def actualizarCantidad(request):
    if request.method == 'POST':
        farmacia = request.POST['farmacia']
        medicamento = request.POST['medicamento']
        cantidad = request.POST['cantidad']
        farmacia_medicamento = FarmaciaMedicamento.objects.get(
            id_medic=medicamento, id_farmacia=farmacia)
        farmacia_medicamento.existencia = cantidad
        farmacia_medicamento.save()
        return JsonResponse({'status': 'Cantidad actualizada'})
    return redirect('/gestionar/')


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
            payload.append(Disponibilidad(nombre=dis.id_farmacia.nombre,
                           telefono=dis.id_farmacia.telefono, existencia=dis.existencia).to_dict())
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

    def __init__(self, nombre, direccion, telefono, turno_corrido, id_tipo):
        self.nombre = nombre
        self.direccion = direccion
        self.telefono = telefono
        self.turno_corrido = turno_corrido
        self.id_tipo = id_tipo

    def to_dict(self):
        return {"nombre": self.nombre, "direccion": self.direccion, "telefono": self.telefono, "turno_corrido": self.turno_corrido, "id_tipo": self.id_tipo}


def buscarDisponibilidadFarmacia(request):
    terminoDeBusqueda = request.GET['termino']
    payload = []
    if terminoDeBusqueda:
        municipio = Municipio.objects.get(nombre=terminoDeBusqueda)
        disponibilidad = Farmacia.objects.filter(id_munic=municipio)
        for dis in disponibilidad:
            payload.append(DisponibilidadFarmacia(nombre=dis.nombre, direccion=dis.direccion,
                           telefono=dis.telefono, turno_corrido=dis.turno_corrido, id_tipo=dis.id_tipo.nombre).to_dict())
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




