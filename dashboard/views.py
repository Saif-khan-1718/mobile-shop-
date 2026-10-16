from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login, logout
from django.db.models import Count, Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from orders.models import Order
from products.models import Category, Product

from .forms import CategoryForm, DashboardLoginForm, ProductForm


def dashboard_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("dashboard_home")

    form = DashboardLoginForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        if not user.is_staff:
            return HttpResponseForbidden("This account cannot manage the store.")
        login(request, user)
        next_url = request.POST.get("next") or request.GET.get("next")
        if next_url and url_has_allowed_host_and_scheme(
            next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
        ):
            return redirect(next_url)
        return redirect("dashboard_home")

    return render(request, "dashboard/login.html", {"form": form})


@require_POST
def dashboard_logout(request):
    logout(request)
    messages.success(request, "You have been signed out.")
    return redirect("dashboard_login")


@staff_member_required(login_url="dashboard_login")
def dashboard_home(request):
    products = Product.objects.all()
    live_categories = Category.objects.filter(is_active=True).annotate(
        product_total=Count("products")
    ).order_by("sort_order", "name")
    return render(request, "dashboard/home.html", {
        "product_count": products.filter(is_active=True).count(),
        "hidden_count": products.filter(is_active=False).count(),
        "category_count": live_categories.count(),
        "low_stock": products.filter(is_active=True, stock__lte=5).count(),
        "order_count": Order.objects.count(),
        "recent_products": products.select_related("category")[:6],
        "live_categories": live_categories,
    })


@staff_member_required(login_url="dashboard_login")
def product_list(request):
    query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "").strip()
    products = Product.objects.select_related("category")
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    if category_slug:
        products = products.filter(category__slug=category_slug)

    return render(request, "dashboard/products.html", {
        "products": products,
        "categories": Category.objects.filter(is_active=True).order_by("sort_order", "name"),
        "query": query,
        "selected_category": category_slug,
    })


@staff_member_required(login_url="dashboard_login")
def product_create(request):
    initial = {}
    category_slug = (request.GET.get("category") or "").strip()
    if category_slug:
        category = Category.objects.filter(slug=category_slug, is_active=True).first()
        if category:
            initial["category"] = category
    form = ProductForm(request.POST or None, request.FILES or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        product = form.save()
        messages.success(request, f"“{product.name}” is now on the website.")
        return redirect("dashboard_products")
    return render(request, "dashboard/product_form.html", {
        "form": form,
        "title": "Add product",
        "product": None,
    })


@staff_member_required(login_url="dashboard_login")
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if request.method == "POST" and form.is_valid():
        product = form.save()
        messages.success(request, f"“{product.name}” has been updated.")
        return redirect("dashboard_products")
    return render(request, "dashboard/product_form.html", {
        "form": form,
        "title": "Edit product",
        "product": product,
    })


@staff_member_required(login_url="dashboard_login")
@require_POST
def product_quick_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    try:
        product.price = Decimal(request.POST.get("price") or product.price)
        old_price = request.POST.get("old_price", "").strip()
        product.old_price = Decimal(old_price) if old_price else None
        product.stock = max(0, int(request.POST.get("stock") or 0))
    except (InvalidOperation, ValueError, TypeError):
        messages.error(request, "Price or stock value is not valid.")
        return redirect("dashboard_products")
    product.is_active = request.POST.get("is_active") == "on"
    product.save(update_fields=["price", "old_price", "stock", "is_active", "updated_at"])
    messages.success(request, f"Updated {product.name}.")
    return redirect("dashboard_products")


@staff_member_required(login_url="dashboard_login")
@require_POST
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if product.order_items.exists():
        product.is_active = False
        product.save(update_fields=["is_active", "updated_at"])
        messages.success(
            request,
            f"“{product.name}” is hidden because it is used in an order.",
        )
        return redirect("dashboard_products")
    name = product.name
    product.delete()
    messages.success(request, f"Deleted “{name}”.")
    return redirect("dashboard_products")


@staff_member_required(login_url="dashboard_login")
def category_list(request):
    categories = Category.objects.annotate(product_total=Count("products")).order_by(
        "-is_active", "sort_order", "name"
    )
    return render(request, "dashboard/categories.html", {
        "categories": categories.filter(is_active=True),
        "hidden_categories": categories.filter(is_active=False),
    })


@staff_member_required(login_url="dashboard_login")
def category_create(request):
    form = CategoryForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        category = form.save()
        messages.success(request, f"Category “{category.name}” added.")
        return redirect("dashboard_categories")
    return render(request, "dashboard/category_form.html", {
        "form": form,
        "title": "Add category",
    })


@staff_member_required(login_url="dashboard_login")
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, request.FILES or None, instance=category)
    if request.method == "POST" and form.is_valid():
        category = form.save()
        messages.success(request, f"Category “{category.name}” updated.")
        return redirect("dashboard_categories")
    return render(request, "dashboard/category_form.html", {
        "form": form,
        "title": "Edit category",
        "category": category,
    })
