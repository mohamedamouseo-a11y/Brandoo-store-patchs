#!/usr/bin/env python3
from pathlib import Path
import re
import sys

VERSION = "0.5.6"
START = "/* BRANDO LUXURY PRESENCE v0.5.6 START */"
END = "/* BRANDO LUXURY PRESENCE v0.5.6 END */"

if len(sys.argv) != 2:
    raise SystemExit("Usage: apply-direct.py /absolute/path/to/brando")

theme = Path(sys.argv[1]).resolve()
if not theme.is_dir():
    raise SystemExit(f"Theme directory not found: {theme}")

required = [
    "style.css",
    "functions.php",
    "header.php",
    "front-page.php",
    "footer.php",
    "assets/css/luxury-v3.css",
    "assets/js/luxury-motion.js",
]
missing = [rel for rel in required if not (theme / rel).is_file()]
if missing:
    raise SystemExit("Missing theme files: " + ", ".join(missing))


def read(rel):
    return (theme / rel).read_text(encoding="utf-8")


def write_atomic(rel, text):
    path = theme / rel
    tmp = path.with_suffix(path.suffix + ".tmp-brando-056")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


style = read("style.css")
functions = read("functions.php")
header = read("header.php")
front = read("front-page.php")
footer = read("footer.php")
css = read("assets/css/luxury-v3.css")
js = read("assets/js/luxury-motion.js")

# Require the approved 0.5.5 baseline and preserve its demo art-direction lock.
if "BRANDO ART DIRECTION LOCK v0.5.5" not in css:
    raise SystemExit("Expected v0.5.5 CSS baseline marker not found")
if "BRANDO DEMO ART DIRECTION v0.5.5" not in js:
    raise SystemExit("Expected v0.5.5 demo art-direction marker not found")

# Preserve section composition/order and locale protections.
front_markers = [
    'class="brando-hero"',
    'id="categories"',
    'id="best-sellers"',
    'class="brando-promo"',
    'class="brando-new-arrivals"',
]
positions = [front.find(marker) for marker in front_markers]
if any(pos < 0 for pos in positions) or positions != sorted(positions):
    raise SystemExit("Homepage section structure/order check failed")
if any(marker not in footer for marker in ["brando-trust", "brando-newsletter", "brando-footer"]):
    raise SystemExit("Footer structure check failed")
for forbidden in ["999 ر.س", "WELCOME10", "+966", "brando.sa"]:
    if forbidden in header + "\n" + front + "\n" + footer:
        raise SystemExit(f"Forbidden locale token returned: {forbidden}")
if "IntersectionObserver" not in js or "scrollIntoView" not in js:
    raise SystemExit("Luxury motion system is incomplete")

style_new, n = re.subn(r"(?m)^Version:\s*[^\r\n]+$", f"Version: {VERSION}", style, count=1)
if n != 1:
    raise SystemExit("Could not update style.css Version")

functions_new, n = re.subn(
    r"define\('BRANDO_THEME_VERSION',\s*'[^']+'\);",
    f"define('BRANDO_THEME_VERSION', '{VERSION}');",
    functions,
    count=1,
)
if n != 1:
    raise SystemExit("Could not update BRANDO_THEME_VERSION")

# Idempotent presence layer. Templates, WooCommerce data, JS, and imagery remain untouched.
pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
css = pattern.sub("", css).rstrip() + "\n\n"

