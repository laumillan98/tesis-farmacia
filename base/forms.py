from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm, PasswordResetForm, UserChangeForm
from .models import CustomUser, FarmaUser, Farmacia, Municipio, Provincia, TipoFarmacia, TurnoFarmacia
from django.contrib.auth import get_user_model
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox
from django.core.validators import RegexValidator


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(help_text='Escriba una dirección de correo válida por favor', required=True)
    first_name = forms.CharField(validators=[RegexValidator('[A-Za-z ]{3,50}', message='Nombre no válido')], label="Nombre", required=True)
    last_name = forms.CharField(validators=[RegexValidator('[A-Za-z ]{3,50}', message='Apellido no válido')], label="Apellidos", required=True)

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
    first_name = forms.CharField(validators=[RegexValidator('[A-Za-z ]{3,50}', message='Nombre no válido')], label="Nombre", required=True)
    last_name = forms.CharField(validators=[RegexValidator('[A-Za-z ]{3,50}', message='Apellido no válido')], label="Apellidos", required=True)
    farma_name = forms.ModelChoiceField(queryset=Farmacia.objects.exclude(farmauser__isnull=False), label="Farmacia Asociada") 

    class Meta:
        model = FarmaUser
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'farma_name']

    def save(self, commit=True):
        user = super(FarmaUserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()

        return user    
    
    def clean_email(self):
        print(type(self.cleaned_data))
        email = self.cleaned_data.get('email')

        if FarmaUser.objects.filter(email=email).exists():
            raise forms.ValidationError("El correo introducido ya está en uso")

        with open ("base/static/txt/disposable_email_providers.txt", 'r') as f:
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

    def clean_farma_name(self):
        farma = self.cleaned_data.get('farma_name')
        if farma:
            self.instance.farma = farma
        return farma


class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)

    username = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control'}),
        label="Nombre de usuario o Correo")

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
    #email = forms.EmailField(required=True)
    first_name = forms.CharField(validators=[RegexValidator('[A-Za-z ]{3,50}', message='Nombre no válido')], label="Nombre", required=True)
    last_name = forms.CharField(validators=[RegexValidator('[A-Za-z ]{3,50}', message='Apellido no válido')], label="Apellidos", required=True)

    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'description']  
    

class UserUpdateForm(UserChangeForm):
    first_name = forms.CharField(validators=[RegexValidator('[A-Za-z ]{3,50}', message='Nombre no válido')], label="Nombre", required=True)
    last_name = forms.CharField(validators=[RegexValidator('[A-Za-z ]{3,50}', message='Apellido no válido')], label="Apellidos", required=True)
    
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name')


class FarmaUserUpdateForm(UserChangeForm):
    first_name = forms.CharField(validators=[RegexValidator('[A-Za-z ]{3,50}', message='Nombre no válido')], label="Nombre", required=True)
    last_name = forms.CharField(validators=[RegexValidator('[A-Za-z ]{3,50}', message='Apellido no válido')], label="Apellidos", required=True)
    
    class Meta:
        model = FarmaUser
        fields = ('first_name', 'last_name', 'id_farma')


class FarmaUpdateForm(forms.ModelForm):
    nombre = forms.CharField(validators=[RegexValidator('[A-Za-z ]{3,50}', message='Nombre no válido')], label="Nombre", required=True)
    direccion = forms.CharField(validators=[RegexValidator('[A-Za-z ]{3,50}', message='Dirección no válida')], label="Dirección", required=True)
    telefono = forms.CharField(label="Teléfono", required=True)
    
    class Meta:
        model = Farmacia
        fields = ('nombre', 'direccion', 'telefono', 'id_turno', 'id_tipo', 'id_munic')


class TipoFarmaciaUpdateForm(forms.ModelForm):
    nombre = forms.CharField(validators=[RegexValidator('[A-Za-z ]{3,50}', message='Nombre no válido')], label="Nombre", required=True)

    class Meta:
        model = TipoFarmacia
        fields = ('nombre',)


class TurnoFarmaciaUpdateForm(forms.ModelForm):
    nombre = forms.CharField(validators=[RegexValidator('[A-Za-z ]{3,50}', message='Nombre no válido')], label="Nombre", required=True)

    class Meta:
        model = TurnoFarmacia
        fields = ('nombre',)


class MunicUpdateForm(forms.ModelForm):
    nombre = forms.CharField(validators=[RegexValidator('[A-Za-z ]{3,50}', message='Nombre no válido')], label="Nombre", required=True)
  
    class Meta:
        model = Municipio
        fields = ('nombre', 'id_prov')


class ProvUpdateForm(forms.ModelForm):
    nombre = forms.CharField(validators=[RegexValidator('[A-Za-z ]{3,50}', message='Nombre no válido')], label="Nombre", required=True)

    class Meta:
        model = Provincia
        fields = ('nombre',)

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
