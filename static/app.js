
const API = "";

// ------------------------------
// Cart storage
// ------------------------------

function getCart() {
    return JSON.parse(localStorage.getItem("minidash_cart") || "null");
}

function saveCart(cart) {
    localStorage.setItem("minidash_cart", JSON.stringify(cart));
    updateCartCount();
}

function clearCart() {
    localStorage.removeItem("minidash_cart");
    updateCartCount();
}

function money(cents) {
    return "$" + (cents / 100).toFixed(2);
}

function escapeHTML(value) {
    return String(value).replace(/[&<>"']/g, character => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;"
    })[character]);
}

function updateCartCount() {
    const element = document.getElementById("cart-count");
    if (!element) return;

    const cart = getCart();
    const count = cart
        ? cart.items.reduce((sum, item) => sum + item.quantity, 0)
        : 0;

    element.textContent = count;
}

// ------------------------------
// API requests
// ------------------------------

async function apiRequest(url, options = {}) {
    const response = await fetch(API + url, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {})
        }
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
        throw new Error(
            typeof data.detail === "string"
                ? data.detail
                : "Something went wrong."
        );
    }

    return data;
}

// ------------------------------
// Page navigation
// ------------------------------

function showPage(pageId) {
    document.querySelectorAll(".page").forEach(page => {
        page.classList.add("hidden");
    });

    const page = document.getElementById(pageId);

    if (page) {
        page.classList.remove("hidden");
    }
}

function getCurrentPath() {
    return window.location.pathname.replace(/\/+$/, "") || "/";
}

async function initializePage() {
    updateCartCount();

    const path = getCurrentPath();

    if (path === "/") {
        showPage("homePage");
        await loadRestaurants();
        return;
    }

    const restaurantMatch = path.match(/^\/restaurants\/(\d+)$/);

    if (restaurantMatch) {
        showPage("restaurantPage");
        await loadRestaurant(Number(restaurantMatch[1]));
        return;
    }

    if (path === "/checkout") {
        showPage("checkoutPage");
        renderCheckout();
        setupCheckout();
        return;
    }

    const confirmationMatch = path.match(/^\/confirmation\/(\d+)$/);

    if (confirmationMatch) {
        showPage("confirmationPage");
        await loadConfirmation(Number(confirmationMatch[1]));
        return;
    }

    if (path === "/track-order") {
        showPage("trackingPage");
        setupTracking();
        return;
    }

    showPage("homePage");
    await loadRestaurants();
}

// ------------------------------
// Homepage
// ------------------------------

async function loadRestaurants() {
    const container = document.getElementById("restaurant-list");

    container.innerHTML = "<p>Loading restaurants...</p>";

    try {
        const restaurants = await apiRequest("/restaurants");

        container.innerHTML = restaurants.map(restaurant => `
            <div class="restaurant-card">
                <h3>${escapeHTML(restaurant.name)}</h3>
                <p>${escapeHTML(restaurant.cuisine)}</p>
                <p>
                    Hours: ${escapeHTML(restaurant.opens_at)}
                    - ${escapeHTML(restaurant.closes_at)}
                </p>
                <a href="/restaurants/${restaurant.id}" class="button">
                    View Menu
                </a>
            </div>
        `).join("");

    } catch (error) {
        container.innerHTML = `<p>${escapeHTML(error.message)}</p>`;
    }
}

// ------------------------------
// Restaurant page
// ------------------------------

async function loadRestaurant(restaurantId) {
    const name = document.getElementById("restaurant-name");
    const description = document.getElementById("restaurant-description");
    const menuContainer = document.getElementById("menu-list");
    const message = document.getElementById("restaurant-message");

    name.textContent = "Loading...";
    menuContainer.innerHTML = "";

    try {
        const restaurants = await apiRequest("/restaurants");

        const restaurant = restaurants.find(
            item => item.id === restaurantId
        );

        if (!restaurant) {
            throw new Error("Restaurant not found.");
        }

        name.textContent = restaurant.name;
        description.textContent =
            `${restaurant.cuisine} | ${restaurant.opens_at} - ${restaurant.closes_at}`;

        const menu = await apiRequest(
            `/restaurants/${restaurantId}/menu`
        );

        menuContainer.innerHTML = menu.map(item => `
            <div class="menu-card">
                <div>
                    <h3>${escapeHTML(item.name)}</h3>
                    <p class="price">${money(item.price_cents)}</p>
                </div>

                <button
                    class="button add-to-cart"
                    data-id="${item.id}"
                    data-name="${escapeHTML(item.name)}"
                    data-price="${item.price_cents}"
                    data-restaurant="${restaurant.id}"
                    data-restaurant-name="${escapeHTML(restaurant.name)}"
                >
                    Add to Cart
                </button>
            </div>
        `).join("");

    } catch (error) {
        message.textContent = error.message;
    }
}

