#!/usr/bin/env python3
from pathlib import Path
import re
import sys

VERSION = "0.5.2"
MARKER_START = "/* BRANDO LUXURY VISUAL REFINEMENT v0.5.2 START */"
MARKER_END = "/* BRANDO LUXURY VISUAL REFINEMENT v0.5.2 END */"

if len(sys.argv) != 2:
    raise SystemExit("Usage: apply-direct.py /absolute/path/to/brando")

theme = Path(sys.argv[1]).resolve()
if not theme.is_dir():
    raise SystemExit(f"Theme directory not found: {theme}")

required = [
    "style.css", "functions.php", "header.php", "front-page.php", "footer.php",
    "assets/css/luxury-v3.css", "assets/js/luxury-motion.js",
]
missing = [name for name in required if not (theme / name).is_file()]
if missing:
    raise SystemExit("Missing theme files: " + ", ".join(missing))

def read(rel):
    return (theme / rel).read_text(encoding="utf-8")

def write_atomic(rel, content):
    path = theme / rel
    tmp = path.with_suffix(path.suffix + ".tmp-brando-052")
    tmp.write_text(content, encoding="utf-8")
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

currency_filter = r'''
if (!function_exists('brando_localize_currency_symbol')) {
    function brando_localize_currency_symbol($symbol, $currency) {
        if ('EGP' === $currency) {
            return 'ج.م';
        }
        return $symbol;
    }
    add_filter('woocommerce_currency_symbol', 'brando_localize_currency_symbol', 10, 2);
}
'''.strip()

if "brando_localize_currency_symbol" not in functions_new:
    insert_at = functions_new.rfind("?>")
    if insert_at == -1:
        functions_new = functions_new.rstrip() + "\n\n" + currency_filter + "\n"
    else:
        functions_new = functions_new[:insert_at].rstrip() + "\n\n" + currency_filter + "\n\n" + functions_new[insert_at:]

front = read("front-page.php")

category_images = {
    "أدوات الطبخ": "https://images.unsplash.com/photo-1698939586636-98209ecf8516?auto=format&fit=crop&fm=jpg&q=84&w=900",
    "أواني التقديم": "https://images.unsplash.com/photo-1772453609632-2f4aa857f56e?auto=format&fit=crop&fm=jpg&q=84&w=900",
    "التخزين والتنظيم": "https://images.unsplash.com/photo-1676976500593-3dfec0b17754?auto=format&fit=crop&fm=jpg&q=84&w=900",
    "مستلزمات الخَبز": "https://images.unsplash.com/photo-1765451490611-dfa0a7aa17d3?auto=format&fit=crop&fm=jpg&q=84&w=900",
    "أدوات المائدة": "https://images.unsplash.com/photo-1773609688714-2f6354ae4f3c?auto=format&fit=crop&fm=jpg&q=84&w=900",
    "تجهيزات المطبخ": "https://images.unsplash.com/photo-1556910602-38f53e68e15d?auto=format&fit=crop&fm=jpg&q=84&w=900",
}
product_images = {
    "طقم أواني طهي عملي": "https://images.unsplash.com/photo-1621494547944-5ddbc84514b2?auto=format&fit=crop&fm=jpg&q=84&w=1000",
    "طقم تقديم أنيق": "https://images.unsplash.com/photo-1772453609632-2f4aa857f56e?auto=format&fit=crop&fm=jpg&q=84&w=1000",
    "منظم مطبخ متعدد الاستخدام": "https://images.unsplash.com/photo-1676976500593-3dfec0b17754?auto=format&fit=crop&fm=jpg&q=84&w=1000",
    "مجموعة مستلزمات الخَبز": "https://images.unsplash.com/photo-1596002937504-1246a49fba48?auto=format&fit=crop&fm=jpg&q=84&w=1000",
}

def replace_named_image(text, name, url):
    pattern = re.compile(
        r"('name'\s*=>\s*'" + re.escape(name) + r"'\s*,\s*(?:\r?\n\s*)?'image'\s*=>\s*')[^']+(')",
        re.M,
    )
    new_text, count = pattern.subn(lambda m: m.group(1) + url + m.group(2), text, count=1)
    if count == 0 and url not in text:
        raise SystemExit(f"Could not update fallback image for: {name}")
    return new_text

front_new = front
for name, url in category_images.items():
    front_new = replace_named_image(front_new, name, url)
