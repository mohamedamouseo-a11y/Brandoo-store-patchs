#!/usr/bin/env python3
from pathlib import Path
import re
import sys

VERSION = "0.5.5"
CSS_START = "/* BRANDO ART DIRECTION LOCK v0.5.5 START */"
CSS_END = "/* BRANDO ART DIRECTION LOCK v0.5.5 END */"
JS_START = "/* BRANDO DEMO ART DIRECTION v0.5.5 START */"
JS_END = "/* BRANDO DEMO ART DIRECTION v0.5.5 END */"

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
    tmp = path.with_suffix(path.suffix + ".tmp-brando-055")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


style = read("style.css")
functions = read("functions.php")
header = read("header.php")
front = read("front-page.php")
footer = read("footer.php")
css = read("assets/css/luxury-v3.css")
js = read("assets/js/luxury-motion.js")

# Require the exact approved finishing baseline.
if "BRANDO LUXURY FINAL FINISH v0.5.4" not in css:
    raise SystemExit("Expected v0.5.4 baseline marker not found")

# Preserve current composition and locale protections.
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

# Idempotent CSS layer.
css_pattern = re.compile(re.escape(CSS_START) + r".*?" + re.escape(CSS_END), re.S)
css = css_pattern.sub("", css).rstrip() + "\n\n"
css_finish = r'''/* BRANDO ART DIRECTION LOCK v0.5.5 START */
/* Keep the approved 0.5.4 composition. This pass fixes visual consistency only. */
.brando-new-arrivals .woocommerce ul.products li.product a img{
  aspect-ratio:4/5!important;
  width:100%!important;
  height:auto!important;
  object-fit:cover!important;
  object-position:center!important;
  filter:saturate(.70) contrast(1.045) brightness(.97) sepia(.025)!important;
  transition:transform .5s cubic-bezier(.2,.7,.2,1),filter .3s ease!important;
}
.brando-new-arrivals .woocommerce ul.products li.product:hover a img{
  transform:scale(1.018)!important;
  filter:saturate(.76) contrast(1.05) brightness(.98)!important;
}
.brando-new-arrivals .woocommerce ul.products li.product .woocommerce-loop-product__title{
  min-height:44px!important;
  font-weight:740!important;
  letter-spacing:-.01em!important;
}
.brando-new-arrivals .woocommerce ul.products li.product .price{
  font-size:17.5px!important;
  font-weight:880!important;
}
.brando-new-arrivals .woocommerce ul.products li.product .button,
.brando-new-arrivals .woocommerce ul.products li.product .add_to_cart_button{
  opacity:.84!important;
  transition:opacity .2s ease,background .2s ease,color .2s ease!important;
}
.brando-new-arrivals .woocommerce ul.products li.product:hover .button,
.brando-new-arrivals .woocommerce ul.products li.product:hover .add_to_cart_button{opacity:1!important}

/* Slightly stronger brand ending without changing the block structure. */
.brando-newsletter__form{width:100%!important;max-width:560px!important}
.brando-newsletter__form input{letter-spacing:0!important}
.brando-footer__brand-name{letter-spacing:-.025em!important}
.brando-footer__column a{color:#918b84!important}
.brando-footer__column a:hover{color:#d2c5b8!important}
.brando-footer__bottom,.brando-footer__bottom small,.brando-footer__bottom span{color:#5d5a56!important}
/* BRANDO ART DIRECTION LOCK v0.5.5 END */'''
css_new = css + css_finish + "\n"

# Idempotent runtime demo-image art direction. It changes homepage presentation only;
# it never writes to WooCommerce posts, attachments, product metadata, or templates.
js_pattern = re.compile(re.escape(JS_START) + r".*?" + re.escape(JS_END), re.S)
js = js_pattern.sub("", js).rstrip() + "\n\n"
js_finish = r'''/* BRANDO DEMO ART DIRECTION v0.5.5 START */
(() => {
  'use strict';

  const applyDemoArtDirection = () => {
    const root = document.querySelector('.brando-new-arrivals .woocommerce ul.products');
    if (!root) return;

    const products = Array.from(root.querySelectorAll('li.product')).slice(0, 4);
    if (products.length !== 4) return;

    const normalizedTitles = products.map((item) => {
      const title = item.querySelector('.woocommerce-loop-product__title');
      return title ? title.textContent.trim() : '';
    });

    // Demo-only guard: apply only while the known four demo product themes are present together.
    const guards = [
      (t) => /خبز|مخبوز|خبز/.test(t),
      (t) => /تقديم|بورسلين/.test(t),
      (t) => /تخزين|محكمة|تنظيم/.test(t),
      (t) => /تحضير|أدوات/.test(t),
    ];
    const allDemoThemesPresent = guards.every((guard) => normalizedTitles.some(guard));
    if (!allDemoThemesPresent) return;

    const art = [
      {
        match: /خبز|مخبوز/,
        src: 'https://images.unsplash.com/photo-1596002937504-1246a49fba48?auto=format&fit=crop&fm=jpg&q=86&w=1100',
      },
      {
        match: /تقديم|بورسلين/,
        src: 'https://images.unsplash.com/photo-1772453609632-2f4aa857f56e?auto=format&fit=crop&fm=jpg&q=86&w=1100',
      },
      {
        match: /تخزين|محكمة|تنظيم/,
        src: 'https://images.unsplash.com/photo-1676976500593-3dfec0b17754?auto=format&fit=crop&fm=jpg&q=86&w=1100',
      },
      {
        match: /تحضير|أدوات/,
        src: 'https://images.unsplash.com/photo-1698939586636-98209ecf8516?auto=format&fit=crop&fm=jpg&q=86&w=1100',
      },
    ];

    products.forEach((item) => {
      const titleEl = item.querySelector('.woocommerce-loop-product__title');
      const image = item.querySelector('img');
      if (!titleEl || !image) return;
      const rule = art.find((entry) => entry.match.test(titleEl.textContent.trim()));
      if (!rule) return;
      image.src = rule.src;
      image.removeAttribute('srcset');
      image.removeAttribute('sizes');
      image.dataset.brandoArtDirected = '055';
    });
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', applyDemoArtDirection, { once: true });
  } else {
    applyDemoArtDirection();
  }
})();
/* BRANDO DEMO ART DIRECTION v0.5.5 END */'''
js_new = js + js_finish + "\n"

write_atomic("style.css", style_new)
write_atomic("functions.php", functions_new)
write_atomic("assets/css/luxury-v3.css", css_new)
write_atomic("assets/js/luxury-motion.js", js_new)

print("PATCH_VERSION=0.5.5")
print("LAYOUT_STRUCTURE_CHANGED=NO")
print("SECTION_ORDER_CHANGED=NO")
print("TEMPLATES_CHANGED=NO")
print("WOOCOMMERCE_DATA_CHANGED=NO")
print("HERO_COMPOSITION_CHANGED=NO")
print("CATEGORIES_COMPOSITION_CHANGED=NO")
print("NEW_ARRIVALS_ART_DIRECTION_LOCK=YES")
print("DEMO_PRESENTATION_ONLY=YES")
print("BRAND_ENDING_FINISH=YES")
print("MOTION_SYSTEM_PRESERVED=YES")
