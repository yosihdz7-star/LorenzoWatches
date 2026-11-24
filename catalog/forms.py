from django import forms
from .models import ContactMessage, Order


class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Tu nombre'}),
            'email': forms.EmailInput(attrs={'placeholder': 'tu@correo.com'}),
            'message': forms.Textarea(attrs={'placeholder': '¿En qué podemos ayudarte?', 'rows': 5}),
        }


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'customer_name', 'email', 'phone', 'address', 'city',
            'state', 'postal_code', 'payment_method',
        ]
        labels = {
            'customer_name': 'Nombre completo',
            'email': 'Correo electrónico',
            'phone': 'Teléfono',
            'address': 'Dirección de envío',
            'city': 'Ciudad',
            'state': 'Estado',
            'postal_code': 'Código postal',
            'payment_method': 'Forma de pago',
        }
        widgets = {
            'customer_name': forms.TextInput(attrs={'placeholder': 'Tu nombre completo'}),
            'email': forms.EmailInput(attrs={'placeholder': 'tu@correo.com'}),
            'phone': forms.TextInput(attrs={'placeholder': '55 1234 5678'}),
            'address': forms.TextInput(attrs={'placeholder': 'Calle, número y colonia'}),
            'city': forms.TextInput(attrs={'placeholder': 'Ciudad'}),
            'state': forms.TextInput(attrs={'placeholder': 'Estado'}),
            'postal_code': forms.TextInput(attrs={'placeholder': '00000'}),
        }
