# Lorenzo Watches — proyecto Django

## Iniciar

Desde la carpeta donde está `manage.py`:

```powershell
py -m pip install -r requirements.txt
py manage.py migrate
py manage.py runserver
```

Abre `http://127.0.0.1:8000/`.

## Flujo de compra

1. Entra a `/catalogo/` y agrega relojes al carrito.
2. En `/carrito/` revisa cantidades y subtotal.
3. Presiona **Continuar compra**.
4. Captura nombre, correo, teléfono y dirección de envío.
5. Selecciona una forma de pago ficticia.
6. Presiona **Confirmar pedido**.

Django crea un pedido y sus detalles, valida el inventario dentro de una transacción y descuenta las piezas compradas. Si no existe suficiente stock, no crea el pedido. Al finalizar, muestra un número de pedido y vacía el carrito.

Los pedidos aparecen en `/admin/` en **Catalog → Orders**. Los mensajes de contacto aparecen en **Contact messages**.

## Correo de confirmación

En modo escolar/desarrollo, el correo se envía con `console.EmailBackend`; por seguridad no se conecta a un servicio real y el contenido del correo se imprime en la terminal donde corre Django. El pedido conserva el correo del cliente en la base de datos. No se guardan números reales de tarjetas y no se realiza ningún cargo.

## Tablas nuevas

- `catalog_order`: datos del cliente, envío, total, forma de pago ficticia y estado.
- `catalog_orderitem`: productos, cantidades, precios y subtotales de cada pedido.
- `catalog_product`: productos e inventario.
