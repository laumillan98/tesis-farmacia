from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm, PasswordResetForm, UserChangeForm
from .models import CustomUser, FarmaUser, Farmacia
from django.contrib.auth import get_user_model
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
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
    

class FarmaUserCreationForm(UserCreationForm):
    email = forms.EmailField(help_text='Escriba una dirección de correo válida por favor', required=True)
    first_name = forms.CharField(validators=[RegexValidator('[A-Za-z ]{3,50}', message='Nombre no válido')], label="Nombre", required=True)
    last_name = forms.CharField(validators=[RegexValidator('[A-Za-z ]{3,50}', message='Apellido no válido')], label="Apellidos", required=True)
    farma_name = forms.ModelChoiceField(queryset=Farmacia.objects.exclude(farmauser__isnull=False), label="Farmacia Asociada") 

    class Meta:
        model = FarmaUser
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2','farma_name']

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


class UserUpdateForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name')