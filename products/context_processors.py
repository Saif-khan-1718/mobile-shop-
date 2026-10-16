def storefront(request):
    cart = request.session.get("cart", {})
    count = 0
    for quantity in cart.values():
        try:
            count += int(quantity)
        except (TypeError, ValueError):
            continue
    return {"cart_count": count}
