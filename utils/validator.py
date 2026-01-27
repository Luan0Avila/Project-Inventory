import re
from django.core.exceptions import ValidationError

def strong_password(password):
    regex = re.compile(
        r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&]).{8,}$'
    )

    if not regex.match(password):
        raise ValidationError(
            'A senha deve conter pelo menos uma letra maiúscula, '
            'uma letra minúscula, um número e um caractere especial. '
            'E ter pelo menos 8 caracteres.',
            code='invalid'
        )