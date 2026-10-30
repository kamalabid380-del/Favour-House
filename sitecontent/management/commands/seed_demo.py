import math
import random
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

from sitecontent.models import (
    Category,
    HeroSlide,
    JournalPost,
    NavLink,
    Product,
    ProductImage,
    Section,
    SiteSettings,
)

ART_DIR = Path(settings.MEDIA_ROOT) / "demo"

PALETTES = {
    "olive": ((38, 41, 30), (129, 124, 92)),
    "charcoal": ((31, 30, 29), (117, 110, 100)),
    "oxblood": ((44, 22, 21), (141, 78, 63)),
    "sand": ((92, 79, 61), (205, 183, 148)),
    "dove": ((60, 60, 58), (166, 163, 154)),
    "midnight": ((20, 26, 40), (83, 96, 122)),
    "cream": ((120, 110, 92), (231, 219, 196)),
    "forest": ((24, 40, 31), (104, 124, 99)),
}


def _poly(draw, points, size, fill=255):
    w, h = size
    draw.polygon([(x * w, y * h) for x, y in points], fill=fill)


def _line(draw, points, size, width, fill=0):
    w, h = size
    draw.line([(x * w, y * h) for x, y in points], fill=fill, width=width)


def _dot(draw, x, y, size, radius, fill=0):
    w, h = size
    r = radius * w
    draw.ellipse((x * w - r, y * h - r, x * w + r, y * h + r), fill=fill)


def draw_garment(draw, kind, size):
    """A ghosted garment drawn in flat shapes; blurred later into the cloth."""
    w, h = size
    seam = max(2, int(w * 0.004))
    button = 0.006

    if kind in ("jacket", "coat"):
        bottom = 0.88 if kind == "jacket" else 0.94
        _poly(draw, [(0.33, 0.19), (0.27, 0.24), (0.21, 0.52), (0.23, 0.74),
                     (0.30, 0.74), (0.31, 0.50), (0.33, 0.31)], size)
        _poly(draw, [(0.67, 0.19), (0.73, 0.24), (0.79, 0.52), (0.77, 0.74),
                     (0.70, 0.74), (0.69, 0.50), (0.67, 0.31)], size)
        _poly(draw, [(0.34, 0.19), (0.42, 0.14), (0.50, 0.22), (0.58, 0.14),
                     (0.66, 0.19), (0.68, 0.44), (0.66, bottom - 0.10),
                     (0.57, bottom - 0.08), (0.55, bottom), (0.45, bottom),
                     (0.43, bottom - 0.08), (0.34, bottom - 0.10), (0.32, 0.44)], size)
        _poly(draw, [(0.415, 0.145), (0.50, 0.225), (0.585, 0.145),
                     (0.56, 0.31), (0.50, 0.39), (0.44, 0.31)], size, 0)
        _line(draw, [(0.415, 0.145), (0.50, 0.39)], size, seam)
        _line(draw, [(0.585, 0.145), (0.50, 0.39)], size, seam)
        _line(draw, [(0.338, 0.30), (0.338, 0.57)], size, seam)
        _line(draw, [(0.662, 0.30), (0.662, 0.57)], size, seam)
        for y in (0.52, 0.63, 0.74):
            _dot(draw, 0.5, y, size, button)
        _line(draw, [(0.38, 0.66), (0.46, 0.66)], size, seam)
        if kind == "coat":
            _line(draw, [(0.36, 0.56), (0.64, 0.56)], size, seam)
            _dot(draw, 0.5, 0.57, size, button)

    elif kind == "waistcoat":
        _poly(draw, [(0.35, 0.20), (0.50, 0.16), (0.65, 0.20), (0.67, 0.50),
                     (0.59, 0.66), (0.50, 0.61), (0.41, 0.66), (0.33, 0.50)], size)
        _poly(draw, [(0.43, 0.17), (0.50, 0.29), (0.57, 0.17),
                     (0.55, 0.35), (0.50, 0.43), (0.45, 0.35)], size, 0)
        _line(draw, [(0.43, 0.17), (0.50, 0.43)], size, seam)
        _line(draw, [(0.57, 0.17), (0.50, 0.43)], size, seam)
        for y in (0.47, 0.53, 0.59):
            _dot(draw, 0.5, y, size, button)

    elif kind == "shirt":
        _poly(draw, [(0.33, 0.20), (0.26, 0.25), (0.21, 0.54), (0.24, 0.76),
                     (0.31, 0.76), (0.32, 0.52), (0.34, 0.30)], size)
        _poly(draw, [(0.67, 0.20), (0.74, 0.25), (0.79, 0.54), (0.76, 0.76),
                     (0.69, 0.76), (0.68, 0.52), (0.66, 0.30)], size)
        _poly(draw, [(0.35, 0.20), (0.50, 0.24), (0.65, 0.20), (0.66, 0.60),
                     (0.63, 0.86), (0.37, 0.86), (0.34, 0.60)], size)
        _poly(draw, [(0.435, 0.175), (0.50, 0.245), (0.565, 0.175),
                     (0.545, 0.29), (0.50, 0.33), (0.455, 0.29)], size, 0)
        _line(draw, [(0.50, 0.33), (0.50, 0.84)], size, seam)
        _line(draw, [(0.348, 0.30), (0.348, 0.57)], size, seam)
        _line(draw, [(0.652, 0.30), (0.652, 0.57)], size, seam)
        for y in (0.44, 0.52, 0.60, 0.68, 0.76):
            _dot(draw, 0.5, y, size, button)

    elif kind == "scarf":
        top, bottom = [], []
        for i in range(25):
            t = i / 24
            x = 0.06 + t * 0.88
            y = 0.50 + 0.11 * math.sin(t * math.pi * 2.1 + 0.4)
            top.append((x, y - 0.06))
            bottom.append((x, y + 0.06))
        _poly(draw, top + bottom[::-1], size)
        for offset in (-0.02, 0.02):
            _line(draw, [(x, y + offset) for x, y in top], size, seam)
            _line(draw, [(x, y + offset) for x, y in bottom], size, seam)

    elif kind == "bowtie":
        _poly(draw, [(0.24, 0.40), (0.47, 0.47), (0.47, 0.55), (0.24, 0.62)], size)
        _poly(draw, [(0.76, 0.40), (0.53, 0.47), (0.53, 0.55), (0.76, 0.62)], size)
        _poly(draw, [(0.465, 0.455), (0.535, 0.455), (0.535, 0.545), (0.465, 0.545)], size)
        _line(draw, [(0.47, 0.47), (0.24, 0.40)], size, seam)
        _line(draw, [(0.53, 0.47), (0.76, 0.40)], size, seam)

    elif kind == "slipper":
        _poly(draw, [(0.20, 0.64), (0.24, 0.55), (0.40, 0.49), (0.60, 0.46),
                     (0.76, 0.50), (0.82, 0.60), (0.79, 0.70), (0.34, 0.72)], size)
        _line(draw, [(0.28, 0.62), (0.48, 0.55), (0.66, 0.56)], size, seam)
        _line(draw, [(0.24, 0.70), (0.78, 0.68)], size, seam)


