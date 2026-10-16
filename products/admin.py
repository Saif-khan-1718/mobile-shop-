from django.contrib import admin

from .models import Category, Product, ProductImage


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "image_type", "alt_text", "sort_order", "is_primary")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "sort_order", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("is_active", "sort_order")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "price",
        "stock",
        "featured",
        "bestseller",
        "new_arrival",
        "is_active",
        "created_at",
    )
    list_filter = (
        "category",
        "is_active",
        "featured",
        "bestseller",
        "new_arrival",
        "color",
        "finish",
        "material",
        "created_at",
    )
    search_fields = ("name", "slug", "description", "color", "material", "finish", "size")
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ("price", "stock", "featured", "bestseller", "new_arrival", "is_active")
    inlines = [ProductImageInline]
    autocomplete_fields = ("category",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("category", "name", "slug", "description")}),
        (
            "Pricing & stock",
            {"fields": ("price", "old_price", "price_unit", "stock")},
        ),
        (
            "Specifications",
            {
                "fields": (
                    "size",
                    "color",
                    "material",
                    "finish",
                    "thickness",
                    "suitable_room",
                    "usage",
                ),
                "description": "Use Compatible with for phone models, and Size / capacity for battery or cable length.",
            },
        ),
        ("Media", {"fields": ("main_image",)}),
        (
            "Flags",
            {"fields": ("is_active", "featured", "bestseller", "new_arrival")},
        ),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "image_type", "is_primary", "sort_order")
    list_filter = ("image_type", "is_primary")
    search_fields = ("product__name", "alt_text")
    autocomplete_fields = ("product",)
