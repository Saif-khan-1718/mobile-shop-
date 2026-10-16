from decimal import Decimal
from io import BytesIO

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from PIL import Image, ImageDraw, ImageFont

from products.models import Category, Product


CATALOG = [
    {
        "name": "Mobile Covers",
        "slug": "phone-cases",
        "description": "Shockproof, clear, and stylish covers for popular phones.",
        "color": (14, 165, 233),
        "products": [
            {
                "name": "Armor Case for iPhone",
                "price": "699.00",
                "old_price": "999.00",
                "description": "Drop-tested bumper case with raised camera lip.",
                "color": "Matte Black",
                "material": "TPU + PC",
                "suitable_room": "iPhone 13/14/15",
                "stock": 60,
                "bestseller": True,
            },
            {
                "name": "Clear MagSafe Cover",
                "price": "899.00",
                "description": "Crystal-clear case with MagSafe ring and yellowing-resistant material.",
                "color": "Clear",
                "suitable_room": "iPhone 14/15",
                "stock": 35,
                "featured": True,
            },
            {
                "name": "Rugged Case for Samsung",
                "price": "649.00",
                "description": "Military-grade corners and a kickstand for videos.",
                "color": "Olive",
                "suitable_room": "Galaxy A & S series",
                "stock": 42,
            },
            {
                "name": "Slim Silicone Case",
                "price": "399.00",
                "description": "Soft-touch silicone with microfiber lining.",
                "color": "Lavender",
                "material": "Silicone",
                "suitable_room": "Most Android phones",
                "stock": 70,
                "new_arrival": True,
            },
        ],
    },
    {
        "name": "Earbuds & Headphones",
        "slug": "earbuds-headphones",
        "description": "Wireless earbuds, neckbands, and over-ear headphones.",
        "color": (37, 99, 235),
        "products": [
            {
                "name": "Pulse Air Buds Pro",
                "price": "2499.00",
                "old_price": "3499.00",
                "description": "ANC wireless earbuds with 28-hour battery and IPX4 splash protection.",
                "color": "Midnight Black",
                "size": "28h battery",
                "material": "Plastic + silicone",
                "suitable_room": "Android & iPhone",
                "usage": "Calls, commute, gym",
                "stock": 40,
                "featured": True,
                "bestseller": True,
            },
            {
                "name": "Street Neckband",
                "price": "999.00",
                "old_price": "1499.00",
                "description": "Lightweight Bluetooth neckband with magnetic earbuds and fast charging.",
                "color": "Blue",
                "size": "18h battery",
                "suitable_room": "Android phones",
                "usage": "Daily listening",
                "stock": 55,
                "bestseller": True,
            },
            {
                "name": "Studio Over-Ear",
                "price": "4299.00",
                "description": "Over-ear wireless headphones with deep bass and cushioned ear cups.",
                "color": "Graphite",
                "size": "40h battery",
                "usage": "Music & travel",
                "stock": 18,
                "new_arrival": True,
            },
            {
                "name": "Kids Safe Earbuds",
                "price": "799.00",
                "description": "Volume-limited wired earbuds with a tangle-free cable.",
                "color": "Mint",
                "usage": "School & home",
                "stock": 30,
            },
        ],
    },
    {
        "name": "Chargers & Cables",
        "slug": "chargers-cables",
        "description": "Fast chargers, USB-C cables, and car adapters.",
        "color": (245, 158, 11),
        "products": [
            {
                "name": "65W GaN Fast Charger",
                "price": "1899.00",
                "old_price": "2499.00",
                "description": "Compact dual-port GaN charger for phones and laptops.",
                "size": "65W",
                "color": "White",
                "suitable_room": "USB-C phones & laptops",
                "stock": 28,
                "featured": True,
            },
            {
                "name": "Braided USB-C Cable 1.5m",
                "price": "349.00",
                "description": "Nylon-braided cable with 60W charging support.",
                "size": "1.5 metres",
                "color": "Black",
                "stock": 120,
                "bestseller": True,
            },
            {
                "name": "Car Charger Dual USB",
                "price": "499.00",
                "description": "18W car charger with USB-A and USB-C ports.",
                "color": "Black",
                "usage": "Car travel",
                "stock": 48,
            },
            {
                "name": "3-in-1 Charging Cable",
                "price": "449.00",
                "description": "Lightning, USB-C, and Micro-USB in one cable.",
                "size": "1.2 metres",
                "suitable_room": "Mixed devices",
                "stock": 80,
            },
        ],
    },
    {
        "name": "Power Banks",
        "slug": "power-banks",
        "description": "Portable batteries for phones, earbuds, and tablets.",
        "color": (16, 185, 129),
        "products": [
            {
                "name": "Slim 10000mAh Power Bank",
                "price": "1299.00",
                "old_price": "1699.00",
                "description": "Pocket-size 22.5W power bank with USB-C in and out.",
                "size": "10000mAh",
                "color": "Silver",
                "stock": 36,
                "bestseller": True,
            },
            {
                "name": "20000mAh Travel Pack",
                "price": "2199.00",
                "description": "High-capacity pack that can charge a phone four times.",
                "size": "20000mAh",
                "color": "Navy",
                "usage": "Travel",
                "stock": 22,
                "featured": True,
            },
            {
                "name": "Magnetic Mini Power Bank",
                "price": "1599.00",
                "description": "MagSafe-style snap-on battery for iPhone.",
                "size": "5000mAh",
                "suitable_room": "iPhone 12 and newer",
                "stock": 25,
                "new_arrival": True,
            },
        ],
    },
    {
        "name": "Smart Watches",
        "slug": "smart-watches",
        "description": "Fitness bands and smartwatches with call support.",
        "color": (139, 92, 246),
        "products": [
            {
                "name": "Pulse Watch SE",
                "price": "2799.00",
                "old_price": "3499.00",
                "description": "1.9-inch display, heart-rate tracking, and Bluetooth calling.",
                "size": "1.9 inch",
                "color": "Black",
                "suitable_room": "Android & iOS",
                "stock": 20,
                "featured": True,
            },
            {
                "name": "Fit Band 6",
                "price": "1499.00",
                "description": "Lightweight fitness band with SpO2 and 14-day battery.",
                "size": "14-day battery",
                "color": "Teal",
                "stock": 40,
                "bestseller": True,
            },
            {
                "name": "Pro Sport Watch",
                "price": "4999.00",
                "description": "GPS, 100+ sports modes, and 5 ATM water resistance.",
                "color": "Orange",
                "usage": "Running & gym",
                "stock": 12,
                "new_arrival": True,
            },
        ],
    },
    {
        "name": "Speakers & More",
        "slug": "speakers-more",
        "description": "Bluetooth speakers, holders, and everyday electronics.",
        "color": (244, 63, 94),
        "products": [
            {
                "name": "Pocket Bluetooth Speaker",
                "price": "1199.00",
                "description": "IPX7 speaker with punchy bass and 12-hour playtime.",
                "color": "Red",
                "size": "12h playtime",
                "stock": 33,
                "bestseller": True,
            },
            {
                "name": "Car Phone Mount",
                "price": "599.00",
                "description": "One-hand magnetic mount for dash or vent.",
                "color": "Black",
                "usage": "Driving",
                "stock": 50,
            },
            {
                "name": "Wireless Mouse",
                "price": "749.00",
                "description": "Silent-click mouse for Windows laptops and desktops.",
                "color": "Grey",
                "suitable_room": "Windows & macOS",
                "stock": 44,
            },
            {
                "name": "USB Hub 4-Port",
                "price": "899.00",
                "description": "USB 3.0 hub for extra ports on a Windows PC or laptop.",
                "color": "Silver",
                "usage": "Office & study",
                "stock": 27,
                "new_arrival": True,
            },
        ],
    },
]


