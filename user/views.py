from django.shortcuts import render
from django.urls import reverse
from .forms.register_form import RegisterForm


def register_view(request):
        register_form_data = request.session.get('register_form_data', None)
        form = RegisterForm(register_form_data)
        return render(request, 'user/pages/register.html', {
                'form' : form,
                'form_action' : reverse('user:register_create')
    })