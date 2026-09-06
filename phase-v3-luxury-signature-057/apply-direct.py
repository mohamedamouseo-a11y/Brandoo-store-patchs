#!/usr/bin/env python3
from pathlib import Path
import re, sys

VERSION='0.5.7'
START='/* BRANDO LUXURY SIGNATURE v0.5.7 START */'
END='/* BRANDO LUXURY SIGNATURE v0.5.7 END */'

if len(sys.argv)!=2: raise SystemExit('Usage: apply-direct.py /absolute/path/to/brando')
theme=Path(sys.argv[1]).resolve()
required=['style.css','functions.php','header.php','front-page.php','footer.php','assets/css/luxury-v3.css','assets/js/luxury-motion.js']
missing=[x for x in required if not (theme/x).is_file()]
if missing: raise SystemExit('Missing theme files: '+', '.join(missing))

def read(rel): return (theme/rel).read_text(encoding='utf-8')
def write(rel,text):
    p=theme/rel; t=p.with_suffix(p.suffix+'.tmp-brando-057'); t.write_text(text,encoding='utf-8'); t.replace(p)

style,functions,header,front,footer,css,js=[read(x) for x in required]
if 'BRANDO LUXURY PRESENCE v0.5.6' not in css: raise SystemExit('Expected v0.5.6 baseline not found')
if 'BRANDO DEMO ART DIRECTION v0.5.5' not in js: raise SystemExit('Expected v0.5.5 art direction not found')
markers=['class="brando-hero"','id="categories"','id="best-sellers"','class="brando-promo"','class="brando-new-arrivals"']
pos=[front.find(x) for x in markers]
if any(x<0 for x in pos) or pos!=sorted(pos): raise SystemExit('Homepage structure/order check failed')
if any(x not in footer for x in ['brando-trust','brando-newsletter','brando-footer']): raise SystemExit('Footer structure check failed')
for bad in ['999 ر.س','WELCOME10','+966','brando.sa']:
    if bad in header+'\n'+front+'\n'+footer: raise SystemExit('Forbidden locale token returned: '+bad)
if 'IntersectionObserver' not in js or 'scrollIntoView' not in js: raise SystemExit('Motion system incomplete')

style_new,n=re.subn(r'(?m)^Version:\s*[^\r\n]+$',f'Version: {VERSION}',style,count=1)
if n!=1: raise SystemExit('Could not update style version')
functions_new,n=re.subn(r"define\('BRANDO_THEME_VERSION',\s*'[^']+'\);",f"define('BRANDO_THEME_VERSION', '{VERSION}');",functions,count=1)
if n!=1: raise SystemExit('Could not update theme constant')
css=re.sub(re.escape(START)+r'.*?'+re.escape(END),'',css,flags=re.S).rstrip()+'\n\n'

layer=r'''/* BRANDO LUXURY SIGNATURE v0.5.7 START */
:root{--br-sig-copper:#92502a;--br-sig-copper-soft:#b77043;--br-sig-line:rgba(79,58,40,.13)}
.brando-categories__eyebrow,.brando-best-sellers__eyebrow,.brando-new-arrivals__eyebrow{display:inline-flex!important;align-items:center!important;gap:9px!important;color:var(--br-sig-copper)!important}
.brando-categories__eyebrow::before,.brando-best-sellers__eyebrow::before,.brando-new-arrivals__eyebrow::before{content:"";width:30px;height:1px;background:var(--br-sig-copper);opacity:.7}
.brando-header{border-bottom:1px solid rgba(183,112,67,.10)!important}.site-nav__menu>li>a::after{height:1px!important;background:var(--br-sig-copper-soft)!important}
.brando-category-card__media::after{background:linear-gradient(180deg,transparent 28%,rgba(5,5,5,.10) 50%,rgba(5,5,5,.90) 100%)!important}.brando-category-card__icon{background:rgba(8,8,7,.78)!important;border-color:rgba(183,112,67,.38)!important}
.brando-product-card{background:#f7f1e8!important;border:1px solid rgba(74,54,37,.07)!important}.brando-product-card__content{background:linear-gradient(180deg,#faf6f0,#f5eee4)!important}.brando-product-card__rating{opacity:.3!important}.brando-product-card__cart,.brando-product-card .button,.brando-product-card .add_to_cart_button{background:rgba(255,255,255,.32)!important;color:#1a1916!important;border-color:rgba(20,18,15,.6)!important}.brando-product-card__cart:hover,.brando-product-card .button:hover,.brando-product-card .add_to_cart_button:hover{background:#11110f!important;color:#fff!important}
.brando-promo__content{position:relative!important}.brando-promo__content::before{content:"";position:absolute;top:42px;inset-inline-start:70px;width:46px;height:1px;background:linear-gradient(90deg,var(--br-sig-copper-soft),transparent)}
.brando-new-arrivals .woocommerce ul.products li.product{background:#fffdfa!important;border:1px solid rgba(69,52,37,.065)!important}.brando-new-arrivals .woocommerce ul.products li.product .button,.brando-new-arrivals .woocommerce ul.products li.product .add_to_cart_button{background:transparent!important;color:#24211d!important;border-color:rgba(35,31,27,.55)!important}
.brando-trust__icon{border:0!important;background:transparent!important}.brando-trust__icon svg{stroke-width:1.55!important}.brando-trust__item:not(:last-child)::after{background:linear-gradient(180deg,transparent,var(--br-sig-line),transparent)!important}
.brando-newsletter__inner{overflow:hidden!important}.brando-newsletter__inner::after{content:"براندو";position:absolute;inset-inline-end:38px;bottom:-28px;font-size:104px;font-weight:900;letter-spacing:-.06em;color:rgba(255,255,255,.018);pointer-events:none}.brando-newsletter h2{letter-spacing:-.045em!important}.brando-newsletter__form button{background:var(--br-sig-copper)!important}
.brando-footer__brand-name{color:var(--br-sig-copper-soft)!important}.brando-footer__column h3{color:#f1ece6!important}.brando-footer__social a{border-color:#24221f!important;background:#0c0c0b!important}
@media(max-width:720px){.brando-categories__eyebrow::before,.brando-best-sellers__eyebrow::before,.brando-new-arrivals__eyebrow::before{width:20px}.brando-newsletter__inner::after{font-size:58px;bottom:-8px}.brando-promo__content::before{display:none}}
/* BRANDO LUXURY SIGNATURE v0.5.7 END */'''

write('style.css',style_new); write('functions.php',functions_new); write('assets/css/luxury-v3.css',css+layer+'\n')
print('PATCH_VERSION=0.5.7')
print('LAYOUT_STRUCTURE_CHANGED=NO')
print('SECTION_ORDER_CHANGED=NO')
print('TEMPLATES_CHANGED=NO')
print('WOOCOMMERCE_DATA_CHANGED=NO')
print('IMAGERY_CHANGED=NO')
print('DEMO_ART_DIRECTION_PRESERVED=YES')
print('HERO_COMPOSITION_CHANGED=NO')
print('CATEGORIES_COMPOSITION_CHANGED=NO')
print('LUXURY_SIGNATURE_PASS=YES')
print('MOTION_SYSTEM_PRESERVED=YES')
