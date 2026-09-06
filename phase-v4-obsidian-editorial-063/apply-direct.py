#!/usr/bin/env python3
from pathlib import Path
import re, sys

VERSION='0.6.3'
START='/* BRANDO OBSIDIAN EDITORIAL v0.6.3 START */'
END='/* BRANDO OBSIDIAN EDITORIAL v0.6.3 END */'

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
    t=p.with_suffix(p.suffix+'.tmp-brando-063')
    t.write_text(text,encoding='utf-8')
    t.replace(p)

style,functions,header,front,footer,css,js=[read(x) for x in required]

if 'BRANDO DARK EDITORIAL LUXURY v0.6.2' not in css:
    raise SystemExit('Expected v0.6.2 dark editorial baseline not found')
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

layer=r'''/* BRANDO OBSIDIAN EDITORIAL v0.6.3 START */
:root{
  --br-obsidian:#050606;
  --br-obsidian-soft:#0b0c0c;
  --br-bone:#f3ece2;
  --br-sand:#e6d9ca;
  --br-copper-deep:#7f3f20;
  --br-copper-soft:#b66b3d;
  --br-hairline:rgba(87,64,45,.14);
}

/* HERO — stronger dark-luxury mood while preserving the 0.6.1 runtime. */
.brando-hero{background:var(--br-obsidian)!important}
.brando-hero__frame{min-height:720px!important}
.brando-hero__media.brando-cinematic-ready{min-height:720px!important}
.brando-hero-scene{filter:saturate(.58) contrast(1.14) brightness(.68)!important}
.brando-hero-scene.scene-a{filter:saturate(.56) contrast(1.16) brightness(.66)!important}
.brando-hero-scene.scene-b{filter:saturate(.54) contrast(1.15) brightness(.63)!important}
.brando-hero-scene.scene-c{filter:saturate(.52) contrast(1.14) brightness(.64)!important}
.brando-hero-scene::before{
  background:
    radial-gradient(circle at 24% 42%,rgba(188,121,76,.06),transparent 34%),
    linear-gradient(180deg,rgba(0,0,0,.10),rgba(0,0,0,.22))!important;
  mix-blend-mode:screen!important;
}
.brando-hero-scene::after{
  background:
    linear-gradient(90deg,rgba(0,0,0,.18) 0%,rgba(0,0,0,.12) 36%,rgba(0,0,0,.44) 62%,rgba(0,0,0,.96) 100%),
    linear-gradient(180deg,rgba(0,0,0,.04),rgba(0,0,0,.28))!important;
}
.brando-hero__content{min-height:720px!important;width:min(48%,780px)!important;padding-inline:clamp(58px,5.4vw,98px)!important;background:linear-gradient(90deg,rgba(5,6,6,0),rgba(5,6,6,.16) 20%,rgba(5,6,6,.72) 66%,rgba(5,6,6,.98) 100%)!important}
.brando-hero__title{font-size:clamp(68px,5.85vw,96px)!important;letter-spacing:-.055em!important;line-height:.96!important}
.brando-hero__title strong{color:var(--br-copper-soft)!important}
.brando-hero__lead{font-size:15.5px!important;line-height:1.95!important;max-width:510px!important;color:#c8c1b8!important}
.brando-hero__cta{min-width:172px!important;min-height:50px!important;border-radius:2px!important;background:var(--br-copper-deep)!important;box-shadow:none!important}
.brando-hero__cta:hover{background:#9c542d!important;transform:translateY(-2px)!important}
.brando-hero__benefits{background:#060707!important;border-top-color:rgba(255,255,255,.05)!important}
.brando-hero__benefit{color:#8d8881!important}.brando-hero__benefit svg{stroke:#9d613c!important}

/* HEADER — more restrained luxury, less ecommerce chrome. */
.brando-header{background:rgba(4,5,5,.96)!important;border-bottom-color:rgba(182,107,61,.08)!important}
.brando-header.is-scrolled{background:rgba(4,5,5,.70)!important;backdrop-filter:blur(24px) saturate(1.14)!important;-webkit-backdrop-filter:blur(24px) saturate(1.14)!important}
.brando-brand__text strong{font-size:32px!important}.site-nav__menu>li>a{font-size:13px!important;color:#c8c3bd!important}.site-nav__menu>li>a:hover,.site-nav__menu>.current-menu-item>a{color:#fff!important}
.brando-action{border-color:rgba(255,255,255,.035)!important;background:transparent!important}

/* SECTION SIGNATURES — larger typography, more editorial spacing. */
.brando-categories__title,.brando-best-sellers__title{font-size:clamp(48px,3.95vw,62px)!important;letter-spacing:-.048em!important}
.brando-new-arrivals__title{font-size:clamp(38px,3.25vw,48px)!important;letter-spacing:-.04em!important}
.brando-categories__eyebrow,.brando-best-sellers__eyebrow,.brando-new-arrivals__eyebrow{font-size:10px!important;color:#8d512f!important;letter-spacing:.06em!important}

/* CATEGORIES — same six slots, less card UI and more collection-gallery presence. */
.brando-categories{padding:86px 0 92px!important;background:#f5efe6!important}
.brando-categories__grid{gap:24px!important}
.brando-category-card{border:0!important;border-radius:2px!important;background:#111!important;box-shadow:0 16px 46px rgba(17,13,10,.08)!important}
.brando-category-card__media{aspect-ratio:4/5.65!important}
.brando-category-card__media::after{background:linear-gradient(180deg,rgba(3,3,3,.01) 24%,rgba(3,3,3,.10) 48%,rgba(3,3,3,.92) 100%)!important}
.brando-category-card__media img{filter:saturate(.58) contrast(1.08) brightness(.84)!important}
.brando-category-card:hover .brando-category-card__media img{transform:scale(1.055)!important;filter:saturate(.64) contrast(1.09) brightness(.88)!important}
.brando-category-card__name{font-size:18px!important;font-weight:760!important}.brando-category-card__hint{opacity:.52!important}.brando-category-card__icon{width:29px!important;height:29px!important;background:rgba(5,6,6,.72)!important;border-color:rgba(182,107,61,.25)!important}

/* BEST SELLERS — image-first luxury retail; remove ratings from the visual hierarchy. */
.brando-best-sellers{padding:94px 0 102px!important;background:linear-gradient(180deg,#e9dece,#e4d7c6)!important;border-block-color:rgba(95,68,46,.10)!important}
.brando-best-sellers__grid{gap:38px!important}
.brando-product-card{background:transparent!important;border:0!important;box-shadow:none!important}
.brando-product-card__media{aspect-ratio:4/5.55!important;border-radius:2px!important;box-shadow:0 20px 56px rgba(19,14,10,.10)!important}
.brando-product-card__media img{filter:saturate(.58) contrast(1.07) brightness(.93)!important}
.brando-product-card__content{padding:22px 2px 0!important;min-height:148px!important}
.brando-product-card__name{font-size:17px!important;font-weight:700!important;line-height:1.5!important;min-height:42px!important}
.brando-product-card__rating{display:none!important}
.brando-product-card__price{margin-top:12px!important;font-size:20.5px!important;font-weight:850!important}
.brando-product-card__cart,.brando-product-card .button,.brando-product-card .add_to_cart_button{margin-top:13px!important;padding:5px 0 7px!important;border:0!important;border-bottom:1px solid rgba(20,18,15,.38)!important;background:transparent!important;color:#26221d!important;font-size:10px!important;border-radius:0!important}
.brando-product-card__cart:hover,.brando-product-card .button:hover,.brando-product-card .add_to_cart_button:hover{color:var(--br-copper-deep)!important;border-bottom-color:var(--br-copper-deep)!important;background:transparent!important}
.brando-product-card__wishlist{width:31px!important;height:31px!important;background:rgba(4,5,5,.62)!important;border-color:rgba(255,255,255,.16)!important}

/* PROMO — same split, more campaign-like and less sale-banner-like. */
.brando-promo{padding:78px 0 86px!important;background:#f7f2ea!important}
.brando-promo__card{min-height:520px!important;border-radius:3px!important;box-shadow:0 34px 92px rgba(16,12,8,.14)!important}
.brando-promo__content{flex-basis:43%!important;padding:76px 72px!important;background:radial-gradient(circle at 88% 10%,rgba(127,63,32,.11),transparent 28%),linear-gradient(145deg,#060707,#111212)!important}
.brando-promo__visual{flex-basis:57%!important;min-height:520px!important;filter:saturate(.50) contrast(1.09) brightness(.78)!important}
.brando-promo__title{font-size:clamp(48px,4.25vw,66px)!important;letter-spacing:-.05em!important}.brando-promo__title strong{color:var(--br-copper-soft)!important}.brando-promo__badge{width:72px!important;height:72px!important;opacity:.54!important}.brando-promo__cta{background:var(--br-copper-deep)!important;border-radius:2px!important;box-shadow:none!important}

/* NEW ARRIVALS — quieter editorial grid, no competing retail noise. */
.brando-new-arrivals{padding:84px 0 92px!important;background:#fbf7f1!important}
.brando-new-arrivals .woocommerce ul.products{gap:30px!important}
.brando-new-arrivals .woocommerce ul.products li.product{background:transparent!important;border:0!important;box-shadow:none!important}
.brando-new-arrivals .woocommerce ul.products li.product a img{border-radius:2px!important;filter:saturate(.54) contrast(1.06) brightness(.94)!important;box-shadow:0 14px 40px rgba(18,14,10,.07)!important}
.brando-new-arrivals .woocommerce ul.products li.product .woocommerce-loop-product__title{font-size:15.2px!important;font-weight:670!important;min-height:42px!important}.brando-new-arrivals .woocommerce ul.products li.product .price{font-size:17.5px!important;font-weight:820!important}.brando-new-arrivals .woocommerce ul.products li.product .button,.brando-new-arrivals .woocommerce ul.products li.product .add_to_cart_button{border:0!important;border-bottom:1px solid rgba(35,31,27,.34)!important;border-radius:0!important;background:transparent!important;color:#2a261f!important;padding:5px 0 7px!important}

/* TRUST + NEWSLETTER + FOOTER — one continuous dark brand world. */
.brando-trust{background:#e9dfd2!important;border-color:#d9ccbc!important}.brando-trust__inner{min-height:112px!important}.brando-trust__item h3{font-size:14px!important}.brando-trust__item p{color:#82786f!important}
.brando-newsletter{padding:86px 0 0!important;background:linear-gradient(180deg,#e9dfd2 0%,#e9dfd2 48%,#050606 48%,#050606 100%)!important}
.brando-newsletter__inner{padding:68px 72px!important;border-radius:3px!important;background:radial-gradient(circle at 88% 8%,rgba(127,63,32,.10),transparent 25%),linear-gradient(135deg,#060707,#101111)!important;box-shadow:0 30px 86px rgba(0,0,0,.20)!important}
.brando-newsletter h2{font-size:clamp(42px,4vw,58px)!important;letter-spacing:-.05em!important}.brando-newsletter p{color:#9f9890!important}.brando-newsletter__form{border-bottom-color:rgba(255,255,255,.18)!important}.brando-newsletter__form button{background:var(--br-copper-deep)!important}
.site-footer.brando-footer{background:radial-gradient(circle at 86% 4%,rgba(127,63,32,.055),transparent 24%),#050606!important}.brando-footer__inner{padding-top:112px!important}.brando-footer__brand-name{font-size:48px!important;color:var(--br-copper-soft)!important}.brando-footer__brand p{color:#7f7972!important}.brando-footer__column h3{color:#ece6df!important}.brando-footer__column a{color:#85807a!important}.brando-footer__column a:hover{color:#d7cabd!important}

@media(max-width:980px){
  .brando-hero__frame,.brando-hero__media.brando-cinematic-ready{min-height:0!important}
  .brando-hero__content{width:100%!important;min-height:0!important}
  .brando-promo__content,.brando-promo__visual{flex-basis:auto!important}
}
@media(max-width:720px){
  .brando-hero__title{font-size:50px!important}
  .brando-categories__grid{gap:14px!important}
  .brando-best-sellers__grid{gap:22px!important}
  .brando-newsletter__inner{padding:38px 24px!important}
}
/* BRANDO OBSIDIAN EDITORIAL v0.6.3 END */'''

write_atomic('style.css',style_new)
write_atomic('functions.php',functions_new)
write_atomic('assets/css/luxury-v3.css',css+layer+'\n')

print('PATCH_VERSION=0.6.3')
print('LAYOUT_STRUCTURE_CHANGED=NO')
print('SECTION_ORDER_CHANGED=NO')
print('TEMPLATES_CHANGED=NO')
print('WOOCOMMERCE_DATA_CHANGED=NO')
print('IMAGERY_CHANGED=NO')
print('CINEMATIC_ENGINE_PRESERVED=YES')
print('OBSIDIAN_HERO_GRADING=YES')
print('CATEGORY_GALLERY_FINISH=YES')
print('BEST_SELLERS_IMAGE_FIRST=YES')
print('PRODUCT_RATINGS_VISUALLY_REMOVED=YES')
print('PROMO_CAMPAIGN_FINISH=YES')
print('NEW_ARRIVALS_EDITORIAL_FINISH=YES')
print('DARK_BRAND_WORLD_ENDING=YES')
