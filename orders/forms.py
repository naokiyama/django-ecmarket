from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'phone_number', 'email',
                  'adress_line', 'city', 'state', 'country', 'postal_code', 'order_note']
