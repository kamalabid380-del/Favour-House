from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html

from .models import (
    Category,
    Enquiry,
    HeroSlide,
    JournalPost,
    NavLink,
    Product,
    ProductImage,
    Section,
    SiteSettings,
)


def thumb(obj_image, size=54):
    if not obj_image:
        return "—"
    return format_html(
        '<img src="{}" style="width:{}px;height:{}px;object-fit:cover;border-radius:3px" />',
        obj_image.url,
        size,
        size,
    )


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Identity", {"fields": ("brand_name", "tagline", "logo", "meta_description")}),
        ("Contact", {"fields": ("contact_email", "contact_phone", "address", "instagram_url", "pinterest_url")}),
        ("Home page", {"fields": ("announcement", "closing_eyebrow", "closing_heading", "closing_body")}),
        ("Collection page", {"fields": ("shop_eyebrow", "shop_heading", "shop_intro")}),
        ("Journal page", {"fields": ("journal_eyebrow", "journal_heading", "journal_intro")}),
        ("Motion", {"fields": ("zoom_strength", "zoom_seconds")}),
        ("Shop", {"fields": ("currency", "footer_note")}),
        ("Interface labels", {
            "classes": ("collapse",),
            "fields": ("interface_text",),
            "description": "Leave empty to use the standard English labels.",
        }),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = SiteSettings.load()
        return HttpResponseRedirect(
            reverse("admin:sitecontent_sitesettings_change", args=[obj.pk])
        )


@admin.register(NavLink)
class NavLinkAdmin(admin.ModelAdmin):
    list_display = ("label", "url", "order", "show_in_header", "show_in_footer", "is_active")
    list_editable = ("order", "show_in_header", "show_in_footer", "is_active")
    list_display_links = ("label",)


@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ("preview", "title", "eyebrow", "order", "is_active")
    list_editable = ("order", "is_active")
    list_display_links = ("preview", "title")

    @admin.display(description="Image")
    def preview(self, obj):
        return thumb(obj.image)


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("preview", "heading", "layout", "order", "is_active")
    list_editable = ("order", "is_active")
    list_display_links = ("preview", "heading")

    @admin.display(description="Image")
    def preview(self, obj):
        return thumb(obj.image)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "alt", "order")
    ordering = ("order",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("preview", "name", "category", "price", "is_featured", "order", "is_active")
    list_editable = ("price", "is_featured", "order", "is_active")
    list_display_links = ("preview", "name")
    list_filter = ("category", "is_featured", "is_active")
    search_fields = ("name", "subtitle", "description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline]

    @admin.display(description="Image")
    def preview(self, obj):
        return thumb(obj.image)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("preview", "name", "order", "is_active")
    list_editable = ("order", "is_active")
    list_display_links = ("preview", "name")
    prepopulated_fields = {"slug": ("name",)}

    @admin.display(description="Cover")
    def preview(self, obj):
        return thumb(obj.cover_image)


@admin.register(JournalPost)
class JournalPostAdmin(admin.ModelAdmin):
    list_display = ("preview", "title", "published_on", "is_published")
    list_display_links = ("preview", "title")
    list_editable = ("is_published",)
    prepopulated_fields = {"slug": ("title",)}

    @admin.display(description="Cover")
    def preview(self, obj):
        return thumb(obj.cover_image)


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "product", "created_at", "is_handled")
    list_filter = ("is_handled", "created_at")
    search_fields = ("name", "email", "message")
    readonly_fields = ("name", "email", "phone", "message", "product", "created_at")
    actions = ("mark_handled",)

    def has_add_permission(self, request):
        return False

    @admin.action(description="Mark selected enquiries as handled")
    def mark_handled(self, request, queryset):
        queryset.update(is_handled=True)