def make_art(filename, size, palette, seed, shape=None):
    """Paint a cloth backdrop with a ghosted garment so the site feels styled."""
    ART_DIR.mkdir(parents=True, exist_ok=True)
    path = ART_DIR / filename
    if path.exists():
        return path

    rnd = random.Random(seed)
    base, glow = PALETTES[palette]
    w, h = size
    img = Image.new("RGB", size, base)

    # draped cloth: soft vertical folds, rotated and blurred into the base
    small = 640
    band = Image.new("L", (small, small), 110)
    band_draw = ImageDraw.Draw(band)
    x = -small
    while x < small * 2:
        width = rnd.randint(int(small * 0.02), int(small * 0.09))
        band_draw.rectangle(
            (x, -small, x + width, small * 2), fill=rnd.randint(48, 190)
        )
        x += width + rnd.randint(4, 26)
    band = band.filter(ImageFilter.GaussianBlur(small / 28))
    band = band.rotate(rnd.randint(-26, 26), resample=Image.BICUBIC, fillcolor=110)
    band = band.resize(size, Image.BICUBIC)

    dark = tuple(int(c * 0.64) for c in base)
    light = tuple(min(255, int(c * 1.55) + 16) for c in base)
    fabric = Image.composite(
        Image.new("RGB", size, light), Image.new("RGB", size, dark), band
    )
    img = Image.blend(img, fabric, 0.72)

    # ghosted garment
    if shape:
        garment = Image.new("L", size, 0)
        draw_garment(ImageDraw.Draw(garment), shape, size)
        scale = rnd.uniform(0.94, 1.1)
        if abs(scale - 1) > 0.01:
            garment = garment.resize(
                (int(w * scale), int(h * scale)), Image.BICUBIC
            )
        garment = garment.rotate(
            rnd.uniform(-3, 3), resample=Image.BICUBIC, fillcolor=0
        )
        canvas = Image.new("L", size, 0)
        canvas.paste(
            garment,
            (int((w - garment.width) / 2 + rnd.uniform(-0.04, 0.04) * w),
             int((h - garment.height) / 2)),
        )
        canvas = canvas.filter(ImageFilter.GaussianBlur(min(w, h) / 80))
        canvas = canvas.point(lambda v: int(v * 0.72))
        lifted = tuple(min(255, int(c + 26)) for c in base)
        img = Image.composite(Image.new("RGB", size, lifted), img, canvas)

    # pools of light
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    for _ in range(3):
        ew = rnd.randint(int(w * 0.4), int(w * 1.1))
        eh = rnd.randint(int(h * 0.3), int(h * 0.9))
        x0 = rnd.randint(-int(w * 0.45), int(w * 0.8))
        y0 = rnd.randint(-int(h * 0.45), int(h * 0.8))
        draw.ellipse((x0, y0, x0 + ew, y0 + eh), fill=rnd.randint(50, 115))

    mask = mask.filter(ImageFilter.GaussianBlur(radius=min(w, h) / 9))
    img = Image.composite(Image.new("RGB", size, glow), img, mask)

    # a shaft of daylight across the cloth
    shaft = Image.new("L", size, 0)
    shaft_draw = ImageDraw.Draw(shaft)
    sx = rnd.randint(0, w)
    shaft_draw.polygon(
        (
            (sx, -h * 0.1),
            (sx + w * 0.2, -h * 0.1),
            (sx - w * 0.16, h * 1.1),
            (sx - w * 0.36, h * 1.1),
        ),
        fill=62,
    )
    shaft = shaft.filter(ImageFilter.GaussianBlur(min(w, h) / 7))
    img = Image.composite(
        Image.new("RGB", size, tuple(min(255, int(c * 1.1)) for c in glow)), img, shaft
    )

    # vignette
    edge = Image.radial_gradient("L").resize(size).point(lambda v: int(v * 0.72))
    shadow = ImageEnhance.Brightness(img).enhance(0.55)
    img = Image.composite(shadow, img, edge)

    # grain and surface
    noise = Image.effect_noise(size, 30).convert("RGB")
    img = Image.blend(img, noise, 0.05)
    img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=55, threshold=3))

    img.save(path, "JPEG", quality=85, optimize=True)
    return path