// ------------------------------
// Add items to cart
// ------------------------------

document.addEventListener("click", event => {
    const button = event.target.closest(".add-to-cart");

    if (!button) return;

    const restaurantId = Number(button.dataset.restaurant);
    const itemId = Number(button.dataset.id);

    let cart = getCart();

    if (cart && cart.restaurantId !== restaurantId) {
        const replaceCart = confirm(
            "Your cart contains items from another restaurant. Clear it and start a new cart?"
        );

        if (!replaceCart) return;

        cart = null;
    }

    if (!cart) {
        cart = {
            restaurantId,
            restaurantName: button.dataset.restaurantName,
            items: []
        };
    }

    const existingItem = cart.items.find(item => item.id === itemId);

    if (existingItem) {
        existingItem.quantity += 1;
    } else {
        cart.items.push({
            id: itemId,
            name: button.dataset.name,
            price_cents: Number(button.dataset.price),
            quantity: 1
        });
    }

    saveCart(cart);

    alert(`${button.dataset.name} added to cart!`);
});

// ------------------------------
// Checkout cart display
// ------------------------------

function renderCheckout() {
    const container = document.getElementById("cart-items");
    const totalElement = document.getElementById("cart-total");
    const form = document.getElementById("checkout-form");

    const cart = getCart();

    if (!cart || cart.items.length === 0) {
        container.innerHTML = `
            <p>Your cart is empty.</p>
            <a href="/" class="button">Browse Restaurants</a>
        `;

        totalElement.textContent = "";
        form.classList.add("hidden");
        return;
    }

    form.classList.remove("hidden");

    container.innerHTML = `
        <h3>${escapeHTML(cart.restaurantName)}</h3>

        ${cart.items.map(item => `
            <div class="cart-item">
                <div>
                    <strong>${escapeHTML(item.name)}</strong>
                    <p>${money(item.price_cents)} each</p>
                </div>

                <div>
                    <button type="button"
                        class="quantity-change"
                        data-id="${item.id}"
                        data-change="-1">−</button>

                    ${item.quantity}

                    <button type="button"
                        class="quantity-change"
                        data-id="${item.id}"
                        data-change="1">+</button>

                    <button type="button"
                        class="remove-item"
                        data-id="${item.id}">Remove</button>
                </div>
            </div>
        `).join("")}
    `;

    const total = cart.items.reduce(
        (sum, item) => sum + item.price_cents * item.quantity,
        0
    );

    totalElement.textContent = `Total: ${money(total)}`;
}

// ------------------------------
// Change cart quantities
// ------------------------------

document.addEventListener("click", event => {
    const quantityButton = event.target.closest(".quantity-change");
    const removeButton = event.target.closest(".remove-item");

    if (!quantityButton && !removeButton) return;

    const cart = getCart();
    if (!cart) return;

    const itemId = Number(
        quantityButton?.dataset.id || removeButton?.dataset.id
    );

    if (removeButton) {
        cart.items = cart.items.filter(item => item.id !== itemId);
    } else {
        const item = cart.items.find(item => item.id === itemId);

        if (item) {
            item.quantity += Number(quantityButton.dataset.change);
        }

        cart.items = cart.items.filter(item => item.quantity > 0);
    }

    if (cart.items.length === 0) {
        clearCart();
    } else {
        saveCart(cart);
    }

    renderCheckout();
});

// ------------------------------
// Date and timezone helpers
// ------------------------------

function toLocalDateTimeValue(date) {
    const local = new Date(
        date.getTime() - date.getTimezoneOffset() * 60000
    );

    return local.toISOString().slice(0, 16);
}

function addLocalTimezoneOffset(value) {
    const date = new Date(value);
    const offset = -date.getTimezoneOffset();

    const sign = offset >= 0 ? "+" : "-";

    const hours = String(
        Math.floor(Math.abs(offset) / 60)
    ).padStart(2, "0");

    const minutes = String(
        Math.abs(offset) % 60
    ).padStart(2, "0");

    return `${value}:00${sign}${hours}:${minutes}`;
}

// ------------------------------
// Checkout and order creation
// ------------------------------

