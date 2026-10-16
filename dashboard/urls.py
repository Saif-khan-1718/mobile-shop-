from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.dashboard_login, name="dashboard_login"),
    path("logout/", views.dashboard_logout, name="dashboard_logout"),
    path("", views.dashboard_home, name="dashboard_home"),
    path("products/", views.product_list, name="dashboard_products"),
    path("products/new/", views.product_create, name="dashboard_product_new"),
    path("products/<int:pk>/edit/", views.product_edit, name="dashboard_product_edit"),
    path("products/<int:pk>/quick/", views.product_quick_update, name="dashboard_product_quick"),
    path("products/<int:pk>/delete/", views.product_delete, name="dashboard_product_delete"),
    path("categories/", views.category_list, name="dashboard_categories"),
    path("categories/new/", views.category_create, name="dashboard_category_new"),
    path("categories/<int:pk>/edit/", views.category_edit, name="dashboard_category_edit"),
]
