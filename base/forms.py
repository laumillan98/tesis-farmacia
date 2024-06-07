from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm, PasswordResetForm, UserChangeForm
from .models import CustomUser, FarmaUser, Farmacia, Municipio, Provincia, TipoFarmacia, TurnoFarmacia, Medicamento, RestriccionMedicamento, ClasificacionMedicamento, FormatoMedicamento, Entrada, Salida
from .widgets import BooleanCheckbox
from django.contrib.auth import get_user_model
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from django.core.validators import RegexValidator, MinValueValidator
from django.core.exceptions import ValidationError
from datetime import date, timedelta


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(help_text='Escriba una dirección de correo válida por favor', required=True)
    first_name = forms.CharField(validators=[RegexValidator(regex='^[A-Za-záéíóúÁÉÍÓÚüÜ\s]{3,50}$', message='Nombre no válido')], label="Nombre", required=True)
    last_name = forms.CharField(validators=[RegexValidator(regex='^[A-Za-záéíóúÁÉÍÓÚüÜ\s]{3,50}$', message='Apellido no válido')], label="Apellidos", required=True)

    class Meta:
        model = get_user_model()
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super(CustomUserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()

        return user    
    
    def clean_email(self):
        print(type(self.cleaned_data))
        email = self.cleaned_data.get('email')

        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("El correo introducido ya está en uso")

        with open ("static/txt/disposable_email_providers.txt", 'r') as f:
            blacklist = f.read().splitlines() 

        for disposable_email in blacklist:
            if disposable_email in email:
                raise forms.ValidationError("Dirección de correo SPAM")
        return email
    
    def clean_pass(self):
        cleaned_data = super().clean()

        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')

        if p1 != p2:
            raise forms.ValidationError("Tus contraseñas no cinciden")
        return cleaned_data
    

class FarmaUserCreationForm(UserCreationForm):
    email = forms.EmailField(help_text='Escriba una dirección de correo válida por favor', required=True)
    first_name = forms.CharField(validators=[RegexValidator(regex='^[A-Za-záéíóúÁÉÍÓÚüÜ\s]{3,50}$', message='Nombre no válido.')], label="Nombre", required=True)
    last_name = forms.CharField(validators=[RegexValidator(regex='^[A-Za-záéíóúÁÉÍÓÚüÜ\s]{3,50}$', message='Apellido no válido.')], label="Apellidos", required=True)
    id_farma = forms.ModelChoiceField(queryset=Farmacia.objects.exclude(farmauser__isnull=False), label="Farmacia Asociada") 

    class Meta:
        model = FarmaUser
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'id_farma']

    def save(self, commit=True):
        user = super(FarmaUserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
        return user    
    
    def clean_email(self):
        print(type(self.cleaned_data))
        email = self.cleaned_data.get('email')

        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("El correo introducido ya está en uso")

        with open ("static/txt/disposable_email_providers.txt", 'r') as f:
            blacklist = f.read().splitlines() 

        for disposable_email in blacklist:
            if disposable_email in email:
                raise forms.ValidationError("Dirección de correo SPAM")
        return email
    
    def clean_pass(self):
        cleaned_data = super().clean()

        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')

        if p1 != p2:
            raise forms.ValidationError("Tus contraseñas no cinciden")
        return cleaned_data    

    def clean_id_farma(self):
        id_farma = self.cleaned_data.get('id_farma')
        if id_farma:
            self.instance.id_farma = id_farma
        return id_farma
    

class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)

    username = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control'}),
        label="Nombre de usuario")

    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control'}),
        label="Contraseña")

    #captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())


class SetPasswordForm(SetPasswordForm):
    class Meta:
        model = get_user_model()
        fields = ['new_password1', 'new_password2']


class PasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(PasswordResetForm, self).__init__(*args, **kwargs)

    #captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())


class UserProfileForm(UserChangeForm):
    username = forms.CharField(max_length=20, validators=[RegexValidator(regex='^[A-Za-z0-9_]{3,150}$', message='Nombre de usuario no válido')], label="Nombre de usuario", required=True)
    first_name = forms.CharField(validators=[RegexValidator(regex='^[A-Za-záéíóúÁÉÍÓÚüÜ\s]{3,50}$', message='Nombre no válido')], label="Nombre", required=True)
    last_name = forms.CharField(validators=[RegexValidator(regex='^[A-Za-záéíóúÁÉÍÓÚüÜ\s]{3,50}$', message='Apellido no válido')], label="Apellidos", required=True)
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}), label="Descripción", required=False)

    class Meta:
        model = get_user_model()
        fields = ['username', 'first_name', 'last_name', 'description']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if get_user_model().objects.filter(username=username).exists() and self.instance.username != username:
            raise forms.ValidationError("El nombre de usuario ya está en uso")
        return username
    