function setupCheckout() {
    const form = document.getElementById("checkout-form");
    const scheduledInput = document.getElementById("scheduled-for");
    const message = document.getElementById("checkout-message");

    const minimum = new Date(Date.now() + 45 * 60000);
    const maximum = new Date(Date.now() + 7 * 86400000);

    scheduledInput.min = toLocalDateTimeValue(minimum);
    scheduledInput.max = toLocalDateTimeValue(maximum);

    form.addEventListener("submit", async event => {
        event.preventDefault();

        const cart = getCart();

        if (!cart || cart.items.length === 0) {
            message.textContent = "Your cart is empty.";
            return;
        }

        const address = document.getElementById("delivery-address").value.trim();

        if (address.length < 5) {
            message.textContent = "Please enter a valid delivery address.";
            return;
        }

        let scheduledFor = null;

        if (scheduledInput.value) {
            const value = scheduledInput.value;
            const selectedDate = new Date(value);

            if (
                selectedDate < minimum ||
                selectedDate > maximum
            ) {
                message.textContent =
                    "Delivery must be at least 45 minutes and no more than 7 days ahead.";
                return;
            }

            scheduledFor = addLocalTimezoneOffset(value);
        }

        const orderRequest = {
            restaurant_id: cart.restaurantId,
            address,
            items: cart.items.map(item => ({
                menu_item_id: item.id,
                quantity: item.quantity
            })),
            scheduled_for: scheduledFor
        };

        const submitButton = form.querySelector("button[type='submit']");
        submitButton.disabled = true;
        message.textContent = "Submitting your order...";

        try {
            const order = await apiRequest("/orders", {
                method: "POST",
                body: JSON.stringify(orderRequest)
            });

            clearCart();

            window.location.href = `/confirmation/${order.order_id}`;

        } catch (error) {
            message.textContent = error.message;
            submitButton.disabled = false;
        }
    });
}

// ------------------------------
// Order confirmation
// ------------------------------

async function loadConfirmation(orderId) {
    const container = document.getElementById("confirmation-details");

    container.innerHTML = "<p>Loading confirmation...</p>";

    try {
        const order = await apiRequest(`/orders/${orderId}`);

        container.innerHTML = `
            <h2>Order #${order.id}</h2>
            <p><strong>Status:</strong> ${escapeHTML(order.status)}</p>
            <p><strong>Restaurant ID:</strong> ${order.restaurant_id}</p>
            <p><strong>Delivery Address:</strong>
                ${escapeHTML(order.address)}
            </p>

            ${order.scheduled_for ? `
                <p><strong>Scheduled for:</strong>
                    ${escapeHTML(order.scheduled_for)}
                </p>
            ` : ""}

            <h3>Items</h3>

            ${order.items.map(item => `
                <p>
                    ${escapeHTML(item.name)} × ${item.quantity}
                    — ${money(item.price_cents * item.quantity)}
                </p>
            `).join("")}

            <h3>Total: ${money(order.total_cents)}</h3>
        `;

    } catch (error) {
        container.innerHTML = `<p>${escapeHTML(error.message)}</p>`;
    }
}

// ------------------------------
// Order tracking
// ------------------------------

function setupTracking() {
    const form = document.getElementById("tracking-form");

    form.addEventListener("submit", async event => {
        event.preventDefault();

        const orderId = Number(
            document.getElementById("tracking-id").value
        );

        if (orderId > 0) {
            await trackOrder(orderId);
        }
    });
}

async function trackOrder(orderId) {
    const container = document.getElementById("tracking-result");

    container.innerHTML = "<p>Loading order...</p>";

    try {
        const order = await apiRequest(`/orders/${orderId}`);

        container.innerHTML = `
            <div class="order-card">
                <h2>Order #${order.id}</h2>

                <p><strong>Status:</strong>
                    ${escapeHTML(order.status)}
                </p>

                <p><strong>Delivery Address:</strong>
                    ${escapeHTML(order.address)}
                </p>

                ${order.scheduled_for ? `
                    <p><strong>Scheduled for:</strong>
                        ${escapeHTML(order.scheduled_for)}
                    </p>
                ` : ""}

                <h3>Items</h3>

                ${order.items.map(item => `
                    <p>
                        ${escapeHTML(item.name)} × ${item.quantity}
                    </p>
                `).join("")}

                <h3>Total: ${money(order.total_cents)}</h3>

                ${order.status === "SCHEDULED" ? `
                    <button type="button" id="cancel-order-button"
                        class="button secondary">
                        Cancel Scheduled Order
                    </button>
                ` : ""}
            </div>
        `;

        const cancelButton = document.getElementById("cancel-order-button");

        if (cancelButton) {
            cancelButton.addEventListener("click", async () => {
                if (!confirm("Are you sure you want to cancel this order?")) {
                    return;
                }

                cancelButton.disabled = true;

                try {
                    await apiRequest(`/orders/${orderId}/status`, {
                        method: "PATCH",
                        body: JSON.stringify({
                            status: "CANCELLED"
                        })
                    });

                    await trackOrder(orderId);

                } catch (error) {
                    alert(error.message);
                    cancelButton.disabled = false;
                }
            });
        }

    } catch (error) {
        container.innerHTML = `<p>${escapeHTML(error.message)}</p>`;
    }
}

// ------------------------------
// Start application
// ------------------------------

document.addEventListener("DOMContentLoaded", initializePage);
