#!/usr/bin/env python3
from pathlib import Path
import re, sys

VERSION='0.6.4'
START='/* BRANDO GALLERY MATERIALITY v0.6.4 START */'
END='/* BRANDO GALLERY MATERIALITY v0.6.4 END */'

if len(sys.argv)!=2:
    raise SystemExit('Usage: apply-direct.py /absolute/path/to/brando')

theme=Path(sys.argv[1]).resolve()
required=['style.css','functions.php','header.php','front-page.php','footer.php','assets/css/luxury-v3.css','assets/js/luxury-motion.js']
missing=[x for x in required if not (theme/x).is_file()]
if missing:
    raise SystemExit('Missing theme files: '+', '.join(missing))

def read(rel): return (theme/rel).read_text(encoding='utf-8')
def write_atomic(rel,text):
    p=theme/rel
    t=p.with_suffix(p.suffix+'.tmp-brando-064')
    t.write_text(text,encoding='utf-8')
    t.replace(p)

style,functions,header,front,footer,css,js=[read(x) for x in required]

if 'BRANDO OBSIDIAN EDITORIAL v0.6.3' not in css:
    raise SystemExit('Expected v0.6.3 obsidian baseline not found')
if 'BRANDO CINEMATIC HERO v0.6.1' not in js:
    raise SystemExit('Expected v0.6.1 cinematic runtime not found')
if 'IntersectionObserver' not in js or 'scrollIntoView' not in js:
    raise SystemExit('Existing motion system is incomplete')

markers=['class="brando-hero"','id="categories"','id="best-sellers"','class="brando-promo"','class="brando-new-arrivals"']
pos=[front.find(x) for x in markers]
if any(x<0 for x in pos) or pos!=sorted(pos):
    raise SystemExit('Homepage structure/order check failed')
if any(x not in footer for x in ['brando-trust','brando-newsletter','brando-footer']):
    raise SystemExit('Footer structure check failed')
for bad in ['999 ر.س','WELCOME10','+966','brando.sa']:
    if bad in header+'\n'+front+'\n'+footer:
        raise SystemExit('Forbidden locale token returned: '+bad)

style_new,n=re.subn(r'(?m)^Version:\s*[^\r\n]+$',f'Version: {VERSION}',style,count=1)
if n!=1: raise SystemExit('Could not update style version')
functions_new,n=re.subn(r"define\('BRANDO_THEME_VERSION',\s*'[^']+'\);",f"define('BRANDO_THEME_VERSION', '{VERSION}');",functions,count=1)
if n!=1: raise SystemExit('Could not update theme constant')

css=re.sub(re.escape(START)+r'.*?'+re.escape(END),'',css,flags=re.S).rstrip()+'\n\n'