class UserUpdateForm(UserChangeForm):
    first_name = forms.CharField(validators=[RegexValidator(regex='^[A-Za-záéíóúÁÉÍÓÚüÜ\s]{3,50}$', message='Nombre no válido')], label="Nombre", required=True)
    last_name = forms.CharField(validators=[RegexValidator(regex='^[A-Za-záéíóúÁÉÍÓÚüÜ\s]{3,50}$', message='Apellido no válido')], label="Apellidos", required=True)
    description = forms.CharField(widget=forms.Textarea, label="Descripción", required=False)
    email = forms.EmailField(help_text='Escriba una dirección de correo válida por favor', required=True)

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'description', 'email')


class FarmaUserUpdateForm(UserChangeForm):
    first_name = forms.CharField(validators=[RegexValidator(regex='^[A-Za-záéíóúÁÉÍÓÚüÜ\s]{3,50}$', message='Nombre no válido')], label="Nombre", required=True)
    last_name = forms.CharField(validators=[RegexValidator(regex='^[A-Za-záéíóúÁÉÍÓÚüÜ\s]{3,50}$', message='Apellido no válido')], label="Apellidos", required=True)
    description = forms.CharField(widget=forms.Textarea, label="Descripción", required=False)
    email = forms.EmailField(help_text='Escriba una dirección de correo válida por favor', required=True)

    class Meta:
        model = FarmaUser
        fields = ('first_name', 'last_name', 'id_farma', 'description', 'email')


class FarmaUpdateForm(forms.ModelForm):
    nombre = forms.CharField(validators=[RegexValidator('[A-Za-z ]{3,50}', message='Nombre no válido')], label="Nombre", required=True)
    direccion = forms.CharField(validators=[RegexValidator('[A-Za-z ]{3,50}', message='Dirección no válida')], label="Dirección", required=True)
    telefono = forms.CharField(validators=[RegexValidator(regex=r'^7\d{7}$', message='El teléfono debe comenzar con 7 y tener exactamente 8 dígitos.')], label="Teléfono", required=True)
    
    class Meta:
        model = Farmacia
        fields = ('nombre', 'direccion', 'telefono', 'id_turno', 'id_tipo', 'id_munic')


class TipoFarmaciaUpdateForm(forms.ModelForm):
    nombre = forms.CharField(validators=[RegexValidator(regex='^[A-Za-záéíóúÁÉÍÓÚüÜ\s]{3,50}$', message='Nombre no válido')], label="Nombre", required=True)

    class Meta:
        model = TipoFarmacia
        fields = ('nombre',)

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if TipoFarmacia.objects.filter(nombre=nombre).exists():
            raise ValidationError('Este nombre ya existe.')
        return nombre


class TurnoFarmaciaUpdateForm(forms.ModelForm):
    nombre = forms.CharField(validators=[RegexValidator(regex='^[A-Za-záéíóúÁÉÍÓÚüÜ\s]{3,50}$', message='Nombre no válido.')], label="Nombre", required=True)

    class Meta:
        model = TurnoFarmacia
        fields = ('nombre',)

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if TurnoFarmacia.objects.filter(nombre=nombre).exists():
            raise ValidationError('Este nombre ya existe.')
        return nombre


class MunicUpdateForm(forms.ModelForm):
    nombre = forms.CharField(validators=[RegexValidator(regex='^[A-Za-záéíóúÁÉÍÓÚüÜ\s]{3,50}$', message='Nombre no válido')], label="Nombre", required=True)
  
    class Meta:
        model = Municipio
        fields = ('nombre', 'id_prov')

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if Municipio.objects.filter(nombre=nombre).exists():
            raise ValidationError('Este nombre ya existe.')
        return nombre


class ProvUpdateForm(forms.ModelForm):
    nombre = forms.CharField(validators=[RegexValidator(regex='^[A-Za-záéíóúÁÉÍÓÚüÜ\s]{3,50}$', message='Nombre no válido')], label="Nombre", required=True)

    class Meta:
        model = Provincia
        fields = ('nombre',)

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if Provincia.objects.filter(nombre=nombre).exists():
            raise ValidationError('Este nombre ya existe.')
        return nombre


class MedicUpdateForm(forms.ModelForm):
    nombre = forms.CharField(validators=[RegexValidator(regex='^[A-Za-záéíóúÁÉÍÓÚüÜ\s]{3,50}$', message='Nombre no válido')], label="Nombre", required=True)
    cant_max = forms.IntegerField(validators=[MinValueValidator(1, message="La cantidad debe ser mayor que cero.")], required=True, label="Cantidad Máxima")
    precio_unidad = forms.FloatField(validators=[MinValueValidator(1.00, message="El precio por unidad debe ser mayor que cero.")], required=True, label="Precio por Unidad")
    origen_natural = forms.BooleanField(widget=BooleanCheckbox, required=False, label="Origen Natural")
    id_restriccion = forms.ModelChoiceField(queryset=RestriccionMedicamento.objects.all(), required=True, label="Restricción")
    id_clasificacion = forms.ModelChoiceField(queryset=ClasificacionMedicamento.objects.all(), required=True, label="Clasificación")
    id_formato = forms.ModelChoiceField(queryset=FormatoMedicamento.objects.all(), required=True, label="Formato")

    class Meta:
        model = Medicamento
        fields = ('nombre', 'description', 'cant_max', 'precio_unidad', 'origen_natural', 'id_restriccion', 'id_clasificacion', 'id_formato')

    def clean(self):
        cleaned_data = super().clean()
        nombre = cleaned_data.get('nombre')
        id_formato = cleaned_data.get('id_formato')

        if Medicamento.objects.filter(nombre=nombre, id_formato=id_formato).exists():
            raise forms.ValidationError("Ya existe un medicamento con este nombre y formato.")

        return cleaned_data


