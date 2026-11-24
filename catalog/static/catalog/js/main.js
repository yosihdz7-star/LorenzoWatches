const cartKey = 'lorenzo_cart';

function getCart() {
    try {
        return JSON.parse(localStorage.getItem(cartKey)) || [];
    } catch (error) {
        return [];
    }
}

function saveCart(cart) {
    localStorage.setItem(cartKey, JSON.stringify(cart));
    updateCartCount();
}

function updateCartCount() {
    const count = getCart().reduce((total, item) => total + item.qty, 0);
    const counter = document.getElementById('cart-count');

    if (counter) {
        counter.textContent = count;
    }
}

async function getProducts() {
    const response = await fetch('/api/products/');

    if (!response.ok) {
        throw new Error('No se pudieron cargar los productos');
    }

    return await response.json();
}

function money(value) {
    return '$' + Number(value).toLocaleString('es-MX', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

async function renderCart() {
    const container = document.getElementById('cart-items');

    if (!container) {
        return;
    }

    const cart = getCart();

    if (cart.length === 0) {
        container.innerHTML = '<p class="empty">Tu carrito está vacío.</p>';

        const total = document.getElementById('cart-total');

        if (total) {
            total.textContent = '$0.00';
        }

        return;
    }

    try {
        const products = await getProducts();
        let total = 0;

        container.innerHTML = cart.map(item => {
            const product = products.find(
                product => String(product.id) === String(item.id)
            );

            if (!product) {
                return '';
            }

            const subtotal = Number(product.price) * item.qty;
            total += subtotal;

            return `
                <article class="cart-item">
                    <div>
                        <p class="product-brand">${product.brand}</p>
                        <h3>${product.name}</h3>
                        <p>${money(product.price)} × ${item.qty}</p>
                    </div>

                    <div>
                        <strong>${money(subtotal)}</strong>
                        <button class="remove-item" data-remove-cart="${product.id}">
                            Quitar
                        </button>
                    </div>
                </article>
            `;
        }).join('');

        const totalElement = document.getElementById('cart-total');

        if (totalElement) {
            totalElement.textContent = money(total);
        }
    } catch (error) {
        container.innerHTML = `
            <p class="empty">
                No se pudieron cargar los productos del carrito.
            </p>
        `;
    }
}

document.addEventListener('click', async function(event) {
    const addButton = event.target.closest('[data-add-cart]');

    if (addButton) {
        const productId = addButton.dataset.addCart;
        const cart = getCart();

        try {
            const products = await getProducts();

            const product = products.find(
                product => String(product.id) === String(productId)
            );

            if (!product) {
                alert('No se encontró el producto.');
                return;
            }

            const existing = cart.find(
                item => String(item.id) === String(productId)
            );

            const currentQuantity = existing ? existing.qty : 0;

            if (currentQuantity >= product.stock) {
                alert(`Solo hay ${product.stock} piezas disponibles.`);
                return;
            }

            if (existing) {
                existing.qty++;
            } else {
                cart.push({
                    id: productId,
                    qty: 1
                });
            }

            saveCart(cart);
            await renderCart();

            const originalText = addButton.textContent;
            addButton.textContent = 'Agregado ✓';

            setTimeout(() => {
                addButton.textContent = originalText;
            }, 1400);
        } catch (error) {
            alert('No se pudo agregar el producto.');
        }
    }

    const removeButton = event.target.closest('[data-remove-cart]');

    if (removeButton) {
        const productId = removeButton.dataset.removeCart;
        const cart = getCart().filter(
            item => String(item.id) !== String(productId)
        );

        saveCart(cart);
        await renderCart();
    }
});

document.getElementById('menu-button')?.addEventListener('click', function() {
    document.getElementById('main-nav').classList.toggle('open');
});

updateCartCount();
renderCart();
