#!/usr/bin/env python3
from pathlib import Path
import re
import sys

VERSION = "0.5.3"
START = "/* BRANDO LUXURY FINISH v0.5.3 START */"
END = "/* BRANDO LUXURY FINISH v0.5.3 END */"

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
    tmp = path.with_suffix(path.suffix + ".tmp-brando-053")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


style = read("style.css")
style_new, n = re.subn(r"(?m)^Version:\s*[^\r\n]+$", f"Version: {VERSION}", style, count=1)
if n != 1:
    raise SystemExit("Could not update style.css Version")

functions = read("functions.php")
functions_new, n = re.subn(
    r"define\('BRANDO_THEME_VERSION',\s*'[^']+'\);",
    f"define('BRANDO_THEME_VERSION', '{VERSION}');",
    functions,
    count=1,
)
if n != 1:
    raise SystemExit("Could not update BRANDO_THEME_VERSION")

front = read("front-page.php")
header = read("header.php")
footer = read("footer.php")
motion = read("assets/js/luxury-motion.js")
css = read("assets/css/luxury-v3.css")

# Safety: this finishing pass must preserve the current template composition.
front_markers = [
    'class="brando-hero"',
    'id="categories"',
    'id="best-sellers"',
    'class="brando-promo"',
    'class="brando-new-arrivals"',
]
front_positions = [front.find(marker) for marker in front_markers]
if any(pos < 0 for pos in front_positions) or front_positions != sorted(front_positions):
    raise SystemExit("Homepage section structure/order check failed")

footer_markers = ["brando-trust", "brando-newsletter", "brando-footer"]
if any(marker not in footer for marker in footer_markers):
    raise SystemExit("Trust/newsletter/footer structure check failed")

for forbidden in ["999 ر.س", "WELCOME10", "+966", "brando.sa"]:
    if forbidden in header + "\n" + front + "\n" + footer:
        raise SystemExit(f"Locale regression detected: {forbidden}")

if "IntersectionObserver" not in motion or "scrollIntoView" not in motion:
    raise SystemExit("Existing luxury motion runtime is incomplete")

# Make re-apply idempotent.
css = re.sub(re.escape(START) + r".*?" + re.escape(END), "", css, flags=re.S).rstrip() + "\n\n"

