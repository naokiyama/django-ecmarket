from django import forms
from .models import Accounts


class RegisterForm(forms.ModelForm):

    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Eenter Password',
        'class': 'form-control'
    }))

    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Eenter Password',
        'class': 'form-control'
    }))

    class Meta:
        model = Accounts
        fields = ['first_name', 'last_name', 'username',
                  'email', 'phone_number', 'password']

    def clean(self):
        cleaned_data = super(RegisterForm, self).clean()
        password_data = cleaned_data.get('password')
        confirm_password_data = cleaned_data.get('confirm_password')
        if password_data != confirm_password_data:
            raise forms.ValidationError(
                'password does not match'
            )

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Last Name'
        self.fields['username'].widget.attrs['placeholder'] = 'Username'
        self.fields['email'].widget.attrs['placeholder'] = 'Email'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Phone Number'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
