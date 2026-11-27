import json
import uuid
from decimal import Decimal

from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.utils.html import strip_tags
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ContactForm, CheckoutForm
from .models import ContactMessage, Order, OrderItem, Product


def home(request):
    products = Product.objects.all()[:6]

    return render(request, 'catalog/home.html', {
        'products': products,
    })


def catalog(request):
    products = Product.objects.all()

    return render(request, 'catalog/catalog.html', {
        'products': products,
    })


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    return render(request, 'catalog/product_detail.html', {
        'product': product,
    })


def cart(request):
    return render(request, 'catalog/cart.html')


def contact(request):
    enviado = False

    if request.method == 'POST':
        form = ContactForm(request.POST)

        if form.is_valid():
            contact_message = ContactMessage.objects.create(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                message=form.cleaned_data['message'],
            )

            subject = f'Nuevo mensaje de contacto - Lorenzo Watches'
            body = (
                f'Has recibido un mensaje desde el sitio web de Lorenzo Watches.\n\n'
                f'Nombre: {contact_message.name}\n'
                f'Correo: {contact_message.email}\n\n'
                f'Mensaje:\n{contact_message.message}'
            )
            send_mail(
                subject, body, settings.DEFAULT_FROM_EMAIL,
                [settings.ADMIN_EMAIL], fail_silently=True,
                reply_to=[contact_message.email],
            )
            send_mail(
                'Recibimos tu mensaje - Lorenzo Watches',
                f'Hola {contact_message.name},\n\nGracias por escribirnos. Hemos recibido tu mensaje y nos pondremos en contacto contigo pronto.\n\nLorenzo Watches',
                settings.DEFAULT_FROM_EMAIL, [contact_message.email],
                fail_silently=True,
            )

            enviado = True
            form = ContactForm()
    else:
        form = ContactForm()

    return render(request, 'catalog/contact.html', {
        'form': form,
        'enviado': enviado,
    })


def products_api(request):
    products = Product.objects.all()

    data = []

    for product in products:
        data.append({
            'id': product.id,
            'name': product.name,
            'brand': product.brand,
            'price': float(product.price),
            'category': product.category,
            'description': product.description,
            'image': product.image,
            'stock': product.stock,
        })

    return JsonResponse(data, safe=False)


@transaction.atomic
def checkout(request):
    if request.method == 'POST':
        form = CheckoutForm(request.POST)

        if form.is_valid():
            cart_data_text = request.POST.get('cart_data', '[]')

            try:
                cart_data = json.loads(cart_data_text)
            except json.JSONDecodeError:
                cart_data = []

            if not cart_data:
                form.add_error(
                    None,
                    'El carrito está vacío. Agrega un reloj antes de continuar.'
                )

                return render(request, 'catalog/checkout.html', {
                    'form': form,
                })

            products_for_order = []
            total = Decimal('0.00')

            for item in cart_data:
                try:
                    product_id = int(item.get('id'))
                    quantity = int(item.get('qty', 0))
                except (TypeError, ValueError):
                    form.add_error(
                        None,
                        'Los datos del carrito no son válidos.'
                    )

                    return render(request, 'catalog/checkout.html', {
                        'form': form,
                    })

                if quantity <= 0:
                    form.add_error(
                        None,
                        'La cantidad de productos no es válida.'
                    )

                    return render(request, 'catalog/checkout.html', {
                        'form': form,
                    })

                product = Product.objects.select_for_update().filter(
                    id=product_id
                ).first()

                if product is None:
                    form.add_error(
                        None,
                        'Uno de los productos ya no existe.'
                    )

                    return render(request, 'catalog/checkout.html', {
                        'form': form,
                    })

                if product.stock < quantity:
                    form.add_error(
                        None,
                        f'No hay suficiente inventario de {product.name}. '
                        f'Disponibles: {product.stock}.'
                    )

                    return render(request, 'catalog/checkout.html', {
                        'form': form,
                    })

                subtotal = product.price * quantity
                total += subtotal

                products_for_order.append({
                    'product': product,
                    'quantity': quantity,
                    'price': product.price,
                })

            customer_name = form.cleaned_data['customer_name']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            address = form.cleaned_data['address']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            postal_code = form.cleaned_data['postal_code']
            payment_method = form.cleaned_data.get(
                'payment_method',
                'Tarjeta de prueba'
            )

            order = Order.objects.create(
                order_number=f'LW-{uuid.uuid4().hex[:8].upper()}',
                customer_name=customer_name,
                email=email,
                phone=phone,
                address=address,
                city=city,
                state=state,
                postal_code=postal_code,
                total=total,
                payment_method=payment_method,
            )

            for item in products_for_order:
                product = item['product']
                quantity = item['quantity']

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name,
                    unit_price=item['price'],
                    quantity=quantity,
                    subtotal=item['price'] * quantity,
                )

                product.stock -= quantity
                product.save(update_fields=['stock'])

            # Enviar confirmacion al cliente y aviso al administrador.
            items_text = '\n'.join(
                f'- {item.product_name} x {item.quantity}: ${item.subtotal:.2f}'
                for item in order.items.all()
            )
            order_details = (
                f'Pedido: {order.order_number}\n'
                f'Cliente: {order.customer_name}\n'
                f'Correo: {order.email}\n'
                f'Teléfono: {order.phone}\n'
                f'Dirección: {order.address}, {order.city}, {order.state}, C.P. {order.postal_code}\n\n'
                f'Productos:\n{items_text}\n\n'
                f'Total: ${order.total:.2f}\n'
                f'Forma de pago: {order.get_payment_method_display()} (simulado)'
            )
            email_sent = False
            try:
                customer_sent = send_mail(
                    f'Confirmación de compra {order.order_number} - Lorenzo Watches',
                    f'Hola {order.customer_name},\n\n¡Gracias por tu compra! Tu pedido ha sido registrado correctamente.\n\n{order_details}\n\nEste pedido es una demostración escolar; no se realizó ningún cargo real.\n\nLorenzo Watches',
                    settings.DEFAULT_FROM_EMAIL, [order.email], fail_silently=False,
                )
                admin_sent = send_mail(
                    f'Nuevo pedido {order.order_number} - Lorenzo Watches',
                    f'Se registró una nueva compra en la tienda.\n\n{order_details}',
                    settings.DEFAULT_FROM_EMAIL, [settings.ADMIN_EMAIL], fail_silently=False,
                )
                email_sent = bool(customer_sent and admin_sent)
            except Exception:
                # El pedido queda registrado aunque el servicio de correo falle.
                email_sent = False

            return render(request, 'catalog/order_success.html', {
                'order': order,
                'email_sent': email_sent,
            })

    else:
        form = CheckoutForm()

    return render(request, 'catalog/checkout.html', {
        'form': form,
    })
