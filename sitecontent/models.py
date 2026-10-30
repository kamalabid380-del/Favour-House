from decimal import Decimal

from django.db import models
from django.urls import reverse
from django.utils.text import slugify

DEFAULT_UI = {
    "menu": "Menu",
    "close": "Close",
    "enquire": "Enquire",
    "shop": "Shop",
    "discover": "Discover",
    "view": "View piece",
    "explore": "Explore",
    "all": "All pieces",
    "read": "Read the story",
    "next": "Next",
    "prev": "Previous",
    "scroll": "Scroll",
    "details": "The details",
    "name": "Your name",
    "email": "Email",
    "phone": "Telephone",
    "message": "Your note",
    "send": "Send enquiry",
    "sent": "Thank you. Your note has reached the atelier and we will reply personally.",
    "nothing": "New pieces are being finished at the bench. Please return shortly.",
    "contact": "Contact",
    "follow": "Follow",
    "skip": "Skip to content",
    "hero": "Featured collection",
    "from": "From",
    "pieces": "pieces",
    "back": "Back to collection",
    "journal": "Journal",
    "collections": "Collections",
    "lookbook": "The lookbook",
    "more": "You may also like",
    "error": "Please check the details above and try again.",
    "home": "Return to the house",
}


class SiteSettings(models.Model):
    brand_name = models.CharField(max_length=120, default="Favour House")
    tagline = models.CharField(max_length=200, blank=True)
    announcement = models.CharField(
        max_length=240,
        blank=True,
        help_text="Runs in the moving band beneath the hero.",
    )
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=60, blank=True)
    address = models.CharField(max_length=240, blank=True)
    instagram_url = models.URLField(blank=True)
    pinterest_url = models.URLField(blank=True)
    footer_note = models.CharField(max_length=240, blank=True)
    meta_description = models.TextField(blank=True)
    logo = models.ImageField(upload_to="brand/", blank=True, null=True)
    currency = models.CharField(max_length=8, default="£")

    shop_eyebrow = models.CharField(max_length=120, blank=True)
    shop_heading = models.CharField(max_length=240, blank=True)
    shop_intro = models.TextField(blank=True)
    journal_eyebrow = models.CharField(max_length=120, blank=True)
    journal_heading = models.CharField(max_length=240, blank=True)
    journal_intro = models.TextField(blank=True)

    closing_eyebrow = models.CharField(max_length=120, blank=True)
    closing_heading = models.CharField(max_length=240, blank=True)
    closing_body = models.TextField(blank=True)

    zoom_strength = models.DecimalField(
        "Hero zoom strength",
        max_digits=4,
        decimal_places=2,
        default=Decimal("1.08"),
        help_text="1.00 is still. 1.20 is a strong slow zoom.",
    )
    zoom_seconds = models.PositiveIntegerField(
        "Hero zoom duration (seconds)", default=18
    )

    interface_text = models.JSONField(
        default=dict,
        blank=True,
        help_text="Optional label overrides as JSON, e.g. {\"view\": \"See the piece\"}.",
    )

    class Meta:
        verbose_name = "Site settings"
        verbose_name_plural = "Site settings"

    def __str__(self):
        return self.brand_name or "Site settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        return None

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class NavLink(models.Model):
    label = models.CharField(max_length=80)
    url = models.CharField(max_length=200, default="/")
    order = models.PositiveIntegerField(default=0)
    show_in_header = models.BooleanField(default=True)
    show_in_footer = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.label


class HeroSlide(models.Model):
    eyebrow = models.CharField(max_length=120, blank=True)
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=280, blank=True)
    cta_label = models.CharField(max_length=80, blank=True)
    cta_url = models.CharField(max_length=200, blank=True, default="/shop/")
    image = models.ImageField(upload_to="hero/")
    zoom_strength = models.DecimalField(
        max_digits=4, decimal_places=2, default=Decimal("1.08")
    )
    zoom_seconds = models.PositiveIntegerField(default=18)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Hero slide"
        verbose_name_plural = "Hero slides"

    def __str__(self):
        return self.title


class Section(models.Model):
    LAYOUT_IMAGE_LEFT = "left"
    LAYOUT_IMAGE_RIGHT = "right"
    LAYOUT_CHOICES = [
        (LAYOUT_IMAGE_LEFT, "Image left"),
        (LAYOUT_IMAGE_RIGHT, "Image right"),
    ]

    eyebrow = models.CharField(max_length=120, blank=True)
    heading = models.CharField(max_length=240)
    body = models.TextField(blank=True)
    image = models.ImageField(upload_to="editorial/", blank=True, null=True)
    layout = models.CharField(
        max_length=10, choices=LAYOUT_CHOICES, default=LAYOUT_IMAGE_LEFT
    )
    link_label = models.CharField(max_length=80, blank=True)
    link_url = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.heading


class Category(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    intro = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to="collections/", blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("category", args=[self.slug])


class Product(models.Model):
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="products"
    )
    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    subtitle = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    details = models.TextField(
        blank=True, help_text="One detail per line, e.g. 100% wool barathea."
    )
    price = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    image = models.ImageField(upload_to="pieces/", blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("product", args=[self.slug])

    @property
    def detail_lines(self):
        return [line.strip() for line in self.details.splitlines() if line.strip()]


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="gallery"
    )
    image = models.ImageField(upload_to="pieces/")
    alt = models.CharField(max_length=160, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.alt or f"Image for {self.product}"


class JournalPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    excerpt = models.TextField(blank=True)
    body = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to="journal/", blank=True, null=True)
    published_on = models.DateField(blank=True, null=True)
    is_published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-published_on", "-id"]
        verbose_name = "Journal story"
        verbose_name_plural = "Journal stories"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("journal_post", args=[self.slug])


class Enquiry(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, null=True, blank=True, related_name="enquiries"
    )
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=60, blank=True)
    message = models.TextField(blank=True)
    is_handled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Enquiries"

    def __str__(self):
        return f"{self.name} — {self.product or 'General'}"
