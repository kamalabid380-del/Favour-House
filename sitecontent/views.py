from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .forms import EnquiryForm
from .models import Category, HeroSlide, JournalPost, Product, Section


def home(request):
    slides = list(HeroSlide.objects.filter(is_active=True))
    featured = list(Product.objects.filter(is_active=True, is_featured=True)[:6])
    if not featured:
        featured = list(Product.objects.filter(is_active=True)[:6])

    hero_payload = [
        {
            "eyebrow": slide.eyebrow,
            "title": slide.title,
            "subtitle": slide.subtitle,
            "cta_label": slide.cta_label,
            "cta_url": slide.cta_url or reverse("shop"),
        }
        for slide in slides
    ]

    context = {
        "hero": True,
        "slides": slides,
        "hero_payload": hero_payload,
        "featured": featured,
        "sections": Section.objects.filter(is_active=True),
        "looks": list(Category.objects.filter(is_active=True)[:4]),
        "stories": list(JournalPost.objects.filter(is_published=True)[:3]),
    }
    return render(request, "home.html", context)


def shop(request, slug=None):
    categories = list(Category.objects.filter(is_active=True))
    products = Product.objects.filter(is_active=True).select_related("category")
    active_category = None
    if slug:
        active_category = get_object_or_404(Category, slug=slug, is_active=True)
        products = products.filter(category=active_category)

    context = {
        "products": list(products),
        "categories": categories,
        "active_filter": active_category.slug if active_category else "all",
        "active_category": active_category,
    }
    return render(request, "shop.html", context)


@require_http_methods(["GET", "POST"])
def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.prefetch_related("gallery"), slug=slug, is_active=True
    )
    form = EnquiryForm(request.POST or None)
    sent = request.GET.get("sent") == "1"

    if request.method == "POST":
        if form.is_valid():
            enquiry = form.save(commit=False)
            enquiry.product = product
            enquiry.save()
            url = reverse("product", args=[product.slug]) + "?sent=1#enquire"
            return redirect(url)

    images = []
    if product.image:
        images.append({"url": product.image.url, "alt": product.name})
    for extra in product.gallery.all():
        if extra.image:
            images.append({"url": extra.image.url, "alt": extra.alt or product.name})

    related = list(
        Product.objects.filter(is_active=True, category=product.category)
        .exclude(pk=product.pk)[:3]
    )

    context = {
        "product": product,
        "images": images,
        "form": form,
        "sent": sent,
        "related": related,
    }
    return render(request, "product.html", context)


def journal_list(request):
    posts = list(JournalPost.objects.filter(is_published=True))
    return render(request, "journal_list.html", {"posts": posts})


def journal_detail(request, slug):
    post = get_object_or_404(JournalPost, slug=slug, is_published=True)
    more = list(JournalPost.objects.filter(is_published=True).exclude(pk=post.pk)[:3])
    return render(request, "journal_detail.html", {"post": post, "more": more})


def custom_404(request, exception):
    return render(request, "404.html", status=404)
