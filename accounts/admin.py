from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import User

from .models import Address, Profile, WishlistItem


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    extra = 0


class AddressInline(admin.TabularInline):
    model = Address
    extra = 0


class UserAdmin(DjangoUserAdmin):
    inlines = [ProfileInline, AddressInline]


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "updated_at")
    search_fields = ("user__username", "user__email", "phone")


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("full_name", "user", "city", "state", "pincode", "is_default")
    list_filter = ("state", "city", "is_default")
    search_fields = ("full_name", "user__username", "pincode", "phone")


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ("user", "product", "created_at")
    search_fields = ("user__username", "product__name")
    autocomplete_fields = ("user", "product")
