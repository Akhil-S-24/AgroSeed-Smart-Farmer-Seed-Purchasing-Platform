document.addEventListener("DOMContentLoaded", () => {
    const container = document.getElementById('seed-container');
    const modal = document.getElementById('modal');
    const modalContent = document.getElementById('modal-content');
    const closeModalBtn = document.getElementById('close-modal');

    fetch('/api/seeds')
        .then(res => res.json())
        .then(seeds => {
            seeds.forEach(seed => {
                console.log(seed._id)
                console.log(seed.name)
                const card = document.createElement('div');
                card.className = "bg-white rounded-xl shadow-md hover:shadow-xl transition duration-300 transform hover:-translate-y-1";
                card.innerHTML = `
    <div class="bg-white rounded-xl shadow-xl overflow-hidden transform transition hover:scale-105 duration-300">
        <img src="${seed.images[0]}" alt="${seed.name}" class="w-full h-48 object-cover">
        <div class="p-4">
            <h3 class="text-2xl font-bold text-green-700 mb-2">${seed.name}</h3>
            <p class="text-gray-600 mb-1"><span class="font-semibold">Type:</span> ${seed.type}</p>
            <p class="text-gray-600 mb-1"><span class="font-semibold">Quantity:</span> ${seed.quantity}</p>
            <p class="text-gray-800 font-semibold text-lg mb-2">₹ ${seed.price}</p>
<div class="mb-4">
  ${seed.rating || seed.rating_count
                        ? `
      <div class="flex items-center space-x-2">
        <div class="flex text-yellow-500 text-lg">
          ${[1, 2, 3, 4, 5].map(i => {
                            if (i <= Math.floor(seed.rating)) return '&#9733;';
                            else if (i - seed.rating < 1) return '&#9733;'; // Optionally use half-star
                            else return '<span class="text-gray-300">&#9733;</span>';
                        }).join('')}
        </div>
        <span class="text-gray-700 text-sm font-medium">
         (${seed.rating_count})
        </span>
      </div>`
                        : `<p class="text-gray-500 italic">Not rated</p>`
                    }
</div>

            <button class="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-2 rounded book-btn" data-id="${seed._id}">
                View Product
            </button>
        </div>
    </div>
`;
                container.appendChild(card);
            });

            document.querySelectorAll('.book-btn').forEach(button => {
                button.addEventListener('click', (e) => {
                    const seedId = e.target.dataset.id;
                    fetch(`/api/seeds/${seedId}`)
                        .then(res => res.json())
                        .then(seed => {
                            modalContent.innerHTML = `
                            <!-- Notification Box -->
<div id="notification-box" class="hidden mt-8 mb-4 p-3 rounded text-white text-sm font-medium"></div>

                            <div class="bg-white rounded-lg p-6 max-w-4xl mx-auto flex flex-col md:flex-row gap-6">
  <!-- Left Column: Images -->
  <div class="w-full md:w-1/2">
    <img id="main-product-image" src="${seed.images?.[0]}" alt="${seed.name}" class="w-full h-96 object-contain border rounded-lg mb-4" />
    <div class="flex gap-3 overflow-x-auto thumbnail-container">
      ${seed.images.map(img => `
        <img src="${img}" class="thumbnail w-20 h-20 object-cover border rounded cursor-pointer hover:ring-2 ring-green-500" />
      `).join('')}
    </div>
  </div>

  <!-- Right Column: Details -->
  <div class="w-full md:w-1/2">
    <h2 class="text-3xl font-bold text-green-700 mb-4">${seed.name}</h2>
    
    <p class="mb-2"><strong>Type:</strong> ${seed.type}</p>
    <p class="mb-2"><strong>Available Stock:</strong> ${seed.quantity} units</p>
    
    <!-- Editable Quantity -->
    <div class="mb-2">
      <label for="quantity-input" class="font-semibold block mb-1">Set Quantity :</label>
      <input type="number" id="quantity-input" name="quantity" value="1" min="1" max="${seed.quantity}" step="1"
             class="border border-gray-300 rounded px-3 py-1 w-24 focus:outline-none focus:ring-2 focus:ring-green-500" />
      <span class="text-sm text-gray-500 ml-2">Max: ${seed.quantity}</span>
    </div>

    <!-- Live Price Display -->
    <p class="mb-4 text-lg text-green-800 font-semibold">
      Total Price: ₹<span id="total-price">${seed.price}</span>
    </p>
    <p class="mb-2"><strong>Vendor Name: </strong> ${seed.user_id?.name}</p>
    

    <!-- Optional Instructions -->
    <p class="mb-4 text-sm text-gray-600">
      <strong>Instructions:</strong> ${seed.instructions || 'No instructions provided'}
    </p>

    <!-- Video Link -->
    ${seed.video_link ? `
    <p class="mb-4 text-sm text-gray-600">
      📹 <strong>Video:</strong> 
      <a href="${seed.video_link}" target="_blank" class="text-blue-600 underline block truncate max-w-xs">
        ${seed.video_link}
      </a>
    </p>
    ` : ''}

    <!-- Payment Button -->
    <button id="pay-now-btn" class="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded w-full font-semibold">
      Pay Now & Book
    </button>
  </div>
</div>

<!-- Hide Scrollbar -->
<style>
  .thumbnail-container::-webkit-scrollbar {
    display: none;
  }

  .thumbnail-container {
    -ms-overflow-style: none;
    scrollbar-width: none;
  }
</style>
`;

                            function showNotification(message, type) {
                                const box = document.getElementById('notification-box');
                                if (!box) return;

                                box.textContent = message;
                                box.classList.remove('hidden');
                                box.classList.remove('bg-red-500', 'bg-green-600');

                                if (type === 'error') {
                                    box.classList.add('bg-red-500');
                                } else {
                                    box.classList.add('bg-green-600');
                                    setTimeout(() => {
                                        modal.classList.add('hidden');
                                    }, 2000);
                                }

                                setTimeout(() => {
                                    box.classList.add('hidden');
                                }, 3000);
                            }

                            // Initialize Razorpay payment
                            const payNowBtn = modalContent.querySelector('#pay-now-btn');
                            const quantityInput = modalContent.querySelector('#quantity-input');
                            const priceDisplay = modalContent.querySelector('#total-price');
                            const basePrice = parseFloat(seed.price);

                            // Update price when quantity changes
                            quantityInput.addEventListener('input', () => {
                                let quantity = parseInt(quantityInput.value);
                                if (isNaN(quantity) || quantity < 1) {
                                    quantity = 1;
                                    quantityInput.value = 1;
                                }
                                if (quantity > seed.quantity) {
                                    quantity = seed.quantity;
                                    quantityInput.value = seed.quantity;
                                    showNotification(`Maximum available quantity is ${seed.quantity}`, 'error');
                                }

                                const total = basePrice * quantity;
                                priceDisplay.textContent = total.toFixed(2);
                            });

                            // Payment button click handler
                            payNowBtn.addEventListener('click', async () => {
                                const quantity = parseInt(quantityInput.value);
                                const totalAmount = basePrice * quantity;

                                if (quantity < 1 || quantity > seed.quantity) {
                                    showNotification('Please enter a valid quantity', 'error');
                                    return;
                                }

                                // Disable button to prevent multiple clicks
                                payNowBtn.disabled = true;
                                payNowBtn.textContent = 'Processing...';

                                try {
                                    // Create order
                                    const orderResponse = await fetch('/api/create-order', {
                                        method: 'POST',
                                        headers: {
                                            'Content-Type': 'application/json'
                                        },
                                        body: JSON.stringify({
                                            seed_id: seed._id,
                                            quantity: quantity,
                                            amount: totalAmount
                                        })
                                    });

                                    const orderData = await orderResponse.json();

                                    if (!orderResponse.ok) {
                                        throw new Error(orderData.error || 'Failed to create order');
                                    }

                                    // Initialize Razorpay
                                    const options = {
                                        key: orderData.key,
                                        amount: orderData.amount,
                                        currency: orderData.currency,
                                        name: 'Farmer Seed Platform',
                                        description: `Purchase of ${seed.name}`,
                                        order_id: orderData.order_id,
                                        handler: async function (response) {
                                            try {
                                                // Verify payment
                                                const verifyResponse = await fetch('/api/verify-payment', {
                                                    method: 'POST',
                                                    headers: {
                                                        'Content-Type': 'application/json'
                                                    },
                                                    body: JSON.stringify({
                                                        razorpay_order_id: response.razorpay_order_id,
                                                        razorpay_payment_id: response.razorpay_payment_id,
                                                        razorpay_signature: response.razorpay_signature
                                                    })
                                                });

                                                const verifyData = await verifyResponse.json();

                                                if (verifyResponse.ok) {
                                                    showNotification('✅ Payment successful! Booking confirmed.', 'success');
                                                    // Refresh the page after a delay to show updated stock
                                                    setTimeout(() => {
                                                        location.reload();
                                                    }, 2500);
                                                } else {
                                                    throw new Error(verifyData.error || 'Payment verification failed');
                                                }
                                            } catch (error) {
                                                console.error('Payment verification error:', error);
                                                showNotification('❌ Payment verification failed: ' + error.message, 'error');
                                            }
                                        },
                                        prefill: {
                                            name: 'Customer',
                                            email: 'customer@example.com',
                                            contact: '9999999999'
                                        },
                                        theme: {
                                            color: '#16a34a'
                                        },
                                        modal: {
                                            ondismiss: function() {
                                                // Re-enable button if payment is cancelled
                                                payNowBtn.disabled = false;
                                                payNowBtn.textContent = 'Pay Now & Book';
                                            }
                                        }
                                    };

                                    const rzp = new Razorpay(options);
                                    rzp.open();

                                } catch (error) {
                                    console.error('Order creation error:', error);
                                    showNotification('❌ Order creation failed: ' + error.message, 'error');
                                    payNowBtn.disabled = false;
                                    payNowBtn.textContent = 'Pay Now & Book';
                                }
                            });

                            // Handle thumbnail clicks
                            const thumbnails = modalContent.querySelectorAll('.thumbnail');
                            const mainImage = modalContent.querySelector('#main-product-image');

                            thumbnails.forEach(thumb => {
                                thumb.addEventListener('click', () => {
                                    mainImage.src = thumb.src;
                                });
                            });

                            modal.classList.remove('hidden');
                        });
                });
            });
        });

    // Close modal
    closeModalBtn.addEventListener('click', () => {
        modal.classList.add('hidden');
    });

    // View bookings functionality
    document.getElementById("view-bookings-btn").addEventListener("click", () => {
        fetch("/api/bookings")
            .then(res => res.json())
            .then(data => {
                const list = document.getElementById("booking-list");
                list.innerHTML = "";

                if (data.length === 0) {
                    list.innerHTML = "<p class='text-gray-600'>No bookings found.</p>";
                } else {
                    data.forEach(booking => {
                        const div = document.createElement("div");
                        div.className = "border p-4 rounded shadow space-y-2";
                        div.innerHTML = `
  <h3 class="text-lg font-semibold text-green-700">${booking.seed_name}</h3>
  <p><strong>Quantity:</strong> ${booking.quantity}</p>
  <p><strong>Price:</strong> ₹${booking.price}</p>
  <p><strong>Booked On:</strong> ${new Date(booking.timestamp).toLocaleString()}</p>
  <p><strong>Status:</strong> <span class="px-2 py-1 rounded text-xs font-medium ${
    booking.status === 'Confirmed' ? 'bg-blue-100 text-blue-800' :
    booking.status === 'Completed' ? 'bg-green-100 text-green-800' :
    booking.status === 'Cancelled' ? 'bg-red-100 text-red-800' :
    'bg-yellow-100 text-yellow-800'
  }">${booking.status || 'Pending'}</span></p>
  ${booking.payment_id ? `<p><strong>Payment ID:</strong> ${booking.payment_id}</p>` : ''}
  <div class="flex gap-2 flex-wrap items-center">
    ${booking.status === 'Confirmed'
                                ? `
      <p class="text-blue-600 font-medium">✅ Payment confirmed - Order being processed</p>
      `
                                : booking.status === 'Completed'
                                    ? booking.hasRated
                                        ? `
      <p class="text-yellow-600 font-medium">You rated: ${booking.userRating} ⭐</p>
      <button class="delete-rating-btn bg-gray-500 text-white px-3 py-1 rounded" data-seedid="${booking.seed_id}">Delete Rating</button>
      `
                                        : `
      <div class="star-rating" data-id="${booking._id}">
        <span class="star cursor-pointer text-2xl" data-value="1">&#9734;</span>
        <span class="star cursor-pointer text-2xl" data-value="2">&#9734;</span>
        <span class="star cursor-pointer text-2xl" data-value="3">&#9734;</span>
        <span class="star cursor-pointer text-2xl" data-value="4">&#9734;</span>
        <span class="star cursor-pointer text-2xl" data-value="5">&#9734;</span>
      </div>
      `
                                    : booking.status === 'Cancelled'
                                        ? `<p class="text-red-600 font-medium">❌ Order cancelled</p>`
                                        : `<p class="text-yellow-600 font-medium">⏳ Awaiting vendor confirmation</p>`
                            }
  </div>
`;
                        list.appendChild(div);
                    });

                    // Star rating functionality for completed orders
                    document.querySelectorAll(".star-rating").forEach(container => {
                        const stars = container.querySelectorAll(".star");
                        const bookingId = container.dataset.id;
                        let selectedRating = 0;

                        // Create submit button dynamically
                        const submitBtn = document.createElement("button");
                        submitBtn.textContent = "Submit Rating";
                        submitBtn.className = "submit-rating-btn bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded ml-2 mt-2";
                        container.appendChild(submitBtn);

                        // Star hover and selection
                        stars.forEach(star => {
                            star.addEventListener("mouseover", () => {
                                const value = parseInt(star.dataset.value);
                                highlightStars(stars, value);
                            });

                            star.addEventListener("mouseout", () => {
                                highlightStars(stars, selectedRating);
                            });

                            star.addEventListener("click", () => {
                                selectedRating = parseInt(star.dataset.value);
                                highlightStars(stars, selectedRating);
                            });
                        });

                        // Submit button event
                        submitBtn.addEventListener("click", () => {
                            if (selectedRating === 0) {
                                alert("Please select a rating before submitting.");
                                return;
                            }

                            fetch(`/api/bookings/${bookingId}/rate`, {
                                method: "POST",
                                headers: {
                                    "Content-Type": "application/json"
                                },
                                body: JSON.stringify({ rating: selectedRating })
                            })
                                .then(res => res.json())
                                .then(data => {
                                    if (data.error) {
                                        alert("Error: " + data.error);
                                    } else {
                                        alert("Thanks for rating!");
                                        container.innerHTML = `<p class="text-yellow-600 font-medium">You rated: ${selectedRating} ⭐</p>`;
                                    }
                                })
                                .catch(err => {
                                    alert("Error submitting rating.");
                                    console.error(err);
                                });
                        });

                        // Highlight stars function
                        function highlightStars(stars, value) {
                            stars.forEach(star => {
                                const val = parseInt(star.dataset.value);
                                if (val <= value) {
                                    star.classList.add("selected");
                                } else {
                                    star.classList.remove("selected");
                                }
                            });
                        }
                    });

                    // Delete Rating functionality
                    document.querySelectorAll(".delete-rating-btn").forEach(btn => {
                        btn.addEventListener("click", () => {
                            const seedId = btn.dataset.seedid;
                            if (confirm("Delete your rating for this product?")) {
                                fetch(`/api/seeds/${seedId}/rating`, {
                                    method: "DELETE"
                                })
                                    .then(res => res.json())
                                    .then(data => {
                                        alert("Rating deleted.");
                                        location.reload(); // Refresh to show updated bookings
                                    })
                                    .catch(err => {
                                        alert("Failed to delete rating.");
                                    });
                            }
                        });
                    });
                }

                document.getElementById("booking-modal").classList.remove("hidden");
            });
    });

    document.getElementById("close-booking-modal").addEventListener("click", () => {
        document.getElementById("booking-modal").classList.add("hidden");
    });
});