layer=r'''/* BRANDO GALLERY MATERIALITY v0.6.4 START */
:root{
  --br-064-ink:#080907;
  --br-064-copper:#9b542d;
  --br-064-copper-soft:#c17a4d;
  --br-064-ivory:#f4eee5;
  --br-064-sand:#dfd2c2;
  --br-064-line:rgba(91,67,47,.14);
}

/* Wider editorial canvas without changing section structure. */
.brando-categories__inner,
.brando-best-sellers__inner,
.brando-promo__inner,
.brando-new-arrivals__inner{max-width:1540px!important}
.brando-newsletter__inner,.brando-footer__inner{max-width:1480px!important}

/* HERO — same engine/scenes, stronger cinematic materiality. */
.brando-hero__frame{min-height:740px!important;background:#050606!important}
.brando-hero__media.brando-cinematic-ready{min-height:740px!important}
.brando-hero__content{min-height:740px!important;padding-inline:clamp(36px,6vw,110px)!important}
.brando-hero-scene{filter:saturate(.58) contrast(1.13) brightness(.68)!important}
.brando-hero-scene::after{
  background:
    radial-gradient(circle at 18% 40%,rgba(0,0,0,.02),rgba(0,0,0,.34) 74%),
    linear-gradient(90deg,rgba(3,3,3,.02) 0%,rgba(3,3,3,.10) 34%,rgba(3,3,3,.52) 67%,rgba(3,3,3,.95) 100%),
    linear-gradient(180deg,rgba(0,0,0,.05),rgba(0,0,0,.28))!important;
}
.brando-hero__title{font-size:clamp(70px,6.2vw,104px)!important;line-height:.94!important;letter-spacing:-.055em!important;max-width:620px!important}
.brando-hero__lead{font-size:15.5px!important;line-height:1.9!important;max-width:560px!important;color:#c9c2ba!important}
.brando-hero__cta{min-height:50px!important;padding:13px 26px!important;background:var(--br-064-copper)!important;border:1px solid rgba(255,255,255,.09)!important;box-shadow:0 22px 54px rgba(90,42,18,.26)!important}
.brando-hero__dots{bottom:24px!important}

/* CATEGORY GALLERY — same 6 columns, more image and less card UI. */
.brando-categories{padding:92px 0 100px!important;background:linear-gradient(180deg,#f7f1e9 0%,#f1e8dd 100%)!important}
.brando-categories__head{margin-bottom:42px!important}
.brando-categories__title{font-size:clamp(50px,4.3vw,66px)!important;letter-spacing:-.045em!important}
.brando-categories__grid{gap:16px!important}
.brando-category-card{border-radius:2px!important;box-shadow:none!important;background:transparent!important}
.brando-category-card__media{aspect-ratio:3/4.15!important;box-shadow:0 24px 62px rgba(18,14,10,.10)!important}
.brando-category-card__media img{filter:saturate(.58) contrast(1.08) brightness(.84)!important}
.brando-category-card:hover .brando-category-card__media img{transform:scale(1.085)!important}
.brando-category-card__content{inset-inline:18px!important;bottom:20px!important}
.brando-category-card__name{font-size:18px!important;font-weight:780!important}
.brando-category-card__hint{opacity:.48!important}
.brando-category-card__icon{width:28px!important;height:28px!important;background:rgba(8,8,7,.52)!important;border:1px solid rgba(255,255,255,.16)!important;backdrop-filter:blur(8px)}

/* BEST SELLERS — larger image-first showcase, cleaner commerce. */
.brando-best-sellers{padding:96px 0 108px!important;background:linear-gradient(180deg,#e8ddcf 0%,#dfd1c0 100%)!important}
.brando-best-sellers__title{font-size:clamp(54px,4.7vw,72px)!important;letter-spacing:-.05em!important}
.brando-best-sellers__grid{gap:38px!important}
.brando-product-card__media{aspect-ratio:4/5.55!important;border-radius:2px!important;box-shadow:0 28px 74px rgba(18,14,10,.13)!important}
.brando-product-card__media img{filter:saturate(.62) contrast(1.08) brightness(.90)!important}
.brando-product-card__content{padding:22px 2px 0!important;min-height:148px!important}
.brando-product-card__name{font-size:17.5px!important;font-weight:740!important;line-height:1.5!important}
.brando-product-card__price{font-size:21px!important;font-weight:900!important}
.brando-product-card__rating{display:none!important}
.brando-product-card__wishlist{width:32px!important;height:32px!important;top:12px!important;left:12px!important}
.brando-product-card__cart,.brando-product-card .button,.brando-product-card .add_to_cart_button{font-size:10.5px!important;opacity:.72!important;transition:opacity .25s ease,color .25s ease,border-color .25s ease!important}
.brando-product-card:hover .brando-product-card__cart,.brando-product-card:hover .button,.brando-product-card:hover .add_to_cart_button{opacity:1!important}

/* PROMO — same split, bolder material campaign. */
.brando-promo{padding:82px 0 90px!important;background:#f6f0e8!important}
.brando-promo__card{min-height:540px!important;border-radius:3px!important;box-shadow:0 42px 110px rgba(17,12,8,.18)!important}
.brando-promo__visual{min-height:540px!important;filter:saturate(.54) contrast(1.10) brightness(.78)!important}
.brando-promo__content{padding:78px 82px!important;background:radial-gradient(circle at 86% 10%,rgba(155,84,45,.12),transparent 24%),linear-gradient(145deg,#050606,#101111)!important}
.brando-promo__title{font-size:clamp(50px,4.4vw,70px)!important;line-height:1.02!important;letter-spacing:-.045em!important}
.brando-promo__text{font-size:14.5px!important;line-height:1.95!important;color:#99928a!important}
.brando-promo__badge{width:74px!important;height:74px!important;opacity:.62!important;background:rgba(155,84,45,.72)!important}

/* NEW ARRIVALS — editorial grid with quieter retail chrome. */
.brando-new-arrivals{padding:92px 0 98px!important;background:#faf7f2!important}
.brando-new-arrivals__title{font-size:clamp(44px,3.8vw,58px)!important;letter-spacing:-.04em!important}
.brando-new-arrivals .woocommerce ul.products{gap:30px!important}
.brando-new-arrivals .woocommerce ul.products li.product a img{aspect-ratio:4/5.05!important;filter:saturate(.58) contrast(1.05) brightness(.94)!important;box-shadow:0 18px 48px rgba(18,14,10,.08)!important}
.brando-new-arrivals .woocommerce ul.products li.product .woocommerce-loop-product__title{font-size:15.7px!important;font-weight:720!important;min-height:44px!important}
.brando-new-arrivals .woocommerce ul.products li.product .price{font-size:18px!important;font-weight:860!important}
.brando-new-arrivals .woocommerce ul.products li.product .button,.brando-new-arrivals .woocommerce ul.products li.product .add_to_cart_button{opacity:.64!important}
.brando-new-arrivals .woocommerce ul.products li.product:hover .button,.brando-new-arrivals .woocommerce ul.products li.product:hover .add_to_cart_button{opacity:1!important}

/* TRUST — premium separator strip, no card feeling. */
.brando-trust{background:linear-gradient(180deg,#e7ddcf,#ded2c2)!important;border-block:1px solid rgba(82,61,43,.11)!important}
.brando-trust__inner{min-height:122px!important}
.brando-trust__item{padding:36px 34px!important}
.brando-trust__icon{color:var(--br-064-copper)!important}
.brando-trust__item h3{font-size:14.5px!important;font-weight:790!important}
.brando-trust__item p{color:#81766a!important}

/* NEWSLETTER + FOOTER — one continuous dark brand world. */
.brando-newsletter{padding:92px 0 0!important;background:#080909!important}
.brando-newsletter__inner{margin-bottom:0!important;padding:72px 74px 66px!important;border:0!important;border-radius:0!important;box-shadow:none!important;transform:none!important;background:radial-gradient(circle at 86% 0%,rgba(155,84,45,.11),transparent 28%),linear-gradient(135deg,#080909,#0e0f0f)!important}
.brando-newsletter h2{font-size:clamp(44px,4.4vw,62px)!important;max-width:800px!important}
.brando-newsletter p{color:#918a82!important;font-size:14px!important}
.brando-newsletter__form{max-width:610px!important}
.site-footer.brando-footer{margin-top:0!important;background:radial-gradient(circle at 82% 0%,rgba(155,84,45,.055),transparent 24%),#050606!important}
.brando-footer__inner{padding:74px 0 34px!important;border-top:1px solid rgba(255,255,255,.055)!important}
.brando-footer__brand-name{font-size:48px!important;letter-spacing:-.04em!important}
.brando-footer__brand p{color:#7e7871!important}
.brando-footer__column h3{font-size:13px!important}
.brando-footer__column a{font-size:12.8px!important;color:#8c8781!important}

@media(max-width:980px){
  .brando-hero__frame,.brando-hero__media.brando-cinematic-ready{min-height:0!important}
  .brando-hero__media.brando-cinematic-ready{min-height:390px!important}
  .brando-hero__content{min-height:0!important}
  .brando-categories__grid{gap:14px!important}
  .brando-best-sellers__grid{gap:22px!important}
  .brando-newsletter__inner{padding:52px 38px!important}
}
@media(max-width:720px){
  .brando-hero__title{font-size:50px!important}
  .brando-categories{padding-block:64px!important}
  .brando-best-sellers{padding-block:68px!important}
  .brando-promo{padding-block:58px!important}
  .brando-new-arrivals{padding-block:64px!important}
  .brando-newsletter{padding-top:62px!important}
  .brando-footer__inner{padding-top:58px!important}
}
/* BRANDO GALLERY MATERIALITY v0.6.4 END */'''

write_atomic('style.css',style_new)
write_atomic('functions.php',functions_new)
write_atomic('assets/css/luxury-v3.css',css+layer+'\n')

print('PATCH_VERSION=0.6.4')
print('LAYOUT_STRUCTURE_CHANGED=NO')
print('SECTION_ORDER_CHANGED=NO')
print('TEMPLATES_CHANGED=NO')
print('WOOCOMMERCE_DATA_CHANGED=NO')
print('IMAGERY_CHANGED=NO')
print('CINEMATIC_ENGINE_PRESERVED=YES')
print('GALLERY_SCALE_PASS=YES')
print('MATERIALITY_PASS=YES')
print('DARK_BRAND_WORLD_ENDING=YES')
print('MOTION_SYSTEM_PRESERVED=YES')
