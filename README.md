# Favour House — editorial tailoring site

A complete Django storefront in the spirit of favourbrook.com: full-bleed
editorial imagery, slow Ken Burns zoom, scroll reveals, parallax and a
click-to-filter collection — with **every word, image, price and label
editable in the admin**. Nothing is hard-coded in the templates.

## 1. Start it

**Desktop shortcut (easiest).** Double-click **Favour House** on the Desktop. It
starts the server invisibly (setting up the database on first run) and opens the
site in a plain app window — no terminal, no tabs, no address bar. Run
`launch.vbs` yourself if you ever lose the shortcut.

**Restart.** Double-click **Restart Favour House** on the Desktop (or run
`restart.vbs`): it stops the server, starts it again, and reloads the open app
window — about two seconds. You only need this after changing code; anything
edited in the admin shows up immediately.

Both icons use the Python install directly and write their start-up notes to
`%TEMP%\favour-house.log`. If a launch ever fails, a small dialog says so
instead of opening an empty window.

Or double-click `start.bat`, or from a terminal:

```
py manage.py migrate
py manage.py seed_demo
py manage.py runserver 8017
```

Then open http://127.0.0.1:8017/

## 2. Edit everything

Admin: http://127.0.0.1:8017/admin/

Demo login (change it immediately):

- user: `studio`
- password: `atelier2026`

Inside the admin:

| Section | What it controls |
| --- | --- |
| **Site settings** | Brand name, tagline, announcement band, contact details, socials, closing section, page intros, currency, footer note |
| **Motion** (inside Site settings) | Default hero zoom strength and duration |
| **Hero slides** | Each slide's image, eyebrow, title, subtitle, button, order, zoom strength and zoom seconds |
| **Sections** | The two split editorial blocks on the home page (image left/right) |
| **Categories** | Collection names, intros, cover images used in the lookbook |
| **Products** | Name, price, description, detail lines, main image, gallery images (inline), featured flag |
| **Journal stories** | Cover image, excerpt, body, publish date |
| **Enquiries** | Every message sent from a product page; mark as handled |
| **Navigation links** | Header and footer links, order, on/off |

All images upload straight into `media/` — replace any placeholder and the
site updates instantly.

Interface labels (View piece, Enquire, Read the story …) come from
*Site settings → Interface labels*. Add JSON such as
`{"view": "See the piece", "enquire": "Arrange a fitting"}` to override them.

## 3. The motion system

- **Hero** — crossfading slides, per-slide Ken Burns zoom (`zoom_strength`,
  `zoom_seconds`), word-by-word title rise, progress line, arrows, keyboard
  and swipe. Scrolling zooms the hero and fades the copy.
- **Reveal** — sections rise and fade as they enter the viewport.
- **Parallax** — editorial images drift inside their frames.
- **Hover zoom** — product and lookbook images scale slowly.
- **Product viewer** — thumbnails swap the main image; on desktop the image
  zooms toward the cursor.
- **Collection filter** — pills filter cards in place, no reload.
- Everything respects `prefers-reduced-motion`.

## 4. Responsive behaviour

- **Phones (up to 720px)** — products sit two-up with the price under the
  name, the filter row scrolls sideways, the footer stacks, and the closing
  watermark shrinks to fit.
- **Large phones and tablets (721–900px)** — editorial images switch to a
  landscape crop so they no longer run a full screen tall.
- **Tablets (up to 1100px)** — header collapses to the menu, product grids
  go two-up, related sections stack.
- **Short landscape phones** — the hero subtitle hides and the copy lifts so
  the button and slide controls never overlap.
- Touch devices get 44px+ tap targets, visible lookbook captions, and no
  hover-only content; form fields are 16px so iOS does not zoom on focus.

## 5. Project map

```
manage.py
start.bat              double-click to run
launch.vbs             what the Desktop shortcut calls: hidden server + app window
restart.vbs            stops the server, starts it again, reloads the window
atelier/               settings and urls
sitecontent/           models, views, admin, seed command
  management/commands/seed_demo.py   demo content + painted placeholder art
templates/             base, home, shop, product, journal, 404, partials
static/css/site.css    all styling and animation
static/js/site.js      hero, reveals, parallax, filter, viewer, cursor
media/demo/            generated placeholders (replace via admin)
```

## 6. Before going live

- Change the admin password.
- In `atelier/settings.py` set `DEBUG = False` and a secret `SECRET_KEY`,
  and set `ALLOWED_HOSTS` to your domain.
- Run `py manage.py collectstatic` if you serve static files from a web
  server, and point your media folder at persistent storage.
