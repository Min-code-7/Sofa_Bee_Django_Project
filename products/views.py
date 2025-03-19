from itertools import product
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseForbidden
from django.templatetags.static import static
from django.contrib import messages
from django.core.paginator import Paginator
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.http import require_POST

from reviews.forms import ReviewForm
from .forms import ProductForm, ProductAttributeForm, ProductAttributeValueForm, ProductVariantForm
from .models import Product, Category, ProductAttribute, ProductAttributeValue, ProductVariant

"""
# just test
PRODUCTS = [
    {"id": 1, "name": "test product 1", "description": "This is the first test product", "category": "Makeup", "price": 99.99, "image": static("products/images/pic1.png")},
    {"id": 2, "name": "test product 2", "description": "This is the second test product", "category": "Clothing", "price": 199.99, "image": static("products/images/pic2.png")},
    {"id": 3, "name": "test product 3", "description": "This is the third test product", "category": "Electronics", "price": 299.99, "image": static("products/images/pic3.png")},
    {"id": 4, "name": "test product 4", "description": "This is the first test product","category": "Makeup", "price": 99.99,
     "image": static("products/images/pic4.png")},
    {"id": 5, "name": "test product 5", "description": "This is the fifth test product", "category": "Electronics", "price": 199.99,
     "image": static("products/images/pic5.png")},
    {"id": 6, "name": "test product 6", "description": "This is the sixth test product", "category": "Clothing", "price": 299.99,
     "image": static("products/images/pic6.png")},
    {"id": 7, "name": "test product 7", "description": "This is the seventh test product","category": "Makeup", "price": 99.99,
     "image": static("products/images/pic7.png")},
    {"id": 8, "name": "test product 8", "description": "This is the eighth test product", "category": "Electronics", "price": 199.99,
     "image": static("products/images/pic8.png")},
    {"id": 9, "name": "test product 9", "description": "This is the ninth test product", "category": "Electronics", "price": 299.99,
     "image": static("products/images/pic9.png")},
    {"id": 10, "name": "test product 10", "description": "This is the tenth test product", "category": "Clothing", "price": 99.99,
     "image": static("products/images/pic10.png")},
    {"id": 11, "name": "test product 11", "description": "This is the eleventh test product", "category": "Makeup", "price": 199.99,
     "image": static("products/images/pic11.png")},
    {"id": 12, "name": "test product 12", "description": "This is the twelfth test product", "category": "Clothing", "price": 299.99,
     "image": static("products/images/pic12.png")},
]

REVIEWS = {
    1: [
        {"user": "UserA", "rating": 5, "comment": "Very good!", "created_at": "2025-03-06 12:05:30"},
        {"user": "UserC", "rating": 2, "comment": "Bad!", "created_at": "2025-03-06 12:05:30"}
    ],
    3: [
        {"user": "UserD", "rating": 4, "comment": "Good!", "created_at": "2025-03-06 12:05:30"},
        {"user": "UserB", "rating": 3, "comment": "Very good!", "created_at": "2025-03-06 12:05:30"},
        {"user": "UserA", "rating": 3, "comment": "Very good!", "created_at": "2025-03-06 12:05:30"}
    ],
    6: [
        {"user": "UserD", "rating": 5, "comment": "Very good!", "created_at": "2025-03-06 12:05:30"}
    ]
}
"""

# Create your views here.
'''
def product_list(request):
    products = Product.objects.all()
    return render(request, 'products/product_list.html', {'products': products})
'''
# testing product_list function
def product_list(request):

    # get keyword
    query = request.GET.get('q', '').strip().lower()
    # print("keywords: ", query)

    # get category
    category_name = request.GET.get('category', '')

    products = Product.objects.all()

    if query:
        products = products.filter(name__icontains=query) | products.filter(description__icontains=query)

    if category_name:
        products = products.filter(category__name__icontains=category_name)

    categories = Category.objects.all()

    # paginator
    paginator = Paginator(products, 9)
    page = request.GET.get('page')
    products = paginator.get_page(page)

    return render(request, "products/product_list.html", {"products": products, "query": query, "categories": categories, "selected_category": category_name})


