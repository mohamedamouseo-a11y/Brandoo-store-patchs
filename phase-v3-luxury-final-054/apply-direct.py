#!/usr/bin/env python3
from pathlib import Path
import re
import sys

VERSION = "0.5.4"
START = "/* BRANDO LUXURY FINAL FINISH v0.5.4 START */"
END = "/* BRANDO LUXURY FINAL FINISH v0.5.4 END */"

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
    tmp = path.with_suffix(path.suffix + ".tmp-brando-054")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


style = read("style.css")
functions = read("functions.php")
front = read("front-page.php")
header = read("header.php")
footer = read("footer.php")
css = read("assets/css/luxury-v3.css")
motion = read("assets/js/luxury-motion.js")

# Require the approved 0.5.3 baseline so this pass never lands on an older visual state.
if "BRANDO LUXURY FINISH v0.5.3" not in css:
    raise SystemExit("Expected v0.5.3 baseline marker not found in luxury-v3.css")

# Preserve the exact page composition/order.
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
    raise SystemExit("Trust/newsletter/footer structure check failed")

for forbidden in ["999 ر.س", "WELCOME10", "+966", "brando.sa"]:
    if forbidden in header + "\n" + front + "\n" + footer:
        raise SystemExit(f"Forbidden locale token returned: {forbidden}")

if "IntersectionObserver" not in motion or "scrollIntoView" not in motion:
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

# Idempotent rerun: replace only this pass while preserving every prior approved layer.
pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
css = pattern.sub("", css).rstrip() + "\n\n"