for name, url in product_images.items():
    front_new = replace_named_image(front_new, name, url)

for amount in [349, 229, 179, 199]:
    front_new = front_new.replace(
        f"'price_text' => '{amount} ر.س'",
        f"'price_text' => function_exists('wc_price') ? wp_strip_all_tags(wc_price({amount})) : '{amount}'",
    )

if " ر.س" in front_new:
    raise SystemExit("Hardcoded Saudi currency remains in front-page.php")

header = read("header.php")
footer = read("footer.php")
combined = "\n".join([header, front_new, footer])
for forbidden in ["999 ر.س", "WELCOME10", " ر.س", "+966", "brando.sa"]:
    if forbidden in combined:
        raise SystemExit(f"Forbidden locale token remains: {forbidden}")

css = read("assets/css/luxury-v3.css")
css = re.sub(
    re.escape(MARKER_START) + r".*?" + re.escape(MARKER_END) + r"\s*",
    "",
    css,
    flags=re.S,
).rstrip()

refinement = r'''
/* BRANDO LUXURY VISUAL REFINEMENT v0.5.2 START */
:root{
  --br-copper:#8f4c26;
  --br-copper-light:#b56b3a;
  --br-ivory:#f6f1e8;
  --br-beige:#e9e0d4;
  --br-beige-deep:#e2d7c8;
  --br-line:#d8cdbf;
  --br-muted:#746c63;
  --br-shadow:0 20px 60px rgba(18,14,10,.07);
  --br-shadow-strong:0 38px 100px rgba(10,8,6,.16);
}
.brando-topbar{font-size:10.5px!important}
.brando-topbar__inner{min-height:28px!important}
.brando-header__inner{min-height:94px!important;gap:38px!important}
.brando-branding{min-width:205px!important}
.brando-brand__mark{width:58px!important;height:58px!important}
.brando-brand__text strong{font-size:30px!important}
.site-nav__menu{gap:8px!important}
.site-nav__menu>li>a{min-height:94px!important;padding-inline:16px!important;font-size:13px!important;font-weight:720!important}
.brando-action{width:42px!important;height:42px!important;border:1px solid rgba(255,255,255,.045)!important;border-radius:50%!important}
.brando-hero__media{filter:saturate(.72) contrast(1.08) brightness(.86)!important}
.brando-hero__content{background:linear-gradient(90deg,rgba(5,5,5,0),rgba(5,5,5,.18) 24%,rgba(5,5,5,.67) 68%,rgba(5,5,5,.95) 100%)!important}
.brando-hero__title strong{color:#b96c3b!important}
.brando-hero__cta{background:#98532b!important;border:1px solid rgba(255,255,255,.08)!important}
.brando-hero__cta:hover{background:#b96c3b!important}
.brando-categories{padding:92px 0 102px!important;background:#f7f2ea!important}
.brando-categories__head{margin-bottom:42px!important}
.brando-categories__grid{gap:20px!important}
.brando-category-card{border:0!important;border-radius:5px!important;box-shadow:0 16px 42px rgba(19,15,11,.075)!important}
.brando-category-card:hover{transform:translateY(-4px)!important;box-shadow:0 28px 68px rgba(19,15,11,.13)!important}
.brando-category-card__media{aspect-ratio:4/5!important;background:#ded4c6!important}
.brando-category-card__media::after{background:linear-gradient(180deg,rgba(7,7,7,0) 34%,rgba(7,7,7,.14) 57%,rgba(7,7,7,.88) 100%)!important}
.brando-category-card__media img{width:100%!important;height:100%!important;object-fit:cover!important;filter:saturate(.66) contrast(1.05) brightness(.93) sepia(.04)!important}
.brando-category-card__content{inset-inline:18px!important;bottom:18px!important;padding-inline-end:40px!important}
.brando-category-card__name{font-size:17px!important;font-weight:800!important;letter-spacing:-.015em!important}
.brando-category-card__hint{font-size:10px!important;color:rgba(255,255,255,.58)!important}
.brando-category-card__icon{width:32px!important;height:32px!important;left:16px!important;bottom:16px!important;background:rgba(143,76,38,.88)!important;border-color:rgba(255,255,255,.2)!important}
.brando-category-card:nth-child(1) img{object-position:center 58%!important}
.brando-category-card:nth-child(2) img{object-position:center 52%!important}
.brando-category-card:nth-child(3) img{object-position:center 48%!important}
.brando-category-card:nth-child(4) img{object-position:center 55%!important}
.brando-category-card:nth-child(5) img{object-position:center 50%!important}
.brando-category-card:nth-child(6) img{object-position:center 54%!important}
.brando-best-sellers{padding:96px 0 106px!important;background:linear-gradient(180deg,#eee6db 0%,#e9dfd2 100%)!important}
.brando-best-sellers__head{margin-bottom:38px!important}
.brando-best-sellers__grid{gap:26px!important}
.brando-product-card{border:0!important;border-radius:5px!important;background:#faf7f1!important;box-shadow:0 15px 42px rgba(18,14,10,.065)!important}
.brando-product-card:hover{transform:translateY(-4px)!important;box-shadow:0 28px 68px rgba(18,14,10,.12)!important}
.brando-product-card__media{aspect-ratio:4/5!important;background:#e2d8ca!important}
.brando-product-card__media img{width:100%!important;height:100%!important;object-fit:cover!important;filter:saturate(.68) contrast(1.045) brightness(.96)!important}
.brando-product-card__content{min-height:176px!important;padding:22px 22px 24px!important}
.brando-product-card__name{font-size:16px!important;font-weight:760!important}
.brando-product-card__rating{transform:scale(.9);transform-origin:right center;opacity:.52!important}
.brando-product-card__price{font-size:20px!important;letter-spacing:-.015em!important}
.brando-product-card__cart,.brando-product-card .button,.brando-product-card .add_to_cart_button{min-height:40px!important;border-radius:3px!important;background:#0b0c0c!important;font-size:10.8px!important;letter-spacing:.01em!important}
.brando-product-card__wishlist{width:34px!important;height:34px!important;top:14px!important;left:14px!important;border-color:rgba(20,20,20,.08)!important;background:rgba(250,248,244,.86)!important;box-shadow:none!important}
.brando-promo{padding:86px 0 92px!important;background:#f8f4ed!important}
.brando-promo__card{min-height:500px!important;border:0!important;border-radius:6px!important;box-shadow:0 34px 90px rgba(11,9,7,.16)!important}
.brando-promo__content{padding:72px 76px!important;background:radial-gradient(circle at 90% 10%,rgba(143,76,38,.10),transparent 29%),linear-gradient(145deg,#070808,#111212)!important}
.brando-promo__title{font-size:clamp(44px,4.15vw,66px)!important}
.brando-promo__title strong{color:#b96c3b!important}
.brando-promo__cta{border-radius:3px!important;background:#98532b!important;box-shadow:none!important}
.brando-promo__badge{width:82px!important;height:82px!important;left:26px!important;bottom:24px!important;background:rgba(7,8,8,.72)!important;border:1px solid rgba(185,108,59,.62)!important;color:#f0ddd0!important;box-shadow:none!important;backdrop-filter:blur(8px)}
.brando-new-arrivals{padding:88px 0 96px!important;background:#fffdf9!important}
.brando-new-arrivals .woocommerce ul.products{gap:24px!important}
.brando-new-arrivals .woocommerce ul.products li.product{border:0!important;border-radius:4px!important;background:#fff!important;box-shadow:0 7px 24px rgba(18,15,11,.04)!important}
.brando-new-arrivals .woocommerce ul.products li.product:hover{transform:translateY(-3px)!important;box-shadow:0 17px 44px rgba(18,15,11,.075)!important}
.brando-new-arrivals .woocommerce ul.products li.product a img{width:100%!important;height:auto!important;object-fit:cover!important;filter:saturate(.64) contrast(1.025) brightness(.98)!important}
.brando-new-arrivals .woocommerce ul.products li.product .woocommerce-loop-product__title{font-weight:700!important}
.brando-new-arrivals .woocommerce ul.products li.product .button,.brando-new-arrivals .woocommerce ul.products li.product .add_to_cart_button{border-radius:3px!important;background:#242525!important}
.brando-trust{background:#eee7dc!important}
.brando-trust__inner{border-inline:0!important}
.brando-trust__item{position:relative!important;padding:30px 28px!important}
.brando-trust__item:not(:last-child)::after{content:"";position:absolute;inset-block:24px;inset-inline-end:0;width:1px;background:#d8cdbf}
.brando-trust__icon{width:38px!important;height:38px!important;flex-basis:38px!important;background:transparent!important;border:1px solid #cdbfae!important;color:#8f4c26!important}
.brando-trust__icon svg{width:19px!important;height:19px!important;stroke:#8f4c26!important}
.brando-trust__item h3{font-size:14px!important}
.brando-trust__item p{font-size:11.5px!important}
.brando-newsletter{padding-top:82px!important;background:#e9e0d4!important}
.brando-newsletter__inner{gap:58px!important;padding:60px 66px!important;border-radius:6px!important;background:radial-gradient(circle at 91% 9%,rgba(143,76,38,.085),transparent 25%),linear-gradient(138deg,#070808,#121313)!important;box-shadow:0 28px 76px rgba(0,0,0,.13)!important;transform:translateY(44px)}
.brando-newsletter h2{font-size:clamp(34px,3.7vw,50px)!important}
.brando-newsletter__form{border-radius:3px!important;background:rgba(255,255,255,.025)!important}
.brando-newsletter__form button{border-radius:2px!important;background:#98532b!important}
.site-footer.brando-footer{background:radial-gradient(circle at 88% 5%,rgba(143,76,38,.04),transparent 25%),#050606!important}
.brando-footer__inner{padding-top:124px!important}
.brando-footer__grid{gap:68px!important;padding-bottom:56px!important}
.brando-footer__brand-name{font-size:42px!important;color:#b96c3b!important}
.brando-footer__brand p{max-width:520px!important;font-size:13px!important;color:#817a73!important}
.brando-footer__column h3{font-size:11.5px!important;color:#e9e2d9!important}
.brando-footer__column a{font-size:12px!important;color:#77716a!important}
.brando-footer__payment-list b{border-radius:3px!important;background:#0b0c0c!important}
.woocommerce-Price-amount.amount{white-space:nowrap}
.woocommerce-Price-currencySymbol{font-size:.82em!important;font-weight:700!important;color:#6f665d!important;margin-inline-start:3px}
@media(max-width:980px){
  .brando-header__inner{min-height:76px!important}
  .brando-category-card{border-radius:4px!important}
  .brando-newsletter__inner{transform:translateY(32px)}
}
@media(max-width:720px){
  .brando-topbar{display:none!important}
  .brando-header__inner{min-height:70px!important}
  .brando-brand__mark{width:48px!important;height:48px!important}
  .brando-category-card__media{aspect-ratio:1/1!important}
  .brando-trust__item:not(:last-child)::after{inset-block:auto;bottom:0;inset-inline:20px;width:auto;height:1px}
  .brando-newsletter__inner{transform:translateY(24px)}
}
/* BRANDO LUXURY VISUAL REFINEMENT v0.5.2 END */
'''.strip()