def make_image(title, rgb):
    image = Image.new("RGB", (900, 720), rgb)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((90, 90, 810, 630), radius=48, fill=(15, 23, 42))
    draw.ellipse((330, 210, 570, 450), outline=(255, 255, 255), width=10)
    font = ImageFont.load_default()
    draw.text((120, 540), title[:28], fill=(226, 232, 240), font=font)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    filename = title.lower().replace(" ", "-") + ".png"
    return ContentFile(buffer.getvalue(), name=filename)


class Command(BaseCommand):
    help = "Replace tile catalog with mobile accessories and electronics."

    def handle(self, *args, **options):
        Category.objects.update(is_active=False)
        Product.objects.update(is_active=False)

        for index, category_data in enumerate(CATALOG, start=1):
            category, _ = Category.objects.update_or_create(
                slug=category_data["slug"],
                defaults={
                    "name": category_data["name"],
                    "description": category_data["description"],
                    "is_active": True,
                    "sort_order": index,
                },
            )
            for product_data in category_data["products"]:
                defaults = {
                    "category": category,
                    "name": product_data["name"],
                    "description": product_data["description"],
                    "price": Decimal(product_data["price"]),
                    "old_price": Decimal(product_data["old_price"]) if product_data.get("old_price") else None,
                    "price_unit": "piece",
                    "size": product_data.get("size", ""),
                    "color": product_data.get("color", ""),
                    "material": product_data.get("material", ""),
                    "finish": product_data.get("finish", ""),
                    "suitable_room": product_data.get("suitable_room", ""),
                    "usage": product_data.get("usage", ""),
                    "stock": product_data.get("stock", 10),
                    "is_active": True,
                    "featured": product_data.get("featured", False),
                    "bestseller": product_data.get("bestseller", False),
                    "new_arrival": product_data.get("new_arrival", False),
                }
                product, created = Product.objects.update_or_create(
                    slug=slugify(product_data["name"]),
                    defaults=defaults,
                )
                if created or not product.main_image:
                    product.main_image.save(
                        product.slug + ".png",
                        make_image(product.name, category_data["color"]),
                        save=True,
                    )

        self.stdout.write(self.style.SUCCESS("Seeded Kaif Mobile catalog."))
