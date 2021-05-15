from django.shortcuts import render, redirect
from . import forms
from .models import Accounts
import logging
# Create your views here.
logging.basicConfig(level=logging.DEBUG)


def register(request):
    if request.method == 'POST':
        registerForm = forms.RegisterForm(request.POST)

        if registerForm.is_valid():
            first_name = registerForm.cleaned_data['first_name']
            last_name = registerForm.cleaned_data['last_name']
            username = registerForm.cleaned_data['username']
            email = registerForm.cleaned_data['email']
            phone_number = registerForm.cleaned_data['phone_number']
            password = registerForm.cleaned_data['password']
            user = Accounts.objects.create_user(
                first_name=first_name, last_name=last_name, username=username, email=email, phone_number=phone_number, password=password)
            user.save()
            return redirect('home')
    else:
        registerForm = forms.RegisterForm()

    return render(request, 'account-form/register.html', context={
        'forms': registerForm
    })


def login(request):
    return render(request, 'account-form/signin.html')