presence = r'''/* BRANDO LUXURY PRESENCE v0.5.6 START */
:root{
  --br-presence-ink:#090908;
  --br-presence-copper:#934a22;
  --br-presence-copper-soft:#b66d3d;
  --br-presence-paper:#f8f3eb;
  --br-presence-beige:#e8ded1;
}

/* GLOBAL RHYTHM — same sections, stronger proportions and less dead space. */
.brando-categories__inner,
.brando-best-sellers__inner,
.brando-promo__inner,
.brando-new-arrivals__inner,
.brando-trust__inner,
.brando-newsletter__inner,
.brando-footer__inner{max-width:1460px!important}
.brando-categories__title,
.brando-best-sellers__title{font-size:clamp(44px,3.65vw,58px)!important;line-height:1.08!important;letter-spacing:-.04em!important}
.brando-new-arrivals__title{font-size:clamp(36px,3.15vw,46px)!important;line-height:1.1!important}
.brando-categories__subtitle,
.brando-best-sellers__subtitle,
.brando-new-arrivals__subtitle{font-size:14.5px!important;line-height:1.9!important;max-width:760px}

/* HEADER — slightly stronger brand presence, no composition change. */
.brando-header__inner{min-height:96px!important}
.brando-brand__mark{width:60px!important;height:60px!important}
.brando-brand__text strong{font-size:31px!important}
.site-nav__menu>li>a{min-height:96px!important;font-size:13.5px!important}

/* CATEGORIES — keep same six-card row, reduce empty vertical gap and add editorial presence. */
.brando-categories{padding:78px 0 84px!important}
.brando-categories__head{margin-bottom:34px!important}
.brando-categories__grid{gap:22px!important}
.brando-category-card{box-shadow:0 18px 44px rgba(16,13,10,.09)!important}
.brando-category-card__name{font-size:17.5px!important;line-height:1.35!important}

/* BEST SELLERS — the primary commercial showcase. */
.brando-best-sellers{padding:82px 0 90px!important;background:linear-gradient(180deg,#eee5d8 0%,#e7dccf 100%)!important}
.brando-best-sellers__head{margin-bottom:34px!important}
.brando-best-sellers__grid{gap:30px!important}
.brando-product-card{box-shadow:0 20px 52px rgba(18,14,10,.08)!important}
.brando-product-card__media{aspect-ratio:4/5.28!important}
.brando-product-card__content{padding:21px 21px 20px!important;min-height:174px!important}
.brando-product-card__name{font-size:16.75px!important;line-height:1.45!important}
.brando-product-card__price{font-size:20.5px!important}

/* PROMO — same split composition, more confident scale with less surrounding whitespace. */
.brando-promo{padding:68px 0 76px!important}
.brando-promo__card{min-height:500px!important;box-shadow:0 36px 94px rgba(19,14,10,.14)!important}
.brando-promo__content{padding:70px 74px!important}
.brando-promo__visual{min-height:500px!important}
.brando-promo__title{font-size:clamp(46px,4.1vw,64px)!important}
.brando-promo__text{font-size:14.5px!important;line-height:1.95!important}

/* NEW ARRIVALS — same four cards, quieter and more editorial. */
.brando-new-arrivals{padding:72px 0 78px!important}
.brando-new-arrivals__head{margin-bottom:30px!important}
.brando-new-arrivals .woocommerce ul.products{gap:26px!important}
.brando-new-arrivals .woocommerce ul.products li.product{box-shadow:0 12px 30px rgba(18,14,10,.05)!important}
.brando-new-arrivals .woocommerce ul.products li.product .woocommerce-loop-product__title{font-size:15.4px!important;line-height:1.48!important}
.brando-new-arrivals .woocommerce ul.products li.product .price{font-size:18px!important}

/* TRUST — increase legibility and presence without cards/boxes. */
.brando-trust__inner{min-height:116px!important}
.brando-trust__item{padding:32px 30px!important;gap:16px!important}
.brando-trust__item h3{font-size:14.5px!important}
.brando-trust__item p{font-size:11.8px!important;line-height:1.75!important}

/* NEWSLETTER + FOOTER — stronger ending and less empty black space. */
.brando-newsletter{padding:72px 0 0!important}
.brando-newsletter__inner{padding:58px 64px!important;gap:58px!important;transform:translateY(36px)!important}
.brando-newsletter h2{font-size:clamp(38px,3.9vw,54px)!important;line-height:1.05!important;max-width:760px!important}
.brando-newsletter p{font-size:14px!important;max-width:680px!important}
.brando-newsletter__form{max-width:580px!important}
.brando-footer__inner{padding:106px 0 30px!important}
.brando-footer__grid{gap:62px!important;padding-bottom:38px!important}
.brando-footer__brand-name{font-size:44px!important;line-height:1!important}
.brando-footer__brand p{font-size:13.3px!important;line-height:1.95!important}
.brando-footer__column h3{font-size:12.75px!important}
.brando-footer__column a{font-size:12.7px!important}
.brando-footer__payments{padding:19px 0!important}

@media(max-width:1200px){
  .brando-categories__grid{gap:18px!important}
  .brando-best-sellers__grid{gap:22px!important}
}
@media(max-width:980px){
  .brando-header__inner{min-height:76px!important}
  .brando-brand__mark{width:52px!important;height:52px!important}
  .site-nav__menu>li>a{min-height:48px!important}
  .brando-newsletter__inner{padding:46px 38px!important;gap:34px!important}
}
@media(max-width:720px){
  .brando-categories{padding-block:58px!important}
  .brando-best-sellers{padding-block:62px!important}
  .brando-promo{padding-block:56px!important}
  .brando-new-arrivals{padding-block:58px!important}
  .brando-newsletter{padding-top:56px!important}
  .brando-newsletter__inner{padding:34px 24px!important;transform:translateY(24px)!important}
  .brando-footer__inner{padding-top:82px!important}
}
/* BRANDO LUXURY PRESENCE v0.5.6 END */'''

css_new = css + presence + "\n"

write_atomic("style.css", style_new)
write_atomic("functions.php", functions_new)
write_atomic("assets/css/luxury-v3.css", css_new)

print("PATCH_VERSION=0.5.6")
print("LAYOUT_STRUCTURE_CHANGED=NO")
print("SECTION_ORDER_CHANGED=NO")
print("TEMPLATES_CHANGED=NO")
print("WOOCOMMERCE_DATA_CHANGED=NO")
print("IMAGERY_CHANGED=NO")
print("DEMO_ART_DIRECTION_PRESERVED=YES")
print("HERO_COMPOSITION_CHANGED=NO")
print("CATEGORIES_COMPOSITION_CHANGED=NO")
print("LUXURY_PRESENCE_PASS=YES")
print("MOTION_SYSTEM_PRESERVED=YES")
