from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q

from products.models import Category, Product


def _input(widget=forms.TextInput, **attrs):
    base = {"class": "dash-input"}
    base.update(attrs)
    return widget(attrs=base)


class DashboardLoginForm(AuthenticationForm):
    username = forms.CharField(widget=_input(placeholder="Username"))
    password = forms.CharField(widget=_input(forms.PasswordInput, placeholder="Password"))


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "category",
            "name",
            "description",
            "price",
            "old_price",
            "stock",
            "main_image",
            "color",
            "size",
            "material",
            "suitable_room",
            "usage",
            "is_active",
            "featured",
            "bestseller",
            "new_arrival",
        ]
        widgets = {
            "category": forms.Select(attrs={"class": "dash-input"}),
            "name": _input(placeholder="Product name"),
            "description": forms.Textarea(
                attrs={"class": "dash-input", "rows": 4, "placeholder": "Short description"}
            ),
            "price": _input(forms.NumberInput, min="0", step="0.01"),
            "old_price": _input(forms.NumberInput, min="0", step="0.01"),
            "stock": _input(forms.NumberInput, min="0", step="1"),
            "main_image": forms.ClearableFileInput(attrs={"class": "dash-input", "accept": "image/*"}),
            "color": _input(placeholder="Color"),
            "size": _input(placeholder="Size / battery / cable length"),
            "material": _input(placeholder="Material"),
            "suitable_room": _input(placeholder="Compatible phones"),
            "usage": _input(placeholder="Best for"),
        }
        labels = {
            "old_price": "Old price (optional)",
            "main_image": "Product photo",
            "suitable_room": "Compatible with",
            "usage": "Best for",
            "is_active": "Show on website",
            "new_arrival": "New arrival",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = Category.objects.filter(is_active=True)
        if self.instance.pk and self.instance.category_id:
            categories = Category.objects.filter(
                Q(is_active=True) | Q(pk=self.instance.category_id)
            )
        self.fields["category"].queryset = categories.order_by("sort_order", "name")
        self.fields["category"].empty_label = "Select category"
        self.fields["old_price"].required = False
        if self.instance.pk:
            self.fields["main_image"].required = False
        else:
            self.fields["main_image"].required = True


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "description", "image", "sort_order", "is_active"]
        widgets = {
            "name": _input(placeholder="Category name"),
            "description": forms.Textarea(
                attrs={"class": "dash-input", "rows": 3, "placeholder": "Shown under the heading"}
            ),
            "image": forms.ClearableFileInput(attrs={"class": "dash-input", "accept": "image/*"}),
            "sort_order": _input(forms.NumberInput, min="0", step="1"),
        }
        labels = {
            "sort_order": "Display order (1 = first)",
            "is_active": "Show on website",
        }