def product_detail(request, product_id):


    # use sqlite
    product = get_object_or_404(Product, id=product_id)
    # use test data
    # product = next((p for p in PRODUCTS if p["id"] == product_id), None)

    if product is None:
        return render(request, "404.html", {"message": "No Product matches the given query."}, status=404)

    # get review
    reviews = product.reviews.all()

    # get new variant of product
    variants = ProductVariant.objects.filter(product=product)
    has_variants = variants.exists()

    """
    # handle review filter
    for review in reviews:
        review["rating"] = int(review["rating"])
        review["stars"] = range(review["rating"])
    """
    # get all attributes
    attributes = {}
    if has_variants:
        for variant in variants:
            for attr_value in variant.attribute_values.all():
                attr = attr_value.attribute
                if attr.id not in attributes:
                    attributes[attr.id] = {
                        'id': attr.id,
                        'name': attr.name,
                        'values': []
                    }

                value_dict = {
                    'id': attr_value.id,
                    'value': attr_value.value
                }
                if value_dict not in attributes[attr.id]['values']:
                    attributes[attr.id]['values'].append(value_dict)


    variants_json = []
    for variant in variants:
        variants_json.append({
            'id': variant.id,
            'price': str(variant.price),
            'stock': variant.stock,
            'is_default': variant.is_default,
            'attribute_values': list(variant.attribute_values.values_list('id', flat=True))
        })

    # get default variant
    default_variant = None
    if has_variants:
        try:
            default_variant = variants.get(is_default=True)
        except ProductVariant.DoesNotExist:
            default_variant = variants.first()

    # submit review
    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, "Your review has been submitted!")
            return redirect('products:product_detail', product_id=product.id)
    else:
        form = ReviewForm()

    context = {
        "product": product,
        "reviews": reviews,
        "form": form,
        "has_variants": has_variants,
        "attributes": list(attributes.values()),
        "variants_json": json.dumps(variants_json, cls=DjangoJSONEncoder),
        "default_variant": default_variant
    }

    return render(request, "products/product_detail.html", context)

def product_search(request):
    query = request.GET.get('q', '')
    # products = Product.objects.filter(name__icontains=query)
    category = request.GET.get('category', '').strip().lower()

    products = Product.objects.all()

    """
    data = {
        'products': [
            {
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': float(product.price),
                'image': product.image.url if product.name else None,
                'created_at': product.created_at.strftime('%Y-%m-%d %H:%M:%S'),
             }
            for product in products
        ]
    }
    """
    if query:
        products = products.filter(name__icontains=query) | products.filter(description__icontains=query)

    if category:
        products = products.filter(category__name__iexact=category)

    data = {
        'products': [
            {
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': float(product.price),
                'image': product.image.url if product.image else None,
                'created_at': product.created_at.strftime('%Y-%m-%d %H:%M:%S') if hasattr(product,'created_at') else '',
            }
            for product in products
        ]
    }

    return JsonResponse(data)


@login_required
def add_product(request):
    if not hasattr(request.user, "userprofile") or request.user.userprofile.user_type != 'merchant':
        messages.error(request, "You are not allowed to add product.")
        return redirect('products:product_list')

    Category.create_default_categories()

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()

            # checkbox of variants
            use_variants = request.POST.get('use_variants') == 'on'

            if use_variants:
                default_variant = ProductVariant.objects.create(
                    product=product,
                    price=product.price,
                    stock=product.stock,
                    is_default=True
                )
                messages.success(request, "Product created successfully. Now you can add variants.")
                return redirect('products:manage_variants', product_id=product.id)
            else:
                messages.success(request, "Product added successfully.")
                return redirect('products:product_list')
    else:
        form = ProductForm()

    return render(request, 'products/add_product.html', {'form': form})


def filter_category(request):
    category = request.GET.get('category', None)

    if category:
        products = Product.objects.filter(category__name__icontains=category)
    else:
        products = Product.objects.all()

    data = {
        'products': [
            {
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': float(product.price),
                'image': product.image.url if product.image else None,
            }
            for product in products
        ]
    }

    return JsonResponse(data)


@login_required
def edit_product(request, product_id):
    if not hasattr(request.user, "userprofile") or request.user.userprofile.user_type != 'merchant':
        messages.error(request, "Only merchant users can edit products.")
        return redirect('products:product_detail', product_id=product_id)


    product = get_object_or_404(Product, id=product_id)
    if product.seller != request.user:
        return HttpResponseForbidden("You have no right to edit this product.")


    variants = ProductVariant.objects.filter(product=product)
    has_variants = variants.exists()

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product information has been successfully updated!")


            if 'convert_to_variants' in request.POST and not has_variants:

                default_variant = ProductVariant.objects.create(
                    product=product,
                    price=product.price,
                    stock=product.stock,
                    is_default=True
                )
                messages.success(request, "The product has been converted to a variant format. You can now add additional parameters.")
                return redirect('products:manage_variants', product_id=product.id)

            return redirect('products:product_detail', product_id=product.id)
    else:
        form = ProductForm(instance=product)

    return render(request, 'products/edit_product.html', {
        'form': form,
        'product': product,
        'has_variants': has_variants
    })


