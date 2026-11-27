from django import forms

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'message']

        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Tu nombre',
                'class': 'form-control',
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'tu@correo.com',
                'class': 'form-control',
            }),
            'message': forms.Textarea(attrs={
                'placeholder': '¿En qué podemos ayudarte?',
                'rows': 5,
                'class': 'form-control',
            }),
        }


class CheckoutForm(forms.Form):
    customer_name = forms.CharField(
        label='Nombre completo',
        max_length=150,
        widget=forms.TextInput(attrs={
            'placeholder': 'Tu nombre completo',
            'class': 'form-control',
        }),
    )

    email = forms.EmailField(
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={
            'placeholder': 'tu@correo.com',
            'class': 'form-control',
        }),
    )

    phone = forms.CharField(
        label='Teléfono',
        max_length=30,
        widget=forms.TextInput(attrs={
            'placeholder': 'Tu número de teléfono',
            'class': 'form-control',
        }),
    )

    address = forms.CharField(
        label='Dirección',
        max_length=255,
        widget=forms.TextInput(attrs={
            'placeholder': 'Calle y número',
            'class': 'form-control',
        }),
    )

    city = forms.CharField(
        label='Ciudad',
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Ciudad',
            'class': 'form-control',
        }),
    )

    state = forms.CharField(
        label='Estado',
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Estado',
            'class': 'form-control',
        }),
    )

    postal_code = forms.CharField(
        label='Código postal',
        max_length=10,
        widget=forms.TextInput(attrs={
            'placeholder': 'Código postal',
            'class': 'form-control',
        }),
    )

    payment_method = forms.CharField(
        label='Forma de pago',
        initial='Tarjeta de prueba',
        widget=forms.TextInput(attrs={
            'value': 'Tarjeta de prueba',
            'readonly': 'readonly',
            'class': 'form-control',
        }),
    )

    card_name = forms.CharField(
        label='Nombre en la tarjeta',
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Nombre del titular',
            'class': 'form-control',
        }),
    )

    card_number = forms.CharField(
        label='Número de tarjeta',
        max_length=16,
        min_length=16,
        widget=forms.TextInput(attrs={
            'placeholder': '16 dígitos',
            'maxlength': '16',
            'inputmode': 'numeric',
            'class': 'form-control',
        }),
    )

    expiry = forms.CharField(
        label='Vencimiento',
        max_length=5,
        widget=forms.TextInput(attrs={
            'placeholder': 'MM/AA',
            'maxlength': '5',
            'class': 'form-control',
        }),
    )

    cvv = forms.CharField(
        label='CVV',
        max_length=3,
        min_length=3,
        widget=forms.PasswordInput(attrs={
            'placeholder': '3 dígitos',
            'maxlength': '3',
            'inputmode': 'numeric',
            'class': 'form-control',
        }),
    )

    def clean_card_number(self):
        card_number = self.cleaned_data['card_number']

        if not card_number.isdigit() or len(card_number) != 16:
            raise forms.ValidationError(
                'La tarjeta debe tener exactamente 16 dígitos.'
            )

        return card_number

    def clean_cvv(self):
        cvv = self.cleaned_data['cvv']

        if not cvv.isdigit() or len(cvv) != 3:
            raise forms.ValidationError(
                'El CVV debe tener exactamente 3 dígitos.'
            )

        return cvv

    def clean_expiry(self):
        expiry = self.cleaned_data['expiry'].strip()

        if len(expiry) != 5 or expiry[2] != '/':
            raise forms.ValidationError(
                'Usa el formato MM/AA.'
            )

        month, year = expiry.split('/')

        if not month.isdigit() or not year.isdigit():
            raise forms.ValidationError(
                'El vencimiento debe contener números.'
            )

        if not 1 <= int(month) <= 12:
            raise forms.ValidationError(
                'El mes de vencimiento no es válido.'
            )

        return expiry