css_new = css + "\n\n" + refinement + "\n"

js = read("assets/js/luxury-motion.js")
for token in ["IntersectionObserver", "scrollIntoView"]:
    if token not in js:
        raise SystemExit(f"Expected motion token missing: {token}")

if ".brando-categories__grid" not in css_new or "repeat(6" not in css_new:
    raise SystemExit("Category grid structure guard failed")
if ".brando-best-sellers__grid" not in css_new or "repeat(4" not in css_new:
    raise SystemExit("Best Sellers grid structure guard failed")
if ".brando-new-arrivals .woocommerce ul.products" not in css_new:
    raise SystemExit("New Arrivals structure guard failed")

write_atomic("style.css", style_new)
write_atomic("functions.php", functions_new)
write_atomic("front-page.php", front_new)
write_atomic("assets/css/luxury-v3.css", css_new)

print(f"PATCH_VERSION={VERSION}")
print("LAYOUT_STRUCTURE_CHANGED=NO")
print("SECTION_ORDER_CHANGED=NO")
print("CATEGORY_GRID_COLUMNS=6")
print("BEST_SELLERS_GRID_COLUMNS=4")
print("DEMO_PRICE_CURRENCY=WOOCOMMERCE_CONFIG")
print("EGP_SYMBOL_ARABIC=YES")
print("CATEGORY_ART_DIRECTION_UPDATED=YES")
print("PRODUCT_FALLBACK_ART_DIRECTION_UPDATED=YES")
print("LUXURY_VISUAL_REFINEMENT_PRESENT=YES")
print("HERO_ANIMATION_CODE_PRESENT=YES" if "brandoHeroDrift" in css_new else "HERO_ANIMATION_CODE_PRESENT=NO")
print("INTERSECTION_OBSERVER_PRESENT=YES")
print("SMOOTH_SCROLL_CODE_PRESENT=YES")
