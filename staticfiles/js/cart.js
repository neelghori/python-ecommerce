document.addEventListener('DOMContentLoaded', () => {
    const quantityButtons = document.querySelectorAll('.cart-item-quantity button');
    quantityButtons.forEach(button => {
        button.addEventListener('click', () => {
            const quantityElement = button.parentElement.querySelector('span');
            let quantity = parseInt(quantityElement.innerText);
            if (button.innerText === '+') {
                quantity++;
            } else if (button.innerText === '-' && quantity > 1) {
                quantity--;
            }
            quantityElement.innerText = quantity;
            const totalElement = button.parentElement.parentElement.querySelector('.cart-item-total');
            const price = parseFloat(totalElement.getAttribute('sup'));
            totalElement.innerText = `₹ ${price * quantity}`;

            const totalAmount = document.querySelector('.cart-total-amount');
            const totalElements = document.querySelectorAll('.cart-item-total');
            let total = 0;
            totalElements.forEach(element => {
                total += parseInt(element.innerText.split(' ')[1]);
            });
            totalAmount.innerText = `₹ ${total}`;
        });
    });

    const totalAmount = document.querySelector('.cart-total-amount');
    const totalElements = document.querySelectorAll('.cart-item-total');
    let total = 0;
    totalElements.forEach(element => {
        total += parseInt(element.innerText.split(' ')[1]);
    });
    totalAmount.innerText = `₹ ${total}`;

    const cartItems = document.querySelectorAll('.cart-table tbody tr');
    if (cartItems.length === 0) {
        const cart = document.querySelector('.cart');
        cart.innerHTML = '<h2>Your cart is empty</h2>';
    }

    const cartTotalItems = document.querySelector('.cart-total-items');
    cartTotalItems.innerText = `${cartItems.length} items`;

    // When hovering over image, a zoomed in version of the image would be displayed.
    const cartItemImages = document.querySelectorAll('.cart-item-image img');
    cartItemImages.forEach(image => {
        image.addEventListener('mouseover', () => {
            // Create overlay
            const overlay = document.createElement('div');
            overlay.id = 'image-overlay';
            overlay.style.position = 'fixed';
            overlay.style.top = '0';
            overlay.style.left = '0';
            overlay.style.width = '100%';
            overlay.style.height = '100%';
            overlay.style.backgroundColor = 'rgba(0,0,0,0.8)';
            overlay.style.display = 'flex';
            overlay.style.justifyContent = 'center';
            overlay.style.alignItems = 'center';
            overlay.style.zIndex = '1000';
            overlay.style.opacity = '0';
            overlay.style.transition = 'opacity 0.3s ease';

            // Create zoomed image
            const zoomedImage = document.createElement('img');
            zoomedImage.id = 'zoomed-image';
            zoomedImage.src = image.src;
            zoomedImage.style.maxHeight = '70%';
            zoomedImage.style.maxWidth = '70%';
            zoomedImage.style.borderRadius = '15px';
            zoomedImage.style.boxShadow = '0 0 20px rgba(255,255,255,0.3)';
            zoomedImage.style.transform = 'scale(0.9)';
            zoomedImage.style.transition = 'transform 0.3s ease';

            // Create caption
            const caption = document.createElement('div');
            caption.textContent = image.closest('tr').querySelector('.cart-item-name').textContent.trim();
            caption.style.color = 'white';
            caption.style.marginTop = '10px';
            caption.style.fontSize = '1.2em';

            // Create close button
            const closeButton = document.createElement('button');
            closeButton.innerHTML = '&times;'; // Using HTML entity for a better-looking X
            closeButton.style.position = 'absolute';
            closeButton.style.top = '20px';
            closeButton.style.right = '20px';
            closeButton.style.background = 'rgba(0, 0, 0)';
            closeButton.style.border = 'none';
            closeButton.style.color = 'white';
            closeButton.style.fontSize = '28px';
            closeButton.style.fontWeight = 'bold';
            closeButton.style.width = '40px';
            closeButton.style.height = '40px';
            closeButton.style.borderRadius = '50%';
            closeButton.style.display = 'flex';
            closeButton.style.justifyContent = 'center';
            closeButton.style.alignItems = 'center';
            closeButton.style.cursor = 'pointer';
            closeButton.style.transition = 'all 0.3s ease';

            // Hover effect for close button
            closeButton.addEventListener('mouseover', () => {
                closeButton.style.transform = 'scale(1.1)';
            });
            closeButton.addEventListener('mouseout', () => {
                closeButton.style.transform = 'scale(1)';
            });

            // Append elements
            const imageContainer = document.createElement('div');
            imageContainer.style.textAlign = 'center';
            imageContainer.appendChild(zoomedImage);
            imageContainer.appendChild(caption);
            overlay.appendChild(imageContainer);
            overlay.appendChild(closeButton);
            document.body.appendChild(overlay);

            // Trigger transitions
            setTimeout(() => {
                overlay.style.opacity = '1';
                zoomedImage.style.transform = 'scale(1)';
            }, 50);

            // Close overlay on button click, overlay click, or Escape key press
            const closeOverlay = () => {
                overlay.style.opacity = '0';
                zoomedImage.style.transform = 'scale(0.9)';
                setTimeout(() => overlay.remove(), 300);
            };
            closeButton.addEventListener('click', closeOverlay);
            overlay.addEventListener('click', (e) => {
                if (e.target === overlay) closeOverlay();
            });
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') closeOverlay();
            });
        });
    });

    const checkoutButton = document.querySelector('.cart-checkout button');
    checkoutButton.addEventListener('click', () => {
        const placeOrderUrl = checkoutButton.getAttribute('data-place-order-url');
        const csrfToken = checkoutButton.getAttribute('data-csrf-token');
        const cartItems = document.querySelectorAll('.cart-item');
        const itemIds = [];
        const quantities = [];
        cartItems.forEach(item => {
            const itemId = item.querySelector('.cart-item-name').getAttribute('data-aria-class');
            const quantity = item.querySelector('.cart-item-quantity span').innerText;
            itemIds.push(itemId);
            quantities.push(quantity);
        });

        // POST request to place order. The view will then create an order and redirect to the order page.
        fetch(placeOrderUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                itemIds: itemIds,
                quantities: quantities
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                window.location.href = data.redirect_url;
            } else {
                alert('There was an error placing the order. Please try again.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while processing your request.');
        });
    });
});