finish_css = r'''/* BRANDO LUXURY FINISH v0.5.3 START */
/* Same page composition. No section reorder. No asymmetric grids. */
:root{
  --br-copper:#8e4824;
  --br-copper-light:#b66d42;
  --br-ivory:#f8f5ef;
  --br-beige:#eee7dc;
  --br-beige-deep:#e7ded1;
  --br-line:#d8cec0;
  --br-shadow:0 20px 52px rgba(18,14,10,.065);
  --br-shadow-strong:0 34px 88px rgba(10,8,6,.13);
}

/* HEADER — stronger presence, less retail noise */
.brando-topbar{font-size:10.5px!important;letter-spacing:.01em!important;background:#0d0e0e!important}
.brando-topbar__inner{min-height:28px!important}
.brando-header{background:rgba(6,7,7,.985)!important;box-shadow:0 16px 46px rgba(0,0,0,.20)!important}
.brando-header__inner{min-height:82px!important;gap:36px!important}
.brando-branding{min-width:196px!important}
.brando-brand__mark{width:56px!important;height:56px!important}
.brando-brand__text strong{font-size:29px!important;letter-spacing:-.045em!important}
.brando-brand__text small{font-size:9.5px!important;opacity:.72!important}
.site-nav__menu{gap:8px!important}
.site-nav__menu>li>a{min-height:82px!important;padding-inline:15px!important;font-size:13px!important;font-weight:700!important;letter-spacing:.005em!important}
.site-nav__menu>li>a::after{height:1px!important;inset-inline:16px!important;background:var(--br-copper-light)!important}
.brando-action{width:38px!important;height:38px!important}

/* HERO — keep composition, only refine finish */
.brando-hero__content{padding-inline:clamp(54px,5.2vw,100px)!important}
.brando-hero__title{font-size:clamp(62px,5.45vw,88px)!important;letter-spacing:-.052em!important}
.brando-hero__title strong{color:var(--br-copper-light)!important}
.brando-hero__lead{max-width:470px!important;color:#c9c4bd!important}
.brando-hero__cta{min-width:176px!important;min-height:52px!important;border-radius:5px!important;background:var(--br-copper)!important;box-shadow:0 14px 34px rgba(142,72,36,.18)!important}
.brando-hero__benefits{min-height:66px!important}
.brando-hero__benefit{font-size:11.8px!important;color:#aaa49d!important}
.brando-hero__benefit svg{width:22px!important;height:22px!important}

/* SECTION TYPOGRAPHY — more editorial, same spacing rhythm */
.brando-categories__eyebrow,.brando-best-sellers__eyebrow,.brando-new-arrivals__eyebrow,.brando-promo__eyebrow,.brando-newsletter__eyebrow{font-size:9.5px!important;letter-spacing:.11em!important;font-weight:800!important}
.brando-categories__title,.brando-best-sellers__title{font-size:clamp(42px,3.5vw,56px)!important;letter-spacing:-.045em!important}
.brando-new-arrivals__title{font-size:clamp(34px,3vw,44px)!important;letter-spacing:-.038em!important}
.brando-categories__subtitle,.brando-best-sellers__subtitle,.brando-new-arrivals__subtitle{font-size:13px!important;line-height:1.9!important;max-width:720px!important}

/* CATEGORIES — same 6 equal cards; more collection-like, less UI-like */
.brando-categories{padding:88px 0 96px!important;background:var(--br-ivory)!important}
.brando-categories__head{margin-bottom:38px!important}
.brando-categories__grid{grid-template-columns:repeat(6,minmax(0,1fr))!important;gap:16px!important}
.brando-category-card{border:0!important;border-radius:9px!important;box-shadow:0 18px 44px rgba(16,12,9,.07)!important;background:#111!important}
.brando-category-card:hover{transform:translateY(-4px)!important;box-shadow:0 28px 66px rgba(16,12,9,.115)!important}
.brando-category-card__media{aspect-ratio:4/5.15!important;background:#ded6ca!important}
.brando-category-card__media::after{background:linear-gradient(180deg,rgba(0,0,0,.01) 28%,rgba(0,0,0,.08) 48%,rgba(0,0,0,.82) 100%)!important}
.brando-category-card__media img{filter:saturate(.62) contrast(1.055) brightness(.94)!important}
.brando-category-card:hover .brando-category-card__media img{transform:scale(1.035)!important;filter:saturate(.70) contrast(1.06) brightness(.96)!important}
.brando-category-card__content{inset-inline:17px!important;bottom:17px!important;padding-inline-end:0!important}
.brando-category-card__name{font-size:17.5px!important;line-height:1.35!important;font-weight:820!important;letter-spacing:-.02em!important}
.brando-category-card__hint{font-size:9.5px!important;opacity:.72!important}
.brando-category-card__icon{width:30px!important;height:30px!important;left:14px!important;bottom:14px!important;background:rgba(9,10,10,.70)!important;border:1px solid rgba(182,109,66,.65)!important;color:#fff!important}
.brando-category-card__icon svg{width:14px!important;height:14px!important;stroke:#fff!important}

/* BEST SELLERS — same 4 cards, stronger luxury commerce system */
.brando-best-sellers{padding:92px 0 104px!important;background:linear-gradient(180deg,#f1ebe2 0%,#ebe3d7 100%)!important}
.brando-best-sellers__head{margin-bottom:36px!important}
.brando-best-sellers__grid{grid-template-columns:repeat(4,minmax(0,1fr))!important;gap:22px!important}
.brando-product-card{border:0!important;border-radius:9px!important;background:#fbfaf7!important;box-shadow:0 18px 46px rgba(17,13,9,.065)!important}
.brando-product-card:hover{transform:translateY(-4px)!important;box-shadow:0 30px 72px rgba(17,13,9,.115)!important}
.brando-product-card__media{aspect-ratio:4/5.15!important;background:#e5ddd1!important}
.brando-product-card__media img{filter:saturate(.70) contrast(1.045) brightness(.97)!important}
.brando-product-card__content{min-height:178px!important;padding:19px 20px 20px!important}
.brando-product-card__name{min-height:44px!important;font-size:15.5px!important;line-height:1.55!important;font-weight:760!important;letter-spacing:-.012em!important}
.brando-product-card__rating{margin-top:6px!important;transform:scale(.9);transform-origin:right center;opacity:.52!important}
.brando-product-card__price{font-size:20px!important;font-weight:850!important;letter-spacing:-.02em!important;margin-top:8px!important}
.brando-product-card__wishlist{width:34px!important;height:34px!important;top:12px!important;left:12px!important;background:rgba(251,250,247,.86)!important;border:0!important;box-shadow:0 5px 18px rgba(0,0,0,.06)!important;opacity:.86!important}
.brando-product-card__cart,.brando-product-card .button,.brando-product-card .add_to_cart_button{min-height:38px!important;padding:9px 13px!important;border-radius:4px!important;background:#101111!important;font-size:10.5px!important;font-weight:750!important;letter-spacing:.01em!important}
.brando-product-card__cart:hover,.brando-product-card .button:hover,.brando-product-card .add_to_cart_button:hover{background:var(--br-copper)!important}

/* PROMO — same split banner, calmer campaign treatment */
.brando-promo{padding:82px 0 88px!important;background:#faf8f4!important}
.brando-promo__card{min-height:470px!important;border-radius:10px!important;border:0!important;box-shadow:0 34px 82px rgba(15,12,9,.12)!important}
.brando-promo__content{padding:68px 72px!important;background:radial-gradient(circle at 88% 8%,rgba(142,72,36,.09),transparent 28%),linear-gradient(145deg,#070808,#111212)!important}
.brando-promo__title{font-size:clamp(43px,3.9vw,61px)!important;letter-spacing:-.045em!important}
.brando-promo__title strong{color:var(--br-copper-light)!important}
.brando-promo__text{font-size:13px!important;color:#aaa49d!important}
.brando-promo__cta{min-height:46px!important;padding:11px 22px!important;border-radius:4px!important;background:var(--br-copper)!important;font-size:10.8px!important;box-shadow:none!important}
.brando-promo__visual{min-height:470px!important;filter:saturate(.65) contrast(1.06) brightness(.90)!important}
.brando-promo__badge{width:82px!important;height:82px!important;left:24px!important;bottom:24px!important;background:rgba(142,72,36,.90)!important;border:1px solid rgba(255,255,255,.18)!important;box-shadow:0 12px 32px rgba(0,0,0,.20)!important;font-size:11px!important}

/* NEW ARRIVALS — deliberately quieter than best sellers */
.brando-new-arrivals{padding:84px 0 92px!important;background:#fcfbf8!important}
.brando-new-arrivals .woocommerce ul.products{grid-template-columns:repeat(4,minmax(0,1fr))!important;gap:20px!important}
.brando-new-arrivals .woocommerce ul.products li.product{border:0!important;border-radius:7px!important;background:#fff!important;box-shadow:0 10px 28px rgba(18,14,10,.045)!important;padding-bottom:18px!important}
.brando-new-arrivals .woocommerce ul.products li.product:hover{transform:translateY(-3px)!important;box-shadow:0 20px 46px rgba(18,14,10,.075)!important}
.brando-new-arrivals .woocommerce ul.products li.product a img{aspect-ratio:4/5!important;filter:saturate(.58) contrast(1.035) brightness(.98)!important;margin-bottom:16px!important}
.brando-new-arrivals .woocommerce ul.products li.product .woocommerce-loop-product__title{font-size:14.5px!important;font-weight:700!important;padding-inline:18px!important}
.brando-new-arrivals .woocommerce ul.products li.product .price{font-size:16.5px!important;margin-inline:18px!important;font-weight:800!important}
.brando-new-arrivals .woocommerce ul.products li.product .button,.brando-new-arrivals .woocommerce ul.products li.product .add_to_cart_button{min-height:36px!important;margin:13px 18px 0!important;padding:8px 12px!important;border:1px solid #d9d1c6!important;border-radius:4px!important;background:transparent!important;color:#1c1d1d!important;font-size:10px!important;font-weight:750!important}
.brando-new-arrivals .woocommerce ul.products li.product .button:hover,.brando-new-arrivals .woocommerce ul.products li.product .add_to_cart_button:hover{border-color:#1c1d1d!important;background:#1c1d1d!important;color:#fff!important}
.brando-new-arrivals .woocommerce ul.products li.product:before{background:rgba(15,16,16,.88)!important;border-radius:3px!important;font-size:8.5px!important}

/* TRUST — same four items, more architectural and less ecommerce-standard */
.brando-trust{background:#eee8de!important;border-block:1px solid #ded5c8!important}
.brando-trust__inner{border-inline:0!important}
.brando-trust__item{position:relative!important;gap:12px!important;padding:24px 26px!important}
.brando-trust__item:not(:last-child)::after{content:"";position:absolute;top:24%;bottom:24%;inset-inline-end:0;width:1px;background:#d7cec1}
.brando-trust__icon{width:38px!important;height:38px!important;flex-basis:38px!important;background:transparent!important;border:1px solid rgba(142,72,36,.28)!important;color:var(--br-copper)!important}
.brando-trust__icon svg{width:18px!important;height:18px!important}
.brando-trust__item h3{font-size:13px!important;font-weight:760!important}
.brando-trust__item p{font-size:10.8px!important;color:#817b73!important}

/* NEWSLETTER + FOOTER — same layout, one stronger brand ending */
.brando-newsletter{padding:76px 0 0!important;background:#eee8de!important}
.brando-newsletter__inner{grid-template-columns:1.08fr .92fr!important;gap:58px!important;padding:60px 64px!important;border-radius:10px!important;border:0!important;background:radial-gradient(circle at 88% 10%,rgba(142,72,36,.065),transparent 25%),linear-gradient(140deg,#070808,#121313)!important;box-shadow:0 30px 76px rgba(0,0,0,.13)!important;transform:translateY(40px)}
.brando-newsletter__inner::before{width:1px!important;background:linear-gradient(180deg,transparent,var(--br-copper-light),transparent)!important}
.brando-newsletter h2{font-size:clamp(34px,3.55vw,50px)!important;letter-spacing:-.045em!important;line-height:1.08!important}
.brando-newsletter p{font-size:13px!important;color:#98928b!important;max-width:560px!important}
.brando-newsletter__form{border-radius:5px!important;background:rgba(255,255,255,.025)!important;border-color:rgba(255,255,255,.06)!important}
.brando-newsletter__form input{height:48px!important;font-size:12.5px!important}
.brando-newsletter__form button{min-height:48px!important;border-radius:4px!important;background:var(--br-copper)!important;font-size:10.5px!important}
.site-footer.brando-footer{background:radial-gradient(circle at 86% 8%,rgba(142,72,36,.035),transparent 28%),#050606!important}
.brando-footer__inner{padding-top:116px!important}
.brando-footer__grid{gap:64px!important;padding-bottom:54px!important}
.brando-footer__brand-name{font-size:40px!important;color:var(--br-copper-light)!important;letter-spacing:-.05em!important}
.brando-footer__brand p{max-width:380px!important;color:#716d68!important;font-size:12.5px!important}
.brando-footer__column h3{font-size:11.5px!important;letter-spacing:.02em!important}
.brando-footer__column a{font-size:12px!important;color:#6e6e6e!important}
.brando-footer__social a{height:34px!important;min-width:40px!important;font-size:9.5px!important;border-radius:999px!important;background:#0b0c0c!important}
.brando-footer__payments{padding:23px 0!important}
.brando-footer__payment-list b{font-size:9.3px!important;padding:6px 10px!important;background:#0a0b0b!important;color:#78736d!important}

/* Keep 0.5.1 motion system; slightly calmer reveal */
.brando-reveal{transform:translateY(18px);transition-duration:.72s!important}

@media(max-width:1200px){
  .brando-categories__grid{grid-template-columns:repeat(3,minmax(0,1fr))!important}
}
@media(max-width:980px){
  .brando-header__inner{min-height:72px!important}
  .brando-best-sellers__grid,.brando-new-arrivals .woocommerce ul.products{grid-template-columns:repeat(2,minmax(0,1fr))!important}
  .brando-newsletter__inner{grid-template-columns:1fr!important;padding:44px 38px!important}
}
@media(max-width:720px){
  .brando-categories__grid{grid-template-columns:repeat(2,minmax(0,1fr))!important}
  .brando-category-card__media{aspect-ratio:1/1!important}
  .brando-trust__item:not(:last-child)::after{display:none!important}
}
@media(max-width:520px){
  .brando-best-sellers__grid,.brando-new-arrivals .woocommerce ul.products{grid-template-columns:1fr!important}
  .brando-newsletter__inner{padding:36px 24px!important}
}
/* BRANDO LUXURY FINISH v0.5.3 END */'''

css_new = css + finish_css + "\n"

for required_css in [
    "grid-template-columns:repeat(6,minmax(0,1fr))",
    "grid-template-columns:repeat(4,minmax(0,1fr))",
    "BRANDO LUXURY FINISH v0.5.3 START",
]:
    if required_css not in css_new:
        raise SystemExit(f"Required CSS invariant missing: {required_css}")

write_atomic("style.css", style_new)
write_atomic("functions.php", functions_new)
write_atomic("assets/css/luxury-v3.css", css_new)

print("PATCH_VERSION=0.5.3")
print("LAYOUT_STRUCTURE_CHANGED=NO")
print("SECTION_ORDER_CHANGED=NO")
print("TEMPLATES_CHANGED=NO")
print("CATEGORY_GRID_COLUMNS=6")
print("BEST_SELLERS_GRID_COLUMNS=4")
print("HERO_COMPOSITION_CHANGED=NO")
print("PRODUCT_CARD_FINISH=YES")
print("CATEGORY_FINISH=YES")
print("PROMO_FINISH=YES")
print("TRUST_FINISH=YES")
print("NEWSLETTER_FOOTER_FINISH=YES")
print("MOTION_SYSTEM_PRESERVED=YES")
