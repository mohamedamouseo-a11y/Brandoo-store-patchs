#!/usr/bin/env python3
from pathlib import Path
import re, sys

VERSION='0.6.2'
START='/* BRANDO DARK EDITORIAL LUXURY v0.6.2 START */'
END='/* BRANDO DARK EDITORIAL LUXURY v0.6.2 END */'

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
    t=p.with_suffix(p.suffix+'.tmp-brando-062')
    t.write_text(text,encoding='utf-8')
    t.replace(p)

style,functions,header,front,footer,css,js=[read(x) for x in required]

if 'BRANDO CINEMATIC ART DIRECTION v0.6.1' not in css:
    raise SystemExit('Expected v0.6.1 cinematic art-direction baseline not found')
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

layer=r'''/* BRANDO DARK EDITORIAL LUXURY v0.6.2 START */
:root{
  --br-062-ink:#070706;
  --br-062-copper:#8c4924;
  --br-062-copper-soft:#b36d43;
  --br-062-paper:#f6f0e7;
  --br-062-beige:#e8ddd0;
  --br-062-line:rgba(80,58,40,.14);
}

/* HERO — same cinematic engine, darker editorial art direction. */
.brando-hero__frame{min-height:740px!important;background:#050505!important}
.brando-hero__media.brando-cinematic-ready{min-height:740px!important}
.brando-hero-scene{filter:saturate(.62) contrast(1.12) brightness(.68)!important}
.brando-hero-scene.scene-a{filter:saturate(.58) contrast(1.13) brightness(.67)!important}
.brando-hero-scene.scene-b{filter:saturate(.60) contrast(1.12) brightness(.66)!important}
.brando-hero-scene.scene-c{filter:saturate(.56) contrast(1.11) brightness(.67)!important}
.brando-hero-scene::before{background:radial-gradient(circle at 35% 48%,transparent 0%,rgba(0,0,0,.08) 42%,rgba(0,0,0,.36) 100%),linear-gradient(120deg,rgba(123,63,31,.05),transparent 34%,rgba(0,0,0,.14))!important}
.brando-hero-scene::after{background:linear-gradient(90deg,rgba(0,0,0,.03) 0%,rgba(0,0,0,.12) 40%,rgba(0,0,0,.58) 68%,rgba(0,0,0,.96) 100%),linear-gradient(180deg,rgba(0,0,0,.08),rgba(0,0,0,.28))!important}
.brando-hero__content{min-height:740px!important;width:min(48%,780px)!important;padding-inline:clamp(58px,5.5vw,104px)!important;background:linear-gradient(90deg,rgba(4,4,4,0),rgba(4,4,4,.16) 26%,rgba(4,4,4,.72) 72%,rgba(4,4,4,.97) 100%)!important}
.brando-hero__content::before{inset-block:104px!important;background:linear-gradient(180deg,transparent,rgba(179,109,67,.84),transparent)!important}
.brando-hero__title{font-size:clamp(70px,6vw,98px)!important;line-height:.94!important;letter-spacing:-.055em!important;text-wrap:balance}
.brando-hero__title strong{color:var(--br-062-copper-soft)!important}
.brando-hero__lead{max-width:540px!important;font-size:16.5px!important;line-height:2!important;color:#d0cac4!important}
.brando-hero__cta{min-width:172px!important;min-height:52px!important;border-radius:3px!important;background:var(--br-062-copper)!important;box-shadow:0 20px 50px rgba(140,73,36,.26)!important}
.brando-hero__benefits{background:#060707!important;border-top-color:rgba(255,255,255,.05)!important}
.brando-hero__benefit{color:#96918c!important}
.brando-hero__dots span{height:6px!important}
.brando-hero__dots span.is-active{width:40px!important;background:var(--br-062-copper-soft)!important}

/* HEADER — visually connected to hero. */
.brando-header{background:rgba(5,6,6,.97)!important;border-bottom-color:rgba(179,109,67,.08)!important}
.brando-header.is-scrolled{background:rgba(5,6,6,.76)!important;backdrop-filter:blur(24px) saturate(1.2)!important;-webkit-backdrop-filter:blur(24px) saturate(1.2)!important;box-shadow:0 20px 58px rgba(0,0,0,.30)!important}
.brando-brand__text strong{font-size:32px!important}
.site-nav__menu>li>a{color:#c8c3bd!important}
.site-nav__menu>li>a:hover,.site-nav__menu>.current-menu-item>a{color:#fff!important}

/* CATEGORIES — same six items, closer to an editorial collection strip. */
.brando-categories{padding:88px 0 92px!important;background:var(--br-062-paper)!important}
.brando-categories__head{margin-bottom:38px!important}
.brando-categories__title{font-size:clamp(48px,4vw,62px)!important}
.brando-categories__grid{gap:16px!important}
.brando-category-card{border:0!important;border-radius:2px!important;box-shadow:0 22px 60px rgba(18,14,10,.09)!important}
.brando-category-card__media{aspect-ratio:4/5.45!important}
.brando-category-card__media::after{background:linear-gradient(180deg,rgba(0,0,0,.00) 28%,rgba(0,0,0,.14) 54%,rgba(0,0,0,.94) 100%)!important}
.brando-category-card__content{bottom:20px!important;inset-inline:20px!important}
.brando-category-card__name{font-size:18px!important;font-weight:780!important}
.brando-category-card__hint{opacity:.58!important}
.brando-category-card__icon{width:30px!important;height:30px!important;opacity:.52!important;background:rgba(6,6,6,.72)!important;border-color:rgba(255,255,255,.16)!important}
.brando-category-card:hover .brando-category-card__icon{opacity:1!important}

/* BEST SELLERS — editorial luxury, image-first. */
.brando-best-sellers{padding:96px 0 102px!important;background:linear-gradient(180deg,#ede3d7,#e5d8c9)!important}
.brando-best-sellers__title{font-size:clamp(48px,4vw,62px)!important}
.brando-best-sellers__grid{gap:36px!important}
.brando-product-card__media{aspect-ratio:4/5.6!important;border-radius:2px!important;box-shadow:0 24px 62px rgba(16,12,9,.11)!important}
.brando-product-card__media img{filter:saturate(.64) contrast(1.06) brightness(.95)!important}
.brando-product-card__content{padding:21px 2px 0!important;min-height:154px!important}
.brando-product-card__name{font-size:17.5px!important;line-height:1.45!important;font-weight:760!important}
.brando-product-card__price{font-size:21px!important;font-weight:900!important}
.brando-product-card__cart,.brando-product-card .button,.brando-product-card .add_to_cart_button{font-size:10px!important;color:#27231f!important;border-bottom-color:rgba(39,35,31,.38)!important}

/* PROMO — more campaign, less sale banner. */
.brando-promo{padding:74px 0 84px!important;background:#faf6f0!important}
.brando-promo__card{min-height:520px!important;border-radius:2px!important;box-shadow:0 40px 110px rgba(18,14,10,.15)!important}
.brando-promo__content{padding:80px 78px!important;background:radial-gradient(circle at 90% 12%,rgba(140,73,36,.11),transparent 28%),linear-gradient(145deg,#050606,#101111)!important}
.brando-promo__visual{min-height:520px!important;filter:saturate(.58) contrast(1.08) brightness(.82)!important}
.brando-promo__title{font-size:clamp(50px,4.5vw,70px)!important;line-height:1.02!important}
.brando-promo__text{color:#aaa39c!important}
.brando-promo__badge{opacity:.58!important;transform:scale(.84)!important}
.brando-promo__cta{background:var(--br-062-copper)!important;border-radius:2px!important}

/* NEW ARRIVALS — lighter editorial contrast to Best Sellers. */
.brando-new-arrivals{padding:82px 0 90px!important;background:#fffdf9!important}
.brando-new-arrivals__title{font-size:clamp(40px,3.5vw,50px)!important}
.brando-new-arrivals .woocommerce ul.products{gap:28px!important}
.brando-new-arrivals .woocommerce ul.products li.product a img{border-radius:1px!important;box-shadow:0 16px 42px rgba(17,13,10,.07)!important;filter:saturate(.62) contrast(1.04) brightness(.97)!important}
.brando-new-arrivals .woocommerce ul.products li.product .woocommerce-loop-product__title{font-size:15.6px!important;font-weight:720!important}
.brando-new-arrivals .woocommerce ul.products li.product .price{font-size:18.2px!important;font-weight:870!important}

/* TRUST / NEWSLETTER / FOOTER — quieter and heavier. */
.brando-trust{background:#ece4d9!important;border-color:#dbd0c2!important}
.brando-trust__inner{min-height:122px!important}
.brando-trust__item{padding-block:38px!important}
.brando-trust__item h3{font-size:14.6px!important}
.brando-trust__item p{color:#7c746b!important}
.brando-newsletter{background:#e7ddd1!important;padding-top:82px!important}
.brando-newsletter__inner{padding:66px 70px!important;border-radius:2px!important;background:radial-gradient(circle at 86% 6%,rgba(140,73,36,.10),transparent 24%),linear-gradient(135deg,#050606,#0e0f0f)!important;box-shadow:0 30px 84px rgba(0,0,0,.16)!important}
.brando-newsletter h2{font-size:clamp(42px,4.2vw,58px)!important;line-height:1.03!important}
.brando-newsletter__form{border-bottom-color:rgba(255,255,255,.28)!important}
.brando-newsletter__form button{background:var(--br-062-copper)!important}
.brando-footer__inner{padding-top:112px!important}
.brando-footer__brand-name{font-size:48px!important;color:var(--br-062-copper-soft)!important}
.brando-footer__brand p{color:#8d8780!important}
.brando-footer__column a{color:#8b8580!important}
.brando-footer__column a:hover{color:#d9cec3!important}

@media(max-width:980px){
  .brando-hero__frame,.brando-hero__media.brando-cinematic-ready{min-height:0!important}
  .brando-hero__media.brando-cinematic-ready{min-height:400px!important}
  .brando-hero__content{width:100%!important;min-height:0!important;padding:46px 30px 52px!important;background:#050606!important}
  .brando-hero__title{font-size:clamp(50px,9vw,70px)!important}
}
@media(max-width:720px){
  .brando-hero__media.brando-cinematic-ready{min-height:320px!important}
  .brando-categories,.brando-best-sellers,.brando-new-arrivals{padding-block:62px!important}
  .brando-promo{padding-block:58px!important}
  .brando-newsletter__inner{padding:38px 26px!important}
}
/* BRANDO DARK EDITORIAL LUXURY v0.6.2 END */'''

write_atomic('style.css',style_new)
write_atomic('functions.php',functions_new)
write_atomic('assets/css/luxury-v3.css',css+layer+'\n')

print('PATCH_VERSION=0.6.2')
print('LAYOUT_STRUCTURE_CHANGED=NO')
print('SECTION_ORDER_CHANGED=NO')
print('TEMPLATES_CHANGED=NO')
print('WOOCOMMERCE_DATA_CHANGED=NO')
print('IMAGERY_CHANGED=NO')
print('CINEMATIC_ENGINE_PRESERVED=YES')
print('DARK_EDITORIAL_HERO=YES')
print('CATEGORY_EDITORIAL_FINISH=YES')
print('BEST_SELLERS_EDITORIAL_FINISH=YES')
print('PROMO_CAMPAIGN_FINISH=YES')
print('NEW_ARRIVALS_EDITORIAL_FINISH=YES')
print('DARK_ENDING_FINISH=YES')