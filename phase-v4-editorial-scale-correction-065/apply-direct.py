#!/usr/bin/env python3
from pathlib import Path
import re,sys
V='0.6.5'; S='/* BRANDO EDITORIAL SCALE CORRECTION v0.6.5 START */'; E='/* BRANDO EDITORIAL SCALE CORRECTION v0.6.5 END */'
if len(sys.argv)!=2: raise SystemExit('Usage: apply-direct.py /absolute/path/to/brando')
t=Path(sys.argv[1]).resolve(); req=['style.css','functions.php','header.php','front-page.php','footer.php','assets/css/luxury-v3.css','assets/js/luxury-motion.js']
if any(not (t/x).is_file() for x in req): raise SystemExit('Missing theme files')
r=lambda x:(t/x).read_text(encoding='utf-8')
style,fn,head,front,foot,css,js=[r(x) for x in req]
if 'BRANDO GALLERY MATERIALITY v0.6.4' not in css: raise SystemExit('Expected v0.6.4 baseline not found')
if 'BRANDO CINEMATIC HERO v0.6.1' not in js or 'IntersectionObserver' not in js or 'scrollIntoView' not in js: raise SystemExit('Cinematic/motion baseline missing')
pos=[front.find(x) for x in ['class="brando-hero"','id="categories"','id="best-sellers"','class="brando-promo"','class="brando-new-arrivals"']]
if any(x<0 for x in pos) or pos!=sorted(pos): raise SystemExit('Section order check failed')
for bad in ['999 ر.س','WELCOME10','+966','brando.sa']:
    if bad in head+'\n'+front+'\n'+foot: raise SystemExit('Forbidden locale token: '+bad)