@login_required
def manage_variants(request, product_id):


    if not hasattr(request.user, "userprofile") or request.user.userprofile.user_type != 'merchant':
        messages.error(request, "Only merchant users can manage commodity variants.")
        return redirect('products:product_detail', product_id=product_id)


    product = get_object_or_404(Product, id=product_id)
    if product.seller != request.user:
        return HttpResponseForbidden("You do not have permission to manage variants of this product.")


    variants = ProductVariant.objects.filter(product=product)


    default_variant = variants.filter(is_default=True).first()
    if not default_variant and variants.exists():
        default_variant = variants.first()
        default_variant.is_default = True
        default_variant.save()
    elif not variants.exists():
        default_variant = ProductVariant.objects.create(
            product=product,
            price=product.price,
            stock=product.stock,
            is_default=True
        )


    attributes = ProductAttribute.objects.filter(product=product)


    attribute_form = ProductAttributeForm()
    if request.method == 'POST' and 'add_attribute' in request.POST:
        attribute_form = ProductAttributeForm(request.POST)
        if attribute_form.is_valid():
            attribute = attribute_form.save(commit=False)
            attribute.product = product
            attribute.save()
            messages.success(request, "The new property has been added.")
            return redirect('products:manage_variants', product_id=product.id)


    attr_value_form = ProductAttributeValueForm()

    attr_value_form.fields['attribute'].queryset = attributes

    if request.method == 'POST' and 'add_attr_value' in request.POST:
        attr_value_form = ProductAttributeValueForm(request.POST)
        attr_value_form.fields['attribute'].queryset = attributes

        if attr_value_form.is_valid():
            attr_value_form.save()
            messages.success(request, "The new value has been added.")
            return redirect('products:manage_variants', product_id=product.id)


    variant_form = ProductVariantForm()

    attribute_ids = attributes.values_list('id', flat=True)
    variant_form.fields['attribute_values'].queryset = ProductAttributeValue.objects.filter(
        attribute_id__in=attribute_ids
    )

    if request.method == 'POST' and 'add_variant' in request.POST:
        variant_form = ProductVariantForm(request.POST)

        variant_form.fields['attribute_values'].queryset = ProductAttributeValue.objects.filter(
            attribute_id__in=attribute_ids
        )

        if variant_form.is_valid():
            variant = variant_form.save(commit=False)
            variant.product = product
            variant.save()
            variant_form.save_m2m()
            messages.success(request, "The new variant has been added.")
            return redirect('products:manage_variants', product_id=product.id)

    context = {
        'product': product,
        'variants': variants,
        'attributes': attributes,
        'attribute_form': attribute_form,
        'attr_value_form': attr_value_form,
        'variant_form': variant_form,
    }

    return render(request, 'products/manage_variants.html', context)


@login_required
def delete_variant(request, variant_id):

    if not hasattr(request.user, "userprofile") or request.user.userprofile.user_type != 'merchant':
        return JsonResponse({"status": "error", "message": "Only merchant users can delete variants."})


    variant = get_object_or_404(ProductVariant, id=variant_id)
    if variant.product.seller != request.user:
        return JsonResponse({"status": "error", "message": "You do not have permission to remove this variant."})

    product_id = variant.product.id


    is_default = variant.is_default


    variant.delete()


    if is_default:
        other_variant = ProductVariant.objects.filter(product_id=product_id).first()
        if other_variant:
            other_variant.is_default = True
            other_variant.save()

    return JsonResponse({"status": "success", "message": "变体已删除"})


@login_required
def manage_products(request):

    if not hasattr(request.user, "userprofile") or request.user.userprofile.user_type != 'merchant':
        messages.error(request, "Only merchant users have access to the merchandise management.")
        return redirect('products:product_list')

    products = Product.objects.filter(seller=request.user)

    paginator = Paginator(products, 10)
    page = request.GET.get('page')
    products = paginator.get_page(page)

    return render(request, 'products/manage_products.html', {'products': products})



@login_required
@require_POST
def delete_attribute(request, attribute_id):
    attribute = get_object_or_404(ProductAttribute, id=attribute_id)

    if attribute.product.seller != request.user:
        return JsonResponse({"status": "error", "message": "You do not have permission to remove this attribute."})

    try:
        # 删除属性会自动删除关联的属性值和变体中的引用（通过CASCADE和M2M关系）
        attribute.delete()
        return JsonResponse({"status": "success", "message": "Attribute removed"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"An error occurred while deleting a property: {str(e)}"})


@login_required
@require_POST
def delete_attribute_value(request, value_id):
    value = get_object_or_404(ProductAttributeValue, id=value_id)

    if value.attribute.product.seller != request.user:
        return JsonResponse({"status": "error", "message": "You do not have permission to remove this attribute value."})

    try:
        value.delete()
        return JsonResponse({"status": "success", "message": "The attribute value has been removed"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": f"An error occurred while deleting an attribute value: {str(e)}"})