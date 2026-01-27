from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django import forms
from utils.validator import strong_password


class RegisterForm(forms.ModelForm):

    username = forms.CharField(
        label='Username',
        error_messages= {
            'required': 'Este campo é obrigatório',
            'min_length': 'Username precisa ter ao menos 4 caracteres',
            'max_length': 'Username precisa ter menos de 150 caracteres',
        },
            min_length=4, max_length=150
    )

    email = forms.EmailField(
        error_messages={'required': 'Este campo é obrigatório'},
        label='E-mail',
        help_text='Ex.:exmplo@email.com',
    )

    password = forms.CharField(
    
        widget=forms.PasswordInput(),
        error_messages={
            'required': 'Password must not be empty'
        },
        help_text=(
            'A senha precisa ter letras maiusculas e minusculas, numeros e simbolos'
        ),
        label='Password',
        validators=[strong_password]
    )

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password',
        ]


    def clean_email(self):
        email = self.cleaned_data.get('email', '')
        exists = User.objects.filter(email=email).exists()

        if exists:
            raise ValidationError(
                'Este e-mail já está em uso', code='invalid',
            )

        return email