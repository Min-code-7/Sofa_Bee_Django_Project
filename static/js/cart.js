document.addEventListener('DOMContentLoaded', function() {
    // Get CSRF token from global variable, form or cookie
    const csrfToken = window.csrfToken || 
                      document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || 
                      document.querySelector('#csrf-form [name=csrfmiddlewaretoken]')?.value || 
                      getCookie('csrftoken') || '';
    
    console.log("Cart JS loaded", { csrfToken: csrfToken ? "Set" : "Not set" });
    
    // Cart URL paths
    const cartDetailUrl = '/cart/';
    const cartUpdateUrl = '/cart/update/';
    const cartRemoveUrl = '/cart/remove/';
    const cartUpdateVariantUrl = '/cart/update_variant/';
    
    // Select all checkbox functionality
    const selectAllCheckbox = document.getElementById('select-all');
    const itemCheckboxes = document.querySelectorAll('.item-checkbox');
    const shopCheckboxes = document.querySelectorAll('.shop-checkbox');
    
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            const isChecked = this.checked;
            itemCheckboxes.forEach(checkbox => {
                checkbox.checked = isChecked;
            });
            shopCheckboxes.forEach(checkbox => {
                checkbox.checked = isChecked;
            });
            updateTotalPrice();
        });
    }
    
    // Shop checkboxes
    shopCheckboxes.forEach(shopCheckbox => {
        shopCheckbox.addEventListener('change', function() {
            const shopName = this.value;
            const isChecked = this.checked;
            document.querySelectorAll(`.item-checkbox[data-shop="${shopName}"]`).forEach(checkbox => {
                checkbox.checked = isChecked;
            });
            updateTotalPrice();
        });
    });
    
    // Item checkboxes
    itemCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            updateTotalPrice();
        });
    });
    
    // Quantity buttons
    document.querySelectorAll('.quantity-btn').forEach(button => {
        button.addEventListener('click', function() {
            const itemId = this.getAttribute('data-item');
            const input = document.querySelector(`.quantity-input[data-item="${itemId}"]`);
            let quantity = parseInt(input.value);
            
            if (this.getAttribute('data-action') === 'increase') {
                quantity += 1;
            } else {
                quantity -= 1;
                if (quantity < 1) quantity = 1;
            }
            
            input.value = quantity;
            
            // Update on server using AJAX
            fetch(`${cartUpdateUrl}${itemId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken
                },
                body: `quantity=${quantity}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    document.querySelector(`.item-price[data-item="${itemId}"]`).textContent = 
                        '$' + data.item_price.toFixed(2);
                    document.getElementById('total-price').textContent = '£' + data.cart_price.toFixed(2);
                }
            });
        });
    });
    
    // Remove item buttons
    document.querySelectorAll('.remove-item').forEach(button => {
        button.addEventListener('click', function() {
            const itemId = this.getAttribute('data-item');
            const productName = this.closest('tr').querySelector('h5').textContent.trim();
            
            // Create a confirmation notification with buttons
            const notification = showNotification(
                `<div class="d-flex justify-content-between align-items-center">
                    <span>Remove <strong>${productName}</strong> from cart?</span>
                    <div>
                        <button type="button" class="btn btn-sm btn-danger confirm-remove-btn">Yes, remove</button>
                        <button type="button" class="btn btn-sm btn-outline-secondary ms-2 cancel-remove-btn">Cancel</button>
                    </div>
                </div>`,
                'warning',
                0 // Don't auto-dismiss
            );
            
            // Add event listeners to the buttons
            notification.querySelector('.confirm-remove-btn').addEventListener('click', () => {
                // Hide the notification
                notification.style.display = 'none';
                
                // Remove the item
                fetch(`${cartRemoveUrl}${itemId}/`, {
                    method: 'POST',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': csrfToken,
                        'Content-Type': 'application/json'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        // Remove the item row
                        button.closest('tr').remove();
                        document.getElementById('total-price').textContent = '£' + data.cart_price.toFixed(2);
                        
                        // Show success notification
                        showSuccessNotification(`<strong>${productName}</strong> has been removed from your cart.`);
                        
                        // If no items left, refresh the page
                        if (data.cart_total === 0) {
                            setTimeout(() => {
                                window.location.reload();
                            }, 1500);
                        }
                    }
                });
            });
            
            // Cancel button
            notification.querySelector('.cancel-remove-btn').addEventListener('click', () => {
                notification.style.display = 'none';
                document.getElementById('notification-area').style.display = 'none';
            });
        });
    });
    
    // Search functionality
    document.getElementById('search-btn')?.addEventListener('click', function() {
        const query = document.getElementById('cart-search').value;
        if (query) {
            window.location.href = `${cartDetailUrl}?q=${encodeURIComponent(query)}`;
        }
    });
    
    // Checkout button
    document.getElementById('checkout-btn')?.addEventListener('click', function() {
        const selectedItems = document.querySelectorAll('.item-checkbox:checked');
        if (selectedItems.length === 0) {
            showWarningNotification('Please select at least one item to checkout.');
            return;
        }
        
        document.getElementById('cart-form').submit();
    });
    
    // Variant selection functionality
    
    // Show variant options when "Change" button is clicked
    document.querySelectorAll('.change-variant-btn').forEach(button => {
        button.addEventListener('click', function() {
            const variantSelection = this.closest('.variant-selection');
            variantSelection.querySelector('.current-variant').style.display = 'none';
            variantSelection.querySelector('.variant-options').style.display = 'block';
        });
    });
    
    // Show variant options when "Select options" button is clicked
    document.querySelectorAll('.select-variant-btn').forEach(button => {
        button.addEventListener('click', function() {
            const variantSelection = this.closest('.variant-selection');
            this.style.display = 'none';
            variantSelection.querySelector('.variant-options').style.display = 'block';
        });
    });
    
    // Hide variant options when "Cancel" button is clicked
    document.querySelectorAll('.cancel-variant-btn').forEach(button => {
        button.addEventListener('click', function() {
            const variantSelection = this.closest('.variant-selection');
            variantSelection.querySelector('.variant-options').style.display = 'none';
            
            if (variantSelection.querySelector('.current-variant')) {
                variantSelection.querySelector('.current-variant').style.display = 'block';
            } else {
                variantSelection.querySelector('.select-variant-btn').style.display = 'inline-block';
            }
        });
    });
    
    // Apply variant changes when "Apply" button is clicked
    document.querySelectorAll('.apply-variant-btn').forEach(button => {
        button.addEventListener('click', function() {
            const variantSelection = this.closest('.variant-selection');
            const itemId = variantSelection.getAttribute('data-item-id');
            const productId = variantSelection.getAttribute('data-product-id');
            
            // Get all selected attribute values
            const selectedAttributeValues = [];
            variantSelection.querySelectorAll('.attribute-options').forEach(group => {
                const selectedRadio = group.querySelector('input[type="radio"]:checked');
                if (selectedRadio) {
                    selectedAttributeValues.push(parseInt(selectedRadio.value));
                }
            });
            
            // Update variant on server
            fetch(`${cartUpdateVariantUrl}${itemId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    product_id: productId,
                    attribute_values: selectedAttributeValues
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Show success notification
                    showSuccessNotification('Variant updated successfully. Refreshing page...');
                    // Refresh the page to show updated variant after a short delay
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                } else {
                    showErrorNotification(data.message || 'Error updating variant');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showErrorNotification('An error occurred while updating the variant');
            });
        });
    });
    
    // Helper function to update total price based on selected items
    function updateTotalPrice() {
        let total = 0;
        document.querySelectorAll('.item-checkbox:checked').forEach(checkbox => {
            const itemId = checkbox.value;
            const row = checkbox.closest('tr');
            const quantity = parseInt(row.querySelector('.quantity-input').value);
            const price = parseFloat(row.querySelector('.item-price').getAttribute('data-price'));
            total += quantity * price;
        });
        document.getElementById('total-price').textContent = '£' + total.toFixed(2);
    }
});
