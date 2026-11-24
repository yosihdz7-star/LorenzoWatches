from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=150)
    brand = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50)
    description = models.TextField()
    image = models.CharField(max_length=255)
    stock = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.brand} - {self.name}"


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"


class Order(models.Model):
    PAYMENT_CHOICES = [
        ('card_test', 'Tarjeta de prueba'),
        ('transfer_test', 'Transferencia simulada'),
        ('cash', 'Pago contra entrega'),
    ]
    STATUS_CHOICES = [
        ('confirmed', 'Confirmado'),
        ('preparing', 'En preparación'),
        ('sent', 'Enviado'),
        ('cancelled', 'Cancelado'),
    ]

    order_number = models.CharField(max_length=20, unique=True)
    customer_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    payment_status = models.CharField(max_length=30, default='Simulado - no se realizó un cargo')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    total = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Pedido {self.order_number} - {self.customer_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    product_name = models.CharField(max_length=150)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"
