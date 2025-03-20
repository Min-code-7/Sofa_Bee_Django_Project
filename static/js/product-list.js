document.addEventListener('DOMContentLoaded', function() {
    // Get CSRF token from hidden form
    const csrfToken = document.querySelector('#csrf-form [name=csrfmiddlewaretoken]')?.value || '';
    
    // Add click event handler for all "Add to Cart" buttons
    $('.add-to-cart').on('click', function() {
        const productId = $(this).data('id');
        console.log(`Button clicked for product ${productId}`);
        addToCart(productId);
    });

    // Filter by category function
    window.filterByCategory = function(category) {
        if (category) {
            window.location.href = "/products/?category=" + encodeURIComponent(category);
        } else {
            window.location.href = "/products/";
        }
    };

    // Search products function
    window.searchProducts = function() {
        var query = $("#search-input").val();
        $.ajax({
            url: "/products/search/",
            data: { q: query },
            dataType: "json",
            success: function(data) {
                $("#product-list").html("");

                if (data.products.length === 0) {
                    $("#product-list").html(`
                        <div class="col-12 text-center py-5">
                            <div class="card shadow-sm">
                                <div class="card-body">
                                    <h5 class="card-title text-muted">No matching products found</h5>
                                    <p class="card-text">Try different search terms or browse categories.</p>
                                    <button class="btn btn-outline-secondary mt-3" onclick="window.location.reload()">
                                        Reset Search
                                    </button>
                                </div>
                            </div>
                        </div>
                    `);
                } else {
                    $.each(data.products, function(index, product) {
                        var imageHtml = product.image ? 
                            `<div class="product-image-container">
                                <img src="${product.image}" class="card-img-top" alt="${product.name}">
                             </div>` : 
                            '<div class="product-image-container d-flex align-items-center justify-content-center bg-light">'+
                            '<span class="text-muted">No Image</span></div>';
                            
                        $("#product-list").append(`
                            <div class="col-md-4 mb-4">
                                <div class="card shadow-sm h-100">
                                    ${imageHtml}
                                    <div class="card-body d-flex flex-column">
                                        <h5 class="card-title">${product.name}</h5>
                                        <p class="card-text text-muted small">${product.category || ''}</p>
                                        <p class="card-text flex-grow-1">${product.description}</p>
                                        <p><strong>Price: <span class="text-primary">£${product.price.toFixed(2)}</span></strong></p>
                                        <div class="d-flex justify-content-center">
                                            <a href="/products/${product.id}/" class="btn btn-primary">View Details</a>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        `);
                    });
                }
            }
        });
    };
    
    // Add to cart function
    window.addToCart = function(productId) {
        console.log("Adding product to cart:", productId);
    
        fetch(`/cart/add/${productId}/`, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => {
            console.log("Response status:", response.status);
            return response.json();
        })
        .then(data => {
            console.log("Response data:", data);
            if (data.status === 'success') {
                alert(data.message);
                location.reload(); 
            } else {
                alert(data.message || 'Error adding to cart');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while adding to cart');
        });
    };
});