def attach(instance, field, filename, size, palette, seed, shape=None):
    path = make_art(filename, size, palette, seed, shape)
    with open(path, "rb") as handle:
        getattr(instance, field).save(filename, File(handle), save=True)


class Command(BaseCommand):
    help = "Create demo content, placeholder imagery and an admin login."

    def handle(self, *args, **options):
        self.site()
        self.nav()
        self.heroes()
        self.sections()
        categories = self.categories()
        self.products(categories)
        self.journal()
        self.admin_user()
        self.stdout.write(self.style.SUCCESS("Demo content is ready."))

    def site(self):
        site = SiteSettings.load()
        site.brand_name = "Favour House"
        site.tagline = "Tailoring & occasionwear, cut in London"
        site.announcement = "Autumn appointments open   ·   Made to measure   ·   Worldwide delivery"
        site.contact_email = "atelier@favourhouse.co.uk"
        site.contact_phone = "+44 20 7946 0871"
        site.address = "14 Savile Row, London W1S"
        site.instagram_url = "https://instagram.com/"
        site.pinterest_url = "https://pinterest.com/"
        site.footer_note = "Hand-finished in London. Cloth from British mills."
        site.meta_description = (
            "Favour House — tailoring, waistcoats and occasionwear, made by hand in London."
        )
        site.shop_eyebrow = "The collection"
        site.shop_heading = "Pieces for the evening and the day"
        site.shop_intro = (
            "Every garment begins on paper, is cut by hand and leaves the atelier only "
            "when it sits exactly as it should."
        )
        site.journal_eyebrow = "The journal"
        site.journal_heading = "Notes from the atelier"
        site.journal_intro = "Cloth, ceremony and the quiet craft of dressing well."
        site.closing_eyebrow = "By appointment"
        site.closing_heading = "A fitting begins with a conversation."
        site.closing_body = (
            "Tell us the occasion, and we will guide you through cloth, cut and "
            "the fittings that follow."
        )
        site.zoom_strength = Decimal("1.09")
        site.zoom_seconds = 18
        site.save()

    def nav(self):
        links = [
            ("Collection", "/shop/", 0, True, True),
            ("Made to measure", "/shop/tailoring/", 1, True, True),
            ("Journal", "/journal/", 2, True, True),
            ("Enquiries", "mailto:atelier@favourhouse.co.uk", 3, False, True),
        ]
        for label, url, order, in_header, in_footer in links:
            NavLink.objects.get_or_create(
                label=label,
                defaults={
                    "url": url,
                    "order": order,
                    "show_in_header": in_header,
                    "show_in_footer": in_footer,
                },
            )

    def heroes(self):
        slides = [
            {
                "eyebrow": "Autumn / Winter",
                "title": "Cut for the long evening",
                "subtitle": "Dinner suits, silk waistcoats and the quiet ceremony of dressing well.",
                "cta_label": "Explore the collection",
                "cta_url": "/shop/",
                "palette": "olive",
                "shape": "coat",
                "zoom": Decimal("1.10"),
                "seconds": 20,
            },
            {
                "eyebrow": "Made to measure",
                "title": "The cloth remembers every hand",
                "subtitle": "British mills, hand-padded canvases, four fittings before anything leaves the bench.",
                "cta_label": "Book a fitting",
                "cta_url": "/shop/tailoring/",
                "palette": "sand",
                "shape": "jacket",
                "zoom": Decimal("1.14"),
                "seconds": 24,
            },
            {
                "eyebrow": "Occasionwear",
                "title": "A wardrobe for the marquee",
                "subtitle": "Morning coats, ivory dinners and the pieces that wait in tissue for the right night.",
                "cta_label": "View occasionwear",
                "cta_url": "/shop/occasionwear/",
                "palette": "midnight",
                "shape": "coat",
                "zoom": Decimal("1.08"),
                "seconds": 18,
            },
        ]
        for index, data in enumerate(slides):
            title = data["title"]
            if HeroSlide.objects.filter(title=title).exists():
                continue
            slide = HeroSlide.objects.create(
                eyebrow=data["eyebrow"],
                title=title,
                subtitle=data["subtitle"],
                cta_label=data["cta_label"],
                cta_url=data["cta_url"],
                zoom_strength=data["zoom"],
                zoom_seconds=data["seconds"],
                order=index,
            )
            attach(
                slide,
                "image",
                f"hero-{index + 1}.jpg",
                (1600, 1000),
                data["palette"],
                100 + index,
                data["shape"],
            )

    def sections(self):
        data = [
            {
                "eyebrow": "The house",
                "heading": "Quiet tailoring, made by hand",
                "body": (
                    "We work in small numbers, in a room above the shop. A jacket passes "
                    "through eleven pairs of hands before it is pressed, wrapped and sent "
                    "to its first fitting. Nothing is rushed, and very little is written down."
                ),
                "link_label": "Read our journal",
                "link_url": "/journal/",
                "layout": "left",
                "palette": "charcoal",
                "shape": "jacket",
            },
            {
                "eyebrow": "The cloth",
                "heading": "Bolts chosen in Huddersfield, cut in London",
                "body": (
                    "Barathea, barleycorn, silk dupion — the cloth is chosen first and the "
                    "garment follows. We keep a small library of bolts so a client can feel "
                    "the weight of a decision before a single cut is made."
                ),
                "link_label": "See the collection",
                "link_url": "/shop/",
                "layout": "right",
                "palette": "oxblood",
                "shape": "scarf",
            },
        ]
        for index, item in enumerate(data):
            if Section.objects.filter(heading=item["heading"]).exists():
                continue
            section = Section.objects.create(
                eyebrow=item["eyebrow"],
                heading=item["heading"],
                body=item["body"],
                link_label=item["link_label"],
                link_url=item["link_url"],
                layout=item["layout"],
                order=index,
            )
            attach(
                section,
                "image",
                f"editorial-{index + 1}.jpg",
                (900, 1200),
                item["palette"],
                200 + index,
                item["shape"],
            )

    def categories(self):
        data = [
            ("Tailoring", "dove", "Jackets, suits and the architecture of a shoulder.", "jacket"),
            ("Waistcoats", "oxblood", "Silk, linen and the small ceremony of a button.", "waistcoat"),
            ("Shirts", "cream", "Marcella, pleats and collars with somewhere to go.", "shirt"),
            ("Occasionwear", "midnight", "For weddings, gardens and long marquees.", "coat"),
        ]
        categories = {}
        for index, (name, palette, intro, shape) in enumerate(data):
            category, created = Category.objects.get_or_create(
                slug=slugify(name),
                defaults={"name": name, "intro": intro, "order": index},
            )
            categories[slugify(name)] = category
            if created:
                attach(
                    category,
                    "cover_image",
                    f"collection-{slugify(name)}.jpg",
                    (1000, 1250),
                    palette,
                    300 + index,
                    shape,
                )
        return categories

    def products(self, categories):
        data = [
            ("The Grosvenor Dinner Jacket", "tailoring", "olive", "1295.00", True,
             "A single-breasted dinner jacket in midnight barathea, with a shawl collar faced in silk.",
             "100% wool barathea\nHand-padded canvas\nSilk-faced shawl collar\nCut and finished in London", "jacket"),
            ("Barleycorn Two-Piece", "tailoring", "charcoal", "1150.00", False,
             "A soft-shouldered suit in barleycorn tweed, cut a little shorter and worn with ease.",
             "Woven in Huddersfield\nHalf-lined body\nTwo-button front\nWorking cuffs", "jacket"),
            ("Midnight Velvet Smoking Jacket", "tailoring", "midnight", "985.00", True,
             "Deep blue velvet, grosgrain lapels and the particular warmth of a room after midnight.",
             "Cotton-silk velvet\nGrosgrain shawl collar\nTurned-back cuffs\nMade to order", "jacket"),
            ("Highgrove Charcoal Suit", "tailoring", "charcoal", "1240.00", False,
             "Charcoal flannel with a clean shoulder — the suit that answers most invitations.",
             "Wool flannel\nSoft Neapolitan shoulder\nSide adjusters\nFour fittings inclusive", "jacket"),
            ("Silk Dupion Waistcoat", "waistcoats", "oxblood", "325.00", True,
             "A deep oxblood waistcoat in slubbed silk dupion, cut low and worn with a white tie.",
             "Silk dupion\nSix-button front\nAdjustable back\nHand-finished buttonholes", "waistcoat"),
            ("Dove Grey Morning Waistcoat", "waistcoats", "dove", "295.00", False,
             "For weddings before noon: dove grey wool, mother-of-pearl and a quiet line.",
             "Wool hopsack\nMother-of-pearl buttons\nCotton back\nMade in London", "waistcoat"),
            ("Olive Linen Waistcoat", "waistcoats", "olive", "260.00", False,
             "Unstructured linen for gardens, with a back that breathes when the day runs long.",
             "100% Irish linen\nUnlined front\nNatural horn buttons\nMachine washable", "waistcoat"),
            ("Ivory Marcella Dress Shirt", "shirts", "cream", "185.00", True,
             "The white-tie shirt: marcella front, wing collar, double cuffs.",
             "Cotton marcella\nWing collar\nDouble cuff\nCut for a bow tie", "shirt"),
            ("Pleated Evening Shirt", "shirts", "dove", "165.00", False,
             "Fine pleats and a softer collar for dinners that do not insist on white tie.",
             "Cotton poplin\nHand-set pleats\nMother-of-pearl studs\nSlim body", "shirt"),
            ("The Marquee Morning Coat", "occasionwear", "sand", "1450.00", True,
             "A morning coat in black herringbone, cut for standing about in a field beautifully.",
             "Herringbone worsted\nPeak lapel\nCutaway front\nHire available", "coat"),
            ("Pearl Grey Stroller", "occasionwear", "dove", "890.00", False,
             "The stroller: morning dress for a modern wedding, with a pearl grey waistcoat.",
             "Worsted wool\nPeak lapel\nMatching waistcoat\nMade to measure", "coat"),
            ("Opera Silk Scarf", "accessories", "forest", "145.00", True,
             "A long silk scarf, printed with an archive drawing of the shop front.",
             "100% silk twill\nHand-rolled edges\n180 × 32 cm\nMade in England", "scarf"),
            ("Black Silk Bow Tie", "accessories", "midnight", "75.00", False,
             "Self-tied, in black silk, with the small imperfection that proves it.",
             "Silk grosgrain\nSelf-tie\nAdjustable band\nMade in England", "bowtie"),
            ("Velvet Smoking Slipper", "accessories", "oxblood", "240.00", False,
             "Quilted velvet, leather sole, made for the walk from dinner to the terrace.",
             "Cotton velvet\nLeather sole\nQuilted lining\nMade in England", "slipper"),
        ]
        for index, (name, cat_slug, palette, price, featured, blurb, details, shape) in enumerate(data):
            product, created = Product.objects.get_or_create(
                slug=slugify(name),
                defaults={
                    "name": name,
                    "category": categories.get(cat_slug),
                    "subtitle": "",
                    "description": blurb,
                    "details": details,
                    "price": Decimal(price),
                    "is_featured": featured,
                    "order": index,
                },
            )
            if not created:
                continue
            attach(
                product,
                "image",
                f"piece-{slugify(name)}.jpg",
                (900, 1125),
                palette,
                400 + index,
                shape,
            )
            alt = ProductImage(product=product, alt=f"{name}, detail", order=1)
            attach(
                alt,
                "image",
                f"piece-{slugify(name)}-detail.jpg",
                (900, 1125),
                palette,
                500 + index,
                shape,
            )

    def journal(self):
        from datetime import date

        posts = [
            {
                "title": "The anatomy of a dinner jacket",
                "published_on": date(2026, 9, 18),
                "excerpt": "Shawl or peak, silk or grosgrain — a short guide to the decisions that make an evening.",
                "palette": "olive",
                "shape": "jacket",
                "body": (
                    "A dinner jacket is a set of small decisions. The first is the collar: shawl "
                    "for ease, peak for ceremony. The second is the facing — silk satin catches "
                    "the light, grosgrain absorbs it.\n\n"
                    "Then the shoulder. We keep ours soft, with just enough structure to hold "
                    "the line when you stand. A hard shoulder photographs well and moves badly.\n\n"
                    "The last decision is the trouser, and it is the one most often got wrong. "
                    "A dinner trouser should break once, gently, and no more."
                ),
            },
            {
                "title": "Notes on cloth: why barathea",
                "published_on": date(2026, 8, 30),
                "excerpt": "The weave behind the black tie, and why it has survived a hundred years of fashion.",
                "palette": "charcoal",
                "shape": "waistcoat",
                "body": (
                    "Barathea is a pebbled weave, part twill and part hopsack. It is matte, "
                    "which is the point: under electric light a satin jacket shines, while "
                    "barathea holds its colour and lets the silk facings do the talking.\n\n"
                    "We buy ours from a mill in Huddersfield that has been weaving it since "
                    "the 1890s. The bolt is heavy in the hand and smells faintly of oil — the "
                    "scent of a loom that has not stopped."
                ),
            },
            {
                "title": "A fitting, step by step",
                "published_on": date(2026, 8, 2),
                "excerpt": "Four appointments, one garment, and what actually happens in the room.",
                "palette": "sand",
                "shape": "coat",
                "body": (
                    "The first fitting is a conversation with a tape measure. We take thirty-two "
                    "measurements and write down which shoulder drops.\n\n"
                    "The second is the basted fitting, when the jacket is held together with "
                    "white thread. It looks unfinished because it is — this is where the shape "
                    "is agreed.\n\n"
                    "The third is the forward fitting, and the fourth is the one where you put "
                    "it on, turn once in front of the mirror, and say nothing at all."
                ),
            },
        ]
        for index, item in enumerate(posts):
            post, created = JournalPost.objects.get_or_create(
                slug=slugify(item["title"]),
                defaults={
                    "title": item["title"],
                    "excerpt": item["excerpt"],
                    "body": item["body"],
                    "published_on": item["published_on"],
                    "is_published": True,
                    "order": index,
                },
            )
            if created:
                attach(
                    post,
                    "cover_image",
                    f"journal-{index + 1}.jpg",
                    (1200, 900),
                    item["palette"],
                    600 + index,
                    item["shape"],
                )

    def admin_user(self):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser("studio", "studio@favourhouse.co.uk", "atelier2026")
            self.stdout.write(
                self.style.WARNING("Admin login created — user: studio / password: atelier2026")
            )