style,n=re.subn(r'(?m)^Version:\s*[^\r\n]+$',f'Version: {V}',style,count=1)
if n!=1: raise SystemExit('Version update failed')
fn,n=re.subn(r"define\('BRANDO_THEME_VERSION',\s*'[^']+'\);",f"define('BRANDO_THEME_VERSION', '{V}');",fn,count=1)
if n!=1: raise SystemExit('Theme constant update failed')
css=re.sub(re.escape(S)+r'.*?'+re.escape(E),'',css,flags=re.S).rstrip()+'\n\n'
layer=r'''/* BRANDO EDITORIAL SCALE CORRECTION v0.6.5 START */
.brando-categories__inner,.brando-best-sellers__inner,.brando-promo__inner,.brando-new-arrivals__inner{max-width:1660px!important}.brando-trust__inner,.brando-newsletter__inner,.brando-footer__inner{max-width:1540px!important}
.brando-hero__frame,.brando-hero__media.brando-cinematic-ready,.brando-hero__content{min-height:750px!important}.brando-hero-scene{filter:saturate(.56) contrast(1.14) brightness(.66)!important}.brando-hero__title{font-size:clamp(72px,6vw,102px)!important;max-width:640px!important}.brando-hero__lead{font-size:16px!important;max-width:570px!important}
.brando-categories{padding:94px 0 112px!important}.brando-categories__head{margin-bottom:48px!important}.brando-categories__title{font-size:clamp(54px,4.6vw,72px)!important}.brando-categories__grid{gap:14px!important}.brando-category-card__media{aspect-ratio:3/4.72!important;box-shadow:0 30px 82px rgba(18,14,10,.13)!important}.brando-category-card__media img{filter:saturate(.56) contrast(1.10) brightness(.82)!important}.brando-category-card__content{bottom:24px!important;inset-inline:20px!important}.brando-category-card__name{font-size:19px!important}
.brando-best-sellers{padding:104px 0 120px!important}.brando-best-sellers__head{margin-bottom:46px!important}.brando-best-sellers__title{font-size:clamp(58px,5vw,78px)!important}.brando-best-sellers__grid{gap:42px!important}.brando-product-card__media{aspect-ratio:4/5.8!important;box-shadow:0 34px 92px rgba(18,14,10,.15)!important}.brando-product-card__content{padding:24px 2px 0!important;min-height:140px!important}.brando-product-card__name{font-size:18px!important}.brando-product-card__price{font-size:22px!important}.brando-product-card__rating{display:none!important}.brando-product-card__cart,.brando-product-card .button,.brando-product-card .add_to_cart_button{opacity:.56!important}.brando-product-card:hover .brando-product-card__cart,.brando-product-card:hover .button,.brando-product-card:hover .add_to_cart_button{opacity:1!important}
.brando-promo{padding:88px 0 98px!important}.brando-promo__card,.brando-promo__visual{min-height:570px!important}.brando-promo__card{box-shadow:0 46px 120px rgba(17,12,8,.19)!important}.brando-promo__visual{filter:saturate(.50) contrast(1.12) brightness(.73)!important}.brando-promo__content{padding:84px 88px!important}.brando-promo__title{font-size:clamp(54px,4.6vw,74px)!important}.brando-promo__badge{width:62px!important;height:62px!important;opacity:.46!important}
.brando-new-arrivals{padding:98px 0 108px!important}.brando-new-arrivals__head{margin-bottom:42px!important}.brando-new-arrivals__title{font-size:clamp(48px,4.1vw,64px)!important}.brando-new-arrivals .woocommerce ul.products{gap:34px!important}.brando-new-arrivals .woocommerce ul.products li.product a img{aspect-ratio:4/5.32!important;box-shadow:0 22px 58px rgba(18,14,10,.09)!important}.brando-new-arrivals .woocommerce ul.products li.product .woocommerce-loop-product__title{font-size:16px!important}.brando-new-arrivals .woocommerce ul.products li.product .price{font-size:18.5px!important}
.brando-trust__inner{min-height:132px!important}.brando-trust__item{padding:40px 36px!important}.brando-trust__item h3{font-size:15px!important}
.brando-newsletter{padding:104px 0 0!important;background:#060707!important}.brando-newsletter__inner{padding:82px 78px 76px!important;background:radial-gradient(circle at 87% -10%,rgba(159,82,39,.14),transparent 30%),linear-gradient(135deg,#060707,#0d0e0e)!important}.brando-newsletter h2{font-size:clamp(50px,4.7vw,68px)!important;max-width:860px!important}.site-footer.brando-footer{background:radial-gradient(circle at 84% 0%,rgba(159,82,39,.065),transparent 28%),#040505!important}.brando-footer__inner{padding:82px 0 36px!important}.brando-footer__grid{gap:72px!important}.brando-footer__brand-name{font-size:52px!important}
@media(max-width:980px){.brando-hero__frame,.brando-hero__media.brando-cinematic-ready{min-height:0!important}.brando-hero__media.brando-cinematic-ready{min-height:400px!important}.brando-hero__content{min-height:0!important}.brando-newsletter__inner{padding:56px 40px!important}}
@media(max-width:720px){.brando-hero__title{font-size:50px!important}.brando-categories,.brando-best-sellers,.brando-new-arrivals{padding-block:68px!important}.brando-promo{padding-block:62px!important}}
/* BRANDO EDITORIAL SCALE CORRECTION v0.6.5 END */'''
def w(rel,text):
    p=t/rel; q=p.with_suffix(p.suffix+'.tmp-brando-065'); q.write_text(text,encoding='utf-8'); q.replace(p)
w('style.css',style); w('functions.php',fn); w('assets/css/luxury-v3.css',css+layer+'\n')
print('PATCH_VERSION=0.6.5')
print('LAYOUT_STRUCTURE_CHANGED=NO')
print('SECTION_ORDER_CHANGED=NO')
print('TEMPLATES_CHANGED=NO')
print('WOOCOMMERCE_DATA_CHANGED=NO')
print('IMAGERY_CHANGED=NO')
print('CINEMATIC_ENGINE_PRESERVED=YES')
print('EDITORIAL_SCALE_CORRECTION=YES')
print('MOTION_SYSTEM_PRESERVED=YES')
