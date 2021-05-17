from django.http.response import HttpResponseBase
from django.shortcuts import render, redirect
from . import forms
from .models import Accounts
from django.contrib import auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django.http import HttpResponse
# verification email

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

import logging

import accounts
# Create your views here.
logging.basicConfig(level=logging.DEBUG)


def register(request):
    logging.debug(request.POST)
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
            # user login　有効にする
            current_site = get_current_site(request)
            logging.debug(current_site)
            mail_subject = 'Please activate your account'
            message = render_to_string('account-form/account_verification_mail.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            logging.debug('token:{}'.format(
                default_token_generator.make_token(user)))
            logging.debug('encode:{}'.format(
                urlsafe_base64_encode(force_bytes(user.pk))))
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            # messages.success(request, 'Thank you for registering with us. we have sent you a verification email to your email address [')
            return redirect('accounts:login')
    else:
        registerForm = forms.RegisterForm()

    return render(request, 'account-form/register.html', context={
        'forms': registerForm
    })


def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        # 認証が通らない原因はis_activeがfalseになっているため
        user = auth.authenticate(email=email, password=password)
        logging.debug('User who have successfully logged in:{}'.format(user))
        if user is not None:
            auth.login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalide login credential')
            return redirect('accounts:login')

    return render(request, 'account-form/signin.html')


@login_required(login_url='accounts:login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You are log out')
    return redirect('accounts:login')


def activate(request, uidb64, token):

    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Accounts._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Accounts.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations Your account is activated')
        return redirect('accounts:login')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('accounts:register')


@ login_required(login_url='accounts:dashboard')
def dashboard(request):
    return render(request, 'account-form/dashboard.html')


def forgotPassword(request):
    if request.method == 'POST':
        logging.debug('reqeust:{}'.format(request))
        email = request.POST['email']
        if Accounts.objects.filter(email__exact=email).exists():
            user = Accounts.objects.get(email__exact=email)
            logging.debug('user SQLStatement:{}'.format(user))
            current_site = get_current_site(request)
            subject = 'Change your password'
            message = render_to_string('account-form/password_reset_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(subject, message, to=[to_email])
            send_email.send()

            messages.success(
                request, 'Password reset email has been sent to your email adress')
            return redirect('accounts:login')
        else:
            messages.error(request, 'Your email address is not registered')
            return redirect('accounts:forgotPassword')
    return render(request, 'account-form/forgot-password.html')


def resetPasswordValidate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Accounts._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Accounts.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect('accounts:resetPassword')
    else:
        messages.error(request, 'Account does not exist')
        return redirect('accounts:login')


def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password != confirm_password:
            messages.error(request, 'Your Password does not match')
            return redirect('account:resetPassword')
        else:
            uid = request.session.get('uid')
            user = Accounts.objects.get(pk=uid)
            if user:
                user.set_password(password)
                user.save()
                messages.success(request, 'Password change is complete')
                return redirect('accounts:login')
    return render(request, 'account-form/reset-password.html')
