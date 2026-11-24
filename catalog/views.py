import json
import secrets
from decimal import Decimal

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from rest_framework import viewsets

from .forms import CheckoutForm, ContactMessageForm
from .models import Order, OrderItem, Product
from .serializers import ProductSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


def _products():
    return list(Product.objects.all().order_by('-id'))


def home(request):
    return render(request, 'catalog/home.html', {'featured_products': _products()[:4]})


def catalog(request):
    return render(request, 'catalog/catalog.html', {'products': _products()})


def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    related = Product.objects.exclude(pk=product_id).filter(category=product.category)[:4]
    return render(request, 'catalog/product_detail.html', {'product': product, 'related_products': related})


def about(request):
    return render(request, 'catalog/about.html')


def contact(request):
    enviado = False
    if request.method == 'POST':
        form = ContactMessageForm(request.POST)
        if form.is_valid():
            form.save()
            enviado = True
            form = ContactMessageForm()
    else:
        form = ContactMessageForm()
    return render(request, 'catalog/contact.html', {'form': form, 'enviado': enviado})


def cart(request):
    return render(request, 'catalog/cart.html')


def checkout(request):
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if not form.is_valid():
            return render(request, 'catalog/checkout.html', {'form': form})

        try:
            cart_data = json.loads(request.POST.get('cart_data', '[]'))
        except (TypeError, ValueError):
            cart_data = []

        if not cart_data:
            form.add_error(None, 'Tu carrito está vacío.')
            return render(request, 'catalog/checkout.html', {'form': form})

        try:
            with transaction.atomic():
                order_lines = []
                total = Decimal('0.00')
                for item in cart_data:
                    product_id = int(item.get('id'))
                    quantity = int(item.get('qty'))
                    if quantity < 1:
                        raise ValueError('Cantidad inválida.')
                    product = Product.objects.select_for_update().get(pk=product_id)
                    if product.stock < quantity:
                        raise ValueError(f'No hay suficiente inventario de {product.name}. Disponible: {product.stock}.')
                    subtotal = product.price * quantity
                    total += subtotal
                    order_lines.append((product, quantity, subtotal))

                order = form.save(commit=False)
                order.order_number = f"LW-{secrets.token_hex(4).upper()}"
                order.total = total
                order.payment_status = 'Simulado - no se realizó un cargo'
                order.status = 'confirmed'
                order.save()

                for product, quantity, subtotal in order_lines:
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        product_name=product.name,
                        unit_price=product.price,
                        quantity=quantity,
                        subtotal=subtotal,
                    )
                    product.stock -= quantity
                    product.save(update_fields=['stock'])
        except Product.DoesNotExist:
            form.add_error(None, 'Uno de los productos ya no está disponible.')
            return render(request, 'catalog/checkout.html', {'form': form})
        except ValueError as error:
            form.add_error(None, str(error))
            return render(request, 'catalog/checkout.html', {'form': form})

        payment_label = order.get_payment_method_display()
        send_mail(
            subject=f'Confirmación de pedido {order.order_number} - Lorenzo Watches',
            message=(
                f'Hola {order.customer_name},\n\n'
                f'Tu pedido {order.order_number} fue registrado correctamente.\n'
                f'Total: ${order.total:,.2f}\n'
                f'Forma de pago: {payment_label} (ficticia)\n'
                f'Envío: {order.address}, {order.city}, {order.state}, C.P. {order.postal_code}\n\n'
                'Este proyecto utiliza pagos simulados; no se realizó ningún cargo real.\n\n'
                'Gracias por comprar en Lorenzo Watches.'
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
            fail_silently=True,
        )
        return render(request, 'catalog/order_success.html', {'order': order})

    return render(request, 'catalog/checkout.html', {'form': CheckoutForm()})