class RestriccionMedicamentoUpdateForm(forms.ModelForm):
    nombre = forms.CharField(validators=[RegexValidator(regex='^[A-Za-záéíóúÁÉÍÓÚüÜ\s]{3,50}$', message='Nombre no válido')], label="Nombre", required=True)
    
    class Meta:
        model = RestriccionMedicamento
        fields = ('nombre',)

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if RestriccionMedicamento.objects.filter(nombre=nombre).exists():
            raise ValidationError('Este nombre ya existe.')
        return nombre


class ClasificacionMedicamentoUpdateForm(forms.ModelForm):
    nombre = forms.CharField(validators=[RegexValidator(regex='^[A-Za-záéíóúÁÉÍÓÚüÜ\s]{3,50}$', message='Nombre no válido')], label="Nombre", required=True)
    
    class Meta:
        model = ClasificacionMedicamento
        fields = ('nombre',)

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if ClasificacionMedicamento.objects.filter(nombre=nombre).exists():
            raise ValidationError('Este nombre ya existe.')
        return nombre


class FormatoMedicamentoUpdateForm(forms.ModelForm):
    nombre = forms.CharField(validators=[RegexValidator(regex='^[A-Za-záéíóúÁÉÍÓÚüÜ\s]{3,50}$', message='Nombre no válido')], label="Nombre", required=True)
    
    class Meta:
        model = FormatoMedicamento
        fields = ('nombre',)

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if FormatoMedicamento.objects.filter(nombre=nombre).exists():
            raise ValidationError('Este nombre ya existe.')
        return nombre
    

class EntradaMedicamentoCreateForm(forms.ModelForm):
    factura = forms.CharField(validators=[RegexValidator(regex='^[A-Za-z0-9]{3,20}$', message='Factura no válida, solo se permiten números y letras')], label="Factura", required=True)
    numero_lote = forms.CharField(validators=[RegexValidator(regex='^[A-Za-z0-9]{3,20}$', message='Número de lote no válido, solo se permiten números y letras')], label="Número de Lote", required=True)
    cantidad = forms.IntegerField(validators=[MinValueValidator(1, message="La cantidad debe ser mayor que cero.")], required=True, label="Cantidad")
    fecha_elaboracion = forms.DateField(required=True, label="Fecha de Elaboración", widget=forms.DateInput(attrs={'type': 'date'}))
    fecha_vencimiento = forms.DateField(required=True, label="Fecha de Vencimiento", widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Entrada
        fields = ['id_farmaciaMedicamento', 'factura', 'numero_lote', 'cantidad', 'fecha_elaboracion', 'fecha_vencimiento']

    def clean_fecha_elaboracion(self):
        fecha_elaboracion = self.cleaned_data.get('fecha_elaboracion')
        if fecha_elaboracion and fecha_elaboracion > date.today():
            raise ValidationError("La fecha de elaboración no puede ser posterior a la fecha actual.")
        return fecha_elaboracion

    def clean_fecha_vencimiento(self):
        fecha_vencimiento = self.cleaned_data.get('fecha_vencimiento')
        if fecha_vencimiento and fecha_vencimiento <= date.today():
            raise ValidationError("La fecha de vencimiento debe ser mayor que la fecha actual.")
        return fecha_vencimiento

    def clean(self):
        cleaned_data = super().clean()
        fecha_elaboracion = cleaned_data.get('fecha_elaboracion')
        fecha_vencimiento = cleaned_data.get('fecha_vencimiento')

        if fecha_elaboracion and fecha_vencimiento:
            if fecha_elaboracion > fecha_vencimiento:
                raise ValidationError("La fecha de elaboración no puede ser posterior a la fecha de vencimiento.")
            if (fecha_vencimiento - fecha_elaboracion).days < 365:
                raise ValidationError("Debe haber al menos un año entre la fecha de elaboración y la fecha de vencimiento.")
        return cleaned_data


class FarmaciaAdminForm(forms.ModelForm):
    latitud = forms.FloatField(required=False)
    longitud = forms.FloatField(required=False)

    class Meta:
        model = Farmacia
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(FarmaciaAdminForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.ubicacion:
            self.fields['latitud'].initial = self.instance.ubicacion.y
            self.fields['longitud'].initial = self.instance.ubicacion.x


