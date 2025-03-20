document.addEventListener('DOMContentLoaded', function() {
    // Get global variables
    const csrfToken = window.csrfToken || document.querySelector('input[name="csrfmiddlewaretoken"]')?.value || '';
    const currentProductId = window.productId || 0;
    
    console.log("Product Detail JS loaded", { csrfToken: csrfToken ? "Set" : "Not set", productId: currentProductId });
    
    // Initialize variant selection if we have variant data
    if (window.variantData) {
        initVariantSelection();
    }
    
    // Initialize filter reviews button
    document.getElementById('apply-filters-btn')?.addEventListener('click', function() {
        filterReviews();
    });
    
    // Basic add to cart function for products without variants
    window.addToCart = function(productId) {
        console.log("Adding product to cart:", productId);
        
        // Get CSRF token from form or cookie if not already set
        const token = csrfToken || document.querySelector('#csrf-form [name=csrfmiddlewaretoken]')?.value || getCookie('csrftoken');
        console.log("Using CSRF token:", token ? "Found" : "Not found");

        fetch(`/cart/add/${productId}/`, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': token,
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            console.log("Response status:", response.status);
            return response.json();
        })
        .then(data => {
            console.log("Response data:", data);
            if (data.status === 'success') {
                showSuccessNotification(data.message);
            } else {
                showErrorNotification(data.message || 'Error adding to cart');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showErrorNotification('An error occurred while adding to cart');
        });
    };

    // Filter reviews functionality
    function filterReviews() {
        let rating = $("#filter-rating").val();
        let keyword = $("#filter-keyword").val();
        let onlyImages = $("#filter-images").prop("checked");

        console.log("Sending rating:", rating, "Type", typeof rating);

        $.ajax({
            url: `/products/reviews/filter/${currentProductId || window.location.pathname.split('/')[2]}/`,
            data: {
                rating: rating ? parseInt(rating, 10) : null,
                keyword: keyword,
                images: onlyImages
            },
            dataType: "json",
            success: function(response) {
                console.log("Filtered Reviews:", response.reviews);

                $("#reviews-list").html("");
                if (response.reviews.length === 0) {
                    $("#reviews-list").html("<p>No matching reviews.</p>");
                } else {
                    $.each(response.reviews, function(index, review) {
                        let stars = "⭐".repeat(parseInt(review.rating));
                        let reviewHtml = `
                            <div class="review-card p-3 border rounded mb-3">
                                <strong>${review.user}</strong> rated: ${stars}
                                <p>${review.comment}</p>
                                <small>${review.created_at}</small>
                        `;
                        if (review.image) {
                            reviewHtml += `<div class="mt-2"><img src="${review.image}" class="img-thumbnail" width="100"></div>`;
                        }
                        reviewHtml += `</div>`;
                        $("#reviews-list").append(reviewHtml);
                    });
                }
            }
        });
    }

    // Initialize variant selection and cart functionality
    function initVariantSelection() {
        const attributeGroups = document.querySelectorAll('.attribute-options');
        const addToCartBtn = document.getElementById('add-to-cart-btn');
        const variantPriceEl = document.getElementById('variant-price');
        const variantStockEl = document.getElementById('variant-stock');

        // Store the selected variant ID
        let selectedVariantId = null;

        // Initialize with default variant
        updateSelectedVariant();

        // Add event listeners to all attribute options
        attributeGroups.forEach(group => {
            const radioButtons = group.querySelectorAll('.attribute-value');
            radioButtons.forEach(radio => {
                radio.addEventListener('change', updateSelectedVariant);
            });
        });

        // Handle the Add to Cart button click
        if (addToCartBtn) {
            addToCartBtn.addEventListener('click', function() {
                if (selectedVariantId) {
                    addToCartWithVariant(currentProductId, selectedVariantId);
                } else {
                    addToCart(currentProductId);
                }
            });
        }

        // Function to update the selected variant based on selected options
        function updateSelectedVariant() {
            if (!window.variantData || window.variantData.length === 0) return;

            // Get all selected attribute values
            const selectedAttributeValues = [];
            attributeGroups.forEach(group => {
                const selectedRadio = group.querySelector('input[type="radio"]:checked');
                if (selectedRadio) {
                    selectedAttributeValues.push(parseInt(selectedRadio.value));
                }
            });

            // Find the matching variant
            for (const variant of window.variantData) {
                // Check if all selected attributes match this variant
                if (selectedAttributeValues.length === variant.attribute_values.length) {
                    let allMatch = true;
                    for (const valueId of selectedAttributeValues) {
                        if (!variant.attribute_values.includes(valueId)) {
                            allMatch = false;
                            break;
                        }
                    }

                    if (allMatch) {
                        // Update the variant ID, price, and stock
                        selectedVariantId = variant.id;
                        if (variantPriceEl) variantPriceEl.textContent = variant.price;
                        if (variantStockEl) variantStockEl.textContent = variant.stock;
                        return;
                    }
                }
            }

            // If no match found, use the default variant
            const defaultVariant = window.variantData.find(v => v.is_default) || window.variantData[0];
            if (defaultVariant) {
                selectedVariantId = defaultVariant.id;
                if (variantPriceEl) variantPriceEl.textContent = defaultVariant.price;
                if (variantStockEl) variantStockEl.textContent = defaultVariant.stock;
            }
        }

        // Function to add a product variant to cart
        function addToCartWithVariant(productId, variantId) {
            console.log("Adding product variant to cart:", productId, variantId);
            
            // Get CSRF token from form or cookie if not already set
            const token = csrfToken || document.querySelector('#csrf-form [name=csrfmiddlewaretoken]')?.value || getCookie('csrftoken');
            console.log("Using CSRF token for variant:", token ? "Found" : "Not found");

            fetch(`/cart/add/${productId}/`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': token,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    variant_id: variantId
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    showSuccessNotification(data.message);
                    // Don't reload the page immediately to allow the user to see the notification
                    setTimeout(() => {
                        location.reload();
                    }, 1500);
                } else {
                    showErrorNotification(data.message || 'Error adding to cart');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showErrorNotification('An error occurred while adding to cart');
            });
        }
    }
});
