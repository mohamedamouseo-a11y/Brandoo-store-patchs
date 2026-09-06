#!/usr/bin/env python3
from pathlib import Path
import re,sys

V='0.7.4'
S='/* BRANDO PREMIUM FIDELITY POLISH v0.7.4 START */'
E='/* BRANDO PREMIUM FIDELITY POLISH v0.7.4 END */'
JS_START='/* BRANDO CINEMATIC HERO v0.6.1 START */'
JS_END='/* BRANDO CINEMATIC HERO v0.6.1 END */'

if len(sys.argv)!=2:
    raise SystemExit('Usage: apply-direct.py /absolute/path/to/brando')

t=Path(sys.argv[1]).resolve()
req=['style.css','functions.php','header.php','front-page.php','footer.php','assets/css/luxury-v3.css','assets/js/luxury-motion.js']
missing=[x for x in req if not (t/x).is_file()]
if missing: raise SystemExit('Missing theme files: '+', '.join(missing))

r=lambda x:(t/x).read_text(encoding='utf-8')
style,fn,head,front,foot,css,js=[r(x) for x in req]
if 'BRANDO REFERENCE PREMIUM PROPORTION v0.7.3 START' not in css:
    raise SystemExit('Expected v0.7.3 baseline not found')
if JS_START not in js:
    raise SystemExit('Expected cinematic runtime not found')
for token in ['ref-topbar','ref-header','ref-hero','ref-category-grid','ref-product-grid','ref-promo','ref-trust','ref-newsletter','ref-footer']:
    if token not in head+'\n'+front+'\n'+foot+'\n'+css:
        raise SystemExit('Reference structure missing: '+token)

style,n=re.subn(r'(?m)^Version:\s*[^\r\n]+$',f'Version: {V}',style,count=1)
if n!=1: raise SystemExit('Version update failed')
fn,n=re.subn(r"define\('BRANDO_THEME_VERSION',\s*'[^']+'\);",f"define('BRANDO_THEME_VERSION', '{V}');",fn,count=1)
if n!=1: raise SystemExit('Theme version update failed')
css=re.sub(re.escape(S)+r'.*?'+re.escape(E),'',css,flags=re.S).rstrip()+'\n\n'

# Keep the 0.7.3 cinematic structure, but make the first visible scene dark/warm and reference-faithful.
m=re.search(re.escape(JS_START)+r'.*?'+re.escape(JS_END),js,flags=re.S)
if not m: raise SystemExit('Cinematic block missing')
block=m.group(0)
urls=[
 'https://images.unsplash.com/photo-1765766601532-90e9b96320c8?auto=format&fit=crop&fm=jpg&q=90&w=2200',
 'https://images.unsplash.com/photo-1769326541248-5e09a8ace25b?auto=format&fit=crop&fm=jpg&q=90&w=2200',
 'https://images.unsplash.com/photo-1776935359460-6c789e972e6a?auto=format&fit=crop&fm=jpg&q=90&w=2200'
]
parts=list(re.finditer(r"src:'https://images\.unsplash\.com/[^']+'",block))
if len(parts)>=3:
    for idx,match in enumerate(reversed(parts[:3])):
        target=urls[len(parts[:3])-1-idx]
        block=block[:match.start()]+"src:'"+target+"'"+block[match.end():]
block=re.sub(r"line:'[^']+'", "line:'أسلوب عصري'", block)
block=re.sub(r"accent:'[^']+'", "accent:'لمطبخك'", block)
block=re.sub(r"lead:'[^']+'", "lead:'اكتشف منتجات مبتكرة بعناية تمنح مطبخك الجمال والعملية التي تستحقها.'", block)
js=js[:m.start()]+block+js[m.end():]