finish = r'''/* BRANDO LUXURY FINAL FINISH v0.5.4 START */
:root{
  --br-final-ink:#0a0a09;
  --br-final-copper:#9a4d21;
  --br-final-copper-soft:#b56637;
  --br-final-ivory:#f8f4ed;
  --br-final-beige:#e9dfd2;
  --br-final-line:rgba(72,56,42,.12);
}

/* Keep Hero/Categories composition intact; only sharpen the finish. */
.brando-header{box-shadow:0 12px 34px rgba(0,0,0,.20)!important}
.brando-brand__text strong{font-weight:850!important}
.brando-categories__head{margin-bottom:38px!important}
.brando-category-card{box-shadow:0 16px 38px rgba(14,12,10,.085)!important}
.brando-category-card__icon{width:32px!important;height:32px!important;background:rgba(10,10,9,.82)!important;border-color:rgba(255,255,255,.22)!important}
.brando-category-card__hint{opacity:.72!important}

/* BEST SELLERS — primary commerce showcase, same 4-card grid. */
.brando-best-sellers{
  padding:94px 0 104px!important;
  background:linear-gradient(180deg,#eee6da 0%,var(--br-final-beige) 100%)!important;
  border-block:1px solid rgba(91,70,50,.12)!important;
}
.brando-best-sellers__head{margin-bottom:38px!important}
.brando-best-sellers__grid{gap:28px!important}
.brando-product-card{
  border:1px solid rgba(83,64,47,.08)!important;
  border-radius:9px!important;
  background:#fcfaf6!important;
  box-shadow:0 18px 44px rgba(20,15,10,.075)!important;
}
.brando-product-card:hover{transform:translateY(-4px)!important;box-shadow:0 30px 68px rgba(20,15,10,.13)!important}
.brando-product-card__media{aspect-ratio:4/5.15!important;background:#ded6ca!important}
.brando-product-card__media img{object-fit:cover!important;filter:saturate(.72) contrast(1.045) brightness(.98)!important}
.brando-product-card__content{min-height:176px!important;padding:20px 20px 19px!important}
.brando-product-card__name{min-height:46px!important;font-size:16.5px!important;font-weight:780!important;letter-spacing:-.012em!important}
.brando-product-card__rating{margin-top:5px!important;opacity:.42!important;transform:scale(.92);transform-origin:right center}
.brando-product-card__price{font-size:20px!important;font-weight:900!important;letter-spacing:-.02em!important}
.brando-product-card__wishlist{width:34px!important;height:34px!important;top:12px!important;left:12px!important;background:rgba(249,247,242,.88)!important;border-color:rgba(20,18,15,.12)!important;box-shadow:none!important}
.brando-product-card__cart,.brando-product-card .button,.brando-product-card .add_to_cart_button{
  min-height:39px!important;padding:9px 14px!important;border:1px solid #181817!important;border-radius:4px!important;
  background:transparent!important;color:#181817!important;font-size:10.5px!important;font-weight:850!important;box-shadow:none!important;
}
.brando-product-card__cart:hover,.brando-product-card .button:hover,.brando-product-card .add_to_cart_button:hover{background:#181817!important;color:#fff!important}

/* PROMO — same split, calmer luxury campaign. */
.brando-promo{padding:82px 0 90px!important;background:#faf7f1!important}
.brando-promo__card{min-height:490px!important;border-radius:10px!important;border-color:rgba(58,46,34,.08)!important;box-shadow:0 34px 88px rgba(20,15,10,.13)!important}
.brando-promo__content{flex-basis:46%!important;padding:72px 70px!important;background:radial-gradient(circle at 90% 12%,rgba(154,77,33,.10),transparent 27%),linear-gradient(145deg,#090a0a,#131414)!important}
.brando-promo__visual{flex-basis:54%!important;min-height:490px!important;filter:saturate(.67) contrast(1.055) brightness(.91)!important}
.brando-promo__title{font-size:clamp(42px,3.7vw,58px)!important;line-height:1.08!important}
.brando-promo__title strong{color:var(--br-final-copper-soft)!important}
.brando-promo__text{max-width:470px!important;color:#a9a39c!important}
.brando-promo__cta{min-height:47px!important;margin-top:26px!important;padding:12px 23px!important;border-radius:4px!important;background:var(--br-final-copper)!important;box-shadow:none!important}
.brando-promo__badge{width:82px!important;height:82px!important;left:24px!important;bottom:22px!important;background:rgba(154,77,33,.92)!important;border-color:rgba(255,255,255,.12)!important;box-shadow:0 10px 24px rgba(0,0,0,.18)!important;transform:scale(.92)}

/* NEW ARRIVALS — deliberately quieter than Best Sellers, same 4 products. */
.brando-new-arrivals{padding:84px 0 92px!important;background:#fffdf9!important}
.brando-new-arrivals__head{margin-bottom:34px!important}
.brando-new-arrivals .woocommerce ul.products{gap:24px!important}
.brando-new-arrivals .woocommerce ul.products li.product{
  border:1px solid rgba(73,57,42,.08)!important;border-radius:7px!important;background:#fff!important;
  box-shadow:0 10px 26px rgba(20,15,10,.045)!important;padding-bottom:18px!important;
}
.brando-new-arrivals .woocommerce ul.products li.product:hover{transform:translateY(-3px)!important;box-shadow:0 19px 42px rgba(20,15,10,.08)!important}
.brando-new-arrivals .woocommerce ul.products li.product a img{
  aspect-ratio:4/5!important;object-fit:cover!important;margin-bottom:17px!important;
  filter:saturate(.62) contrast(1.025) brightness(.99)!important;
}
.brando-new-arrivals .woocommerce ul.products li.product .woocommerce-loop-product__title{padding-inline:18px!important;font-size:15px!important;font-weight:720!important;min-height:46px}
.brando-new-arrivals .woocommerce ul.products li.product .price{margin:8px 18px 0!important;font-size:17px!important;font-weight:850!important}
.brando-new-arrivals .woocommerce ul.products li.product .button,.brando-new-arrivals .woocommerce ul.products li.product .add_to_cart_button{
  min-height:37px!important;margin:13px 18px 0!important;padding:8px 13px!important;border:1px solid #242423!important;border-radius:3px!important;
  background:transparent!important;color:#242423!important;font-size:10px!important;
}
.brando-new-arrivals .woocommerce ul.products li.product .button:hover,.brando-new-arrivals .woocommerce ul.products li.product .add_to_cart_button:hover{background:#242423!important;color:#fff!important}
.brando-new-arrivals .woocommerce ul.products li.product:before{padding:4px 8px!important;border-radius:3px!important;background:rgba(18,18,17,.88)!important;font-size:8.5px!important}

/* TRUST — same four items, less ecommerce-boxy and more editorial. */
.brando-trust{background:#efe8dd!important;border-color:#ded4c6!important}
.brando-trust__inner{min-height:108px!important;border-inline:0!important}
.brando-trust__item{position:relative!important;gap:15px!important;padding:30px 28px!important}
.brando-trust__item:not(:last-child)::after{content:"";position:absolute;inset-inline-end:0;top:30%;bottom:30%;width:1px;background:rgba(91,70,50,.13)}
.brando-trust__icon{width:36px!important;height:36px!important;flex-basis:36px!important;background:transparent!important;border:0!important;color:var(--br-final-copper)!important}
.brando-trust__icon svg{width:21px!important;height:21px!important;stroke:var(--br-final-copper)!important}
.brando-trust__item h3{font-size:14px!important;font-weight:820!important}
.brando-trust__item p{font-size:11.5px!important;line-height:1.7!important;color:#81786e!important}

/* NEWSLETTER — stronger entrance into footer, same block/form. */
.brando-newsletter{padding:86px 0 0!important;background:#eae1d5!important}
.brando-newsletter__inner{
  grid-template-columns:1.18fr .82fr!important;gap:62px!important;padding:64px 68px!important;border-radius:10px!important;
  background:radial-gradient(circle at 88% 6%,rgba(154,77,33,.08),transparent 24%),linear-gradient(135deg,#080909,#121313)!important;
  box-shadow:0 28px 72px rgba(0,0,0,.13)!important;transform:translateY(42px)!important;
}
.brando-newsletter h2{font-size:clamp(34px,3.7vw,50px)!important;line-height:1.08!important}
.brando-newsletter p{max-width:620px!important;color:#aaa39b!important;line-height:1.9!important}
.brando-newsletter__form{max-width:520px!important;border-radius:5px!important;background:rgba(255,255,255,.025)!important}
.brando-newsletter__form input{height:54px!important;font-size:13px!important}
.brando-newsletter__form button{min-height:54px!important;border-radius:3px!important;background:var(--br-final-copper)!important;padding-inline:28px!important}

/* FOOTER — heavier brand ending, less dead black space. */
.site-footer.brando-footer{background:radial-gradient(circle at 84% 7%,rgba(154,77,33,.045),transparent 24%),#050606!important}
.brando-footer__inner{padding:122px 0 34px!important}
.brando-footer__grid{gap:68px!important;padding-bottom:44px!important}
.brando-footer__brand-name{font-size:41px!important;margin-bottom:15px!important;color:var(--br-final-copper-soft)!important}
.brando-footer__brand p{max-width:430px!important;font-size:13px!important;line-height:2!important;color:#817b74!important}
.brando-footer__column h3{font-size:12.5px!important;margin-bottom:19px!important}
.brando-footer__column a{font-size:12.5px!important;color:#85817c!important}
.brando-footer__payments{padding:22px 0!important}
.brando-footer__payment-list b{font-size:9.5px!important;padding:6px 10px!important;background:#0b0c0c!important;border-color:#1b1c1c!important;color:#77716b!important}
.brando-footer__bottom{padding-top:17px!important}

@media(max-width:980px){
  .brando-promo__content,.brando-promo__visual{flex-basis:auto!important}
  .brando-newsletter__inner{grid-template-columns:1fr!important;gap:34px!important;padding:46px 38px!important}
  .brando-trust__item:not(:last-child)::after{display:none}
}
@media(max-width:720px){
  .brando-best-sellers{padding-block:64px!important}
  .brando-promo{padding-block:60px!important}
  .brando-new-arrivals{padding-block:62px!important}
  .brando-newsletter__inner{padding:36px 25px!important;transform:translateY(26px)!important}
  .brando-footer__inner{padding-top:92px!important}
}
/* BRANDO LUXURY FINAL FINISH v0.5.4 END */'''

css_new = css + finish + "\n"

# Only these three files are written by this pass.
write_atomic("style.css", style_new)
write_atomic("functions.php", functions_new)
write_atomic("assets/css/luxury-v3.css", css_new)

print("PATCH_VERSION=0.5.4")
print("LAYOUT_STRUCTURE_CHANGED=NO")
print("SECTION_ORDER_CHANGED=NO")
print("TEMPLATES_CHANGED=NO")
print("HERO_COMPOSITION_CHANGED=NO")
print("CATEGORIES_COMPOSITION_CHANGED=NO")
print("BEST_SELLERS_FINISH=YES")
print("PRODUCT_CARD_FINISH=YES")
print("PROMO_FINISH=YES")
print("NEW_ARRIVALS_FINISH=YES")
print("TRUST_FINISH=YES")
print("NEWSLETTER_FOOTER_FINISH=YES")
print("MOTION_SYSTEM_PRESERVED=YES")
