from django.urls import path
from . import views

app_name = 'catalog'
urlpatterns = [
    path('', views.home, name='home'),
    path('catalogo/', views.catalog, name='catalog'),
    path('producto/<int:product_id>/', views.product_detail, name='product_detail'),
    path('nosotros/', views.about, name='about'),
    path('contacto/', views.contact, name='contact'),
    path('carrito/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
]