layer=r'''/* BRANDO PREMIUM FIDELITY POLISH v0.7.4 START */
body.brando-reference-070{--pf-orange:#ff7200;--pf-ink:#070707;--pf-line:#dedede;--pf-shadow:0 8px 24px rgba(0,0,0,.055)}

/* Hero fidelity: darker, warmer, more premium without changing composition. */
body.brando-reference-070 .ref-hero__media .brando-hero-scene{filter:saturate(.72) contrast(1.18) brightness(.56) sepia(.08)!important}
body.brando-reference-070 .ref-hero__media .brando-hero-scene::after{background:linear-gradient(90deg,rgba(0,0,0,.02),rgba(0,0,0,.10) 55%,rgba(0,0,0,.70) 100%)!important}
body.brando-reference-070 .ref-hero__content{background:linear-gradient(90deg,#141414,#050505 38%)!important}
body.brando-reference-070 .ref-hero__title{font-weight:950!important;text-shadow:0 2px 18px rgba(0,0,0,.18)}
body.brando-reference-070 .ref-hero__lead{color:#ededed!important}
body.brando-reference-070 .ref-btn--orange{background:linear-gradient(180deg,#ff7b12,#f26600)!important;box-shadow:0 10px 28px rgba(242,102,0,.22)!important}

/* Categories: cleaner premium cards, stronger title hierarchy, same structure. */
body.brando-reference-070 .ref-category-card{border-color:#e0e0e0!important;box-shadow:var(--pf-shadow)!important;transition:transform .28s ease,box-shadow .28s ease,border-color .28s ease}
body.brando-reference-070 .ref-category-card:hover{transform:translateY(-3px);box-shadow:0 14px 32px rgba(0,0,0,.08)!important;border-color:#d1d1d1!important}
body.brando-reference-070 .ref-category-image{background:linear-gradient(180deg,#fff,#f8f8f8)!important}
body.brando-reference-070 .ref-category-image img{object-position:center!important;transition:transform .35s ease!important}
body.brando-reference-070 .ref-category-card:hover .ref-category-image img{transform:scale(1.025)!important}
body.brando-reference-070 .ref-category-card h3{font-weight:900!important;color:#0b0b0b!important}
body.brando-reference-070 .ref-category-card p{color:#666!important}
body.brando-reference-070 .ref-category-image span{box-shadow:0 4px 14px rgba(0,0,0,.18)!important}

/* Product cards: premium retail finish, clearer hierarchy. */
body.brando-reference-070 .ref-product-card{border-color:#dedede!important;box-shadow:var(--pf-shadow)!important;transition:transform .25s ease,box-shadow .25s ease}
body.brando-reference-070 .ref-product-card:hover{transform:translateY(-3px)!important;box-shadow:0 14px 34px rgba(0,0,0,.085)!important}
body.brando-reference-070 .ref-product-image{background:linear-gradient(180deg,#fff,#fafafa)!important}
body.brando-reference-070 .ref-product-image img{object-position:center!important;transition:transform .35s ease!important}
body.brando-reference-070 .ref-product-card:hover .ref-product-image img{transform:scale(1.025)!important}
body.brando-reference-070 .ref-product-name{font-weight:800!important;color:#111!important}
body.brando-reference-070 .ref-rating span{color:#ff8700!important}
body.brando-reference-070 .ref-price{font-weight:950!important;color:#080808!important}
body.brando-reference-070 .ref-cart-btn{background:linear-gradient(180deg,#111,#000)!important;border:1px solid #000!important;box-shadow:0 5px 14px rgba(0,0,0,.10)!important}
body.brando-reference-070 .ref-cart-btn:hover{background:#1a1a1a!important}
body.brando-reference-070 .ref-heart{filter:drop-shadow(0 1px 4px rgba(255,255,255,.55))}

/* Promo: richer campaign contrast, still the exact 3-zone reference layout. */
body.brando-reference-070 .ref-promo{box-shadow:0 16px 34px rgba(0,0,0,.09)!important}
body.brando-reference-070 .ref-promo-benefits{background:linear-gradient(90deg,#ff7500,#f26400 64%,#2a1308)!important}
body.brando-reference-070 .ref-promo-copy{background:radial-gradient(circle at 50% 30%,#181818,#050505 66%)!important}
body.brando-reference-070 .ref-promo-copy h2{font-weight:900!important}
body.brando-reference-070 .ref-promo-copy h2 strong{color:var(--pf-orange)!important;text-shadow:0 2px 20px rgba(255,114,0,.12)}
body.brando-reference-070 .ref-promo-image{filter:brightness(.48) saturate(.74) contrast(1.18)!important;box-shadow:inset 26px 0 42px rgba(0,0,0,.22)!important}

/* New arrivals: slightly lighter than best sellers, same premium finish. */
body.brando-reference-070 .ref-product-card--new{box-shadow:0 6px 20px rgba(0,0,0,.045)!important}
body.brando-reference-070 .ref-product-card--new .ref-product-image{background:linear-gradient(180deg,#fff,#fafafa)!important}
body.brando-reference-070 .ref-product-card--new .ref-product-name{font-weight:780!important}

/* Trust: stronger authority without redesign. */
body.brando-reference-070 .ref-trust{background:#fff!important;border-color:#d9d9d9!important}
body.brando-reference-070 .ref-trust article>span{opacity:.86!important;filter:grayscale(1) contrast(2.3)!important}
body.brando-reference-070 .ref-trust h3{font-weight:900!important;color:#0a0a0a!important}
body.brando-reference-070 .ref-trust p{color:#666!important}

/* Newsletter/footer: denser, clearer, still reference-faithful. */
body.brando-reference-070 .ref-newsletter{background:linear-gradient(90deg,#050505,#0c0c0c)!important;border-top:1px solid #1f1f1f!important;border-bottom:1px solid #1f1f1f!important}
body.brando-reference-070 .ref-newsletter__form input{box-shadow:inset 0 0 0 1px #ececec!important}
body.brando-reference-070 .ref-newsletter__form button{background:linear-gradient(180deg,#ff7c12,#f16400)!important;font-weight:900!important}
body.brando-reference-070 .ref-footer{background:linear-gradient(180deg,#070707,#030303)!important}
body.brando-reference-070 .ref-footer nav h3,body.brando-reference-070 .ref-footer__social h3{color:#fff!important;font-weight:850!important}
body.brando-reference-070 .ref-footer nav a{color:#d5d5d5!important;transition:color .2s ease}
body.brando-reference-070 .ref-footer nav a:hover{color:#fff!important}
body.brando-reference-070 .ref-payments span{box-shadow:0 2px 8px rgba(0,0,0,.14)!important}

@media(max-width:980px){
 body.brando-reference-070 .ref-category-card:hover,body.brando-reference-070 .ref-product-card:hover{transform:none!important}
}
/* BRANDO PREMIUM FIDELITY POLISH v0.7.4 END */'''

def w(rel,text):
    p=t/rel; q=p.with_suffix(p.suffix+'.tmp-brando-074'); q.write_text(text,encoding='utf-8'); q.replace(p)

w('style.css',style)
w('functions.php',fn)
w('assets/css/luxury-v3.css',css+layer+'\n')
w('assets/js/luxury-motion.js',js)

print('PATCH_VERSION=0.7.4')
print('REFERENCE_MATCH_MODE=1TO1')
print('PREMIUM_FIDELITY_POLISH=YES')
print('HERO_DARK_WARM_FIDELITY=YES')
print('CATEGORY_PREMIUM_FINISH=YES')
print('BEST_SELLERS_PREMIUM_FINISH=YES')
print('PROMO_PREMIUM_FINISH=YES')
print('NEW_ARRIVALS_PREMIUM_FINISH=YES')
print('TRUST_AUTHORITY_FINISH=YES')
print('NEWSLETTER_FOOTER_PREMIUM_FINISH=YES')
print('TEMPLATES_CHANGED=NO')
print('SECTION_ORDER_CHANGED=NO')
print('WOOCOMMERCE_DATA_CHANGED=NO')
print('CINEMATIC_ENGINE_PRESERVED=YES')
