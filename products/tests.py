from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone

from products.models import Category, Product, ProductImage

TINY_GIF = (
    b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff"
    b"!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01"
    b"\x00\x00\x02\x01D\x00;"
)


def make_image(name="tile.gif"):
    return SimpleUploadedFile(name, TINY_GIF, content_type="image/gif")


class CategoryModelTests(TestCase):
    def test_create_category_and_auto_slug(self):
        category = Category.objects.create(name="Floor Tiles")
        self.assertEqual(category.slug, "floor-tiles")
        self.assertEqual(str(category), "Floor Tiles")

    def test_category_slug_is_unique(self):
        Category.objects.create(name="Kitchen Tiles", slug="kitchen-tiles")
        with self.assertRaises(Exception):
            Category.objects.create(name="Kitchen", slug="kitchen-tiles")


class ProductModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Bathroom Tiles")

    def test_create_product(self):
        product = Product.objects.create(
            category=self.category,
            name="Marble Carrara Tile",
            description="Premium marble-look tile.",
            price=Decimal("85.00"),
            old_price=Decimal("110.00"),
            size="600x600 mm",
            color="White",
            material="Porcelain",
            finish="Polished",
            thickness="10 mm",
            stock=40,
            main_image=make_image(),
            featured=True,
        )
        self.assertEqual(product.slug, "marble-carrara-tile")
        self.assertTrue(product.in_stock)
        self.assertEqual(product.discount_percent, 23)
        self.assertEqual(str(product), "Marble Carrara Tile")

    def test_discount_percent_zero_without_old_price(self):
        product = Product.objects.create(
            category=self.category,
            name="Plain Ceramic",
            description="Simple tile.",
            price=Decimal("45.00"),
            stock=1,
            main_image=make_image("plain.gif"),
        )
        self.assertEqual(product.discount_percent, 0)


class ProductImageModelTests(TestCase):
    def test_gallery_image_and_alt_text(self):
        category = Category.objects.create(name="Wall Tiles")
        product = Product.objects.create(
            category=category,
            name="Glossy Wall Tile",
            description="For bathrooms.",
            price=Decimal("60.00"),
            main_image=make_image("main.gif"),
        )
        image = ProductImage.objects.create(
            product=product,
            image=make_image("gallery.gif"),
            image_type=ProductImage.ImageKind.BATHROOM,
        )
        self.assertIn("In use", image.alt_text)
        self.assertEqual(product.images.count(), 1)


class CouponModelTests(TestCase):
    def test_percentage_discount_with_cap(self):
        from orders.models import Coupon

        coupon = Coupon.objects.create(
            code="welcome10",
            discount_type=Coupon.DiscountType.PERCENTAGE,
            discount_value=Decimal("10.00"),
            minimum_order=Decimal("100.00"),
            maximum_discount=Decimal("50.00"),
            valid_from=timezone.now() - timedelta(days=1),
            valid_until=timezone.now() + timedelta(days=1),
        )
        self.assertEqual(coupon.code, "WELCOME10")
        self.assertEqual(coupon.calculate_discount(Decimal("200.00")), Decimal("20.00"))
        self.assertEqual(coupon.calculate_discount(Decimal("900.00")), Decimal("50.00"))
        self.assertEqual(coupon.calculate_discount(Decimal("50.00")), Decimal("0.00"))


class ProfileSignalTests(TestCase):
    def test_profile_created_for_new_user(self):
        user = get_user_model().objects.create_user(
            username="buyer",
            email="buyer@example.com",
            password="secure-pass-123",
        )
        self.assertTrue(hasattr(user, "profile"))
