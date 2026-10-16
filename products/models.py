from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, db_index=True)
    image = models.ImageField(upload_to="categories/", blank=True, null=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "category"
        verbose_name_plural = "categories"
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active", "sort_order"]),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, db_index=True)
    description = models.TextField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    old_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    price_unit = models.CharField(max_length=20, default="piece")

    size = models.CharField("Size / capacity", max_length=50, blank=True)
    color = models.CharField(max_length=50, blank=True, db_index=True)
    material = models.CharField(max_length=80, blank=True, db_index=True)
    finish = models.CharField(max_length=50, blank=True, db_index=True)
    thickness = models.CharField("Weight", max_length=50, blank=True)
    suitable_room = models.CharField("Compatible with", max_length=120, blank=True)
    usage = models.CharField("Best for", max_length=120, blank=True)

    stock = models.PositiveIntegerField(default=0)
    main_image = models.ImageField(upload_to="products/")

    is_active = models.BooleanField(default=True, db_index=True)
    featured = models.BooleanField(default=False, db_index=True)
    bestseller = models.BooleanField(default=False, db_index=True)
    new_arrival = models.BooleanField(default=False, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active", "featured"]),
            models.Index(fields=["is_active", "bestseller"]),
            models.Index(fields=["is_active", "new_arrival"]),
            models.Index(fields=["category", "is_active"]),
            models.Index(fields=["price"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def in_stock(self):
        return self.stock > 0

    @property
    def discount_percent(self):
        if self.old_price and self.old_price > self.price:
            return round(((self.old_price - self.price) / self.old_price) * 100)
        return 0


class ProductImage(models.Model):
    class ImageKind(models.TextChoices):
        MAIN = "main", "Main photo"
        CLOSEUP = "closeup", "Close-up"
        ANGLE = "angle", "Different angle"
        TEXTURE = "texture", "Detail"
        LIVING_ROOM = "living_room", "Lifestyle"
        KITCHEN = "kitchen", "Unboxed"
        BATHROOM = "bathroom", "In use"
        FLOOR = "floor", "Packaging"

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(upload_to="products/gallery/")
    alt_text = models.CharField(max_length=200, blank=True)
    image_type = models.CharField(
        max_length=20,
        choices=ImageKind.choices,
        default=ImageKind.MAIN,
    )
    sort_order = models.PositiveIntegerField(default=0)
    is_primary = models.BooleanField(default=False)

    class Meta:
        ordering = ["sort_order", "id"]

    def __str__(self):
        return f"{self.product.name} — {self.get_image_type_display()}"

    def save(self, *args, **kwargs):
        if not self.alt_text:
            self.alt_text = f"{self.product.name} {self.get_image_type_display()}"
        super().save(*args, **kwargs)
