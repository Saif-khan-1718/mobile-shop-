from django.db.models import Prefetch
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST

from products.models import Product, Category


def home(request):
    categories = Category.objects.filter(is_active=True).prefetch_related(
        Prefetch(
            "products",
            queryset=Product.objects.filter(is_active=True).select_related("category"),
        )
    )

    return render(request, "home.html", {
        "categories": categories
    })


def category_products(request, slug):
    category = get_object_or_404(
        Category,
        slug=slug,
        is_active=True
    )

    products = Product.objects.filter(
        category=category,
        is_active=True
    ).select_related("category")

    categories = Category.objects.filter(
        is_active=True
    ).order_by("sort_order", "name")

    return render(request, "category_products.html", {
        "category": category,
        "products": products,
        "categories": categories,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)

    return render(request, "product_detail.html", {
        "product": product
    })


@require_POST
def add_to_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)

    quantity = int(request.POST.get("quantity", 1))

    if quantity < 1:
        quantity = 1

    if quantity > product.stock:
        quantity = product.stock

    cart = request.session.get("cart", {})

    product_id = str(product.id)

    if product_id in cart:
        cart[product_id] += quantity
    else:
        cart[product_id] = quantity

    request.session["cart"] = cart
    request.session.modified = True

    return redirect("cart")


def cart(request):
    cart_data = request.session.get("cart", {})

    cart_items = []
    total = 0

    for product_id, quantity in cart_data.items():

        try:
            product = Product.objects.get(
                id=product_id,
                is_active=True
            )
        except Product.DoesNotExist:
            continue

        subtotal = product.price * quantity
        total += subtotal

        cart_items.append({
            "product": product,
            "quantity": quantity,
            "subtotal": subtotal,
        })

    return render(request, "cart.html", {
        "cart_items": cart_items,
        "total": total,
    })


def remove_from_cart(request, slug):
    product = get_object_or_404(Product, slug=slug)

    cart_data = request.session.get("cart", {})

    product_id = str(product.id)

    if product_id in cart_data:
        del cart_data[product_id]

    request.session["cart"] = cart_data
    request.session.modified = True

    return redirect("cart")


def increase_quantity(request, slug):
    product = get_object_or_404(Product, slug=slug)

    cart_data = request.session.get("cart", {})

    product_id = str(product.id)

    if product_id in cart_data:
        if cart_data[product_id] < product.stock:
            cart_data[product_id] += 1

    request.session["cart"] = cart_data
    request.session.modified = True

    return redirect("cart")


def decrease_quantity(request, slug):
    product = get_object_or_404(Product, slug=slug)

    cart_data = request.session.get("cart", {})

    product_id = str(product.id)

    if product_id in cart_data:
        if cart_data[product_id] > 1:
            cart_data[product_id] -= 1
        else:
            del cart_data[product_id]

    request.session["cart"] = cart_data
    request.session.modified = True

    return redirect("cart")
