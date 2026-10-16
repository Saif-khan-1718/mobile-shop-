from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "Kaif Mobile Admin"
admin.site.site_title = "Kaif Mobile"
admin.site.index_title = "Store management"

from products.views import (
    home,
    category_products,
    product_detail,
    add_to_cart,
    cart,
    remove_from_cart,
    increase_quantity,
    decrease_quantity,
)


urlpatterns = [

    path(
        "",
        home,
        name="home"
    ),

    path(
        "category/<str:slug>/",
        category_products,
        name="category_products"
    ),

    path(
        "product/<str:slug>/",
        product_detail,
        name="product_detail"
    ),

    path(
        "cart/",
        cart,
        name="cart"
    ),

    path(
        "cart/add/<str:slug>/",
        add_to_cart,
        name="add_to_cart"
    ),

    path(
        "cart/remove/<str:slug>/",
        remove_from_cart,
        name="remove_from_cart"
    ),

    path(
        "cart/increase/<str:slug>/",
        increase_quantity,
        name="increase_quantity"
    ),

    path(
        "cart/decrease/<str:slug>/",
        decrease_quantity,
        name="decrease_quantity"
    ),

    path(
        "manage/",
        include("dashboard.urls")
    ),

    path(
        "admin/",
        admin.site.urls
    ),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )