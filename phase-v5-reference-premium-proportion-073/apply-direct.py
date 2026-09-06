#!/usr/bin/env python3
from pathlib import Path
import re,sys

V='0.7.3'
S='/* BRANDO REFERENCE PREMIUM PROPORTION v0.7.3 START */'
E='/* BRANDO REFERENCE PREMIUM PROPORTION v0.7.3 END */'
JS_START='/* BRANDO CINEMATIC HERO v0.6.1 START */'
JS_END='/* BRANDO CINEMATIC HERO v0.6.1 END */'

if len(sys.argv)!=2:
    raise SystemExit('Usage: apply-direct.py /absolute/path/to/brando')

t=Path(sys.argv[1]).resolve()
req=['style.css','functions.php','header.php','front-page.php','footer.php','assets/css/luxury-v3.css','assets/js/luxury-motion.js']
missing=[x for x in req if not (t/x).is_file()]
if missing:
    raise SystemExit('Missing theme files: '+', '.join(missing))

r=lambda x:(t/x).read_text(encoding='utf-8')
style,fn,head,front,foot,css,js=[r(x) for x in req]

if 'BRANDO REFERENCE PIXEL ALIGNMENT v0.7.2 START' not in css:
    raise SystemExit('Expected v0.7.2 baseline not found')
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

# Restore three dark/warm luxury-kitchen cinematic scenes inside the 0.6.1 runtime only.
m=re.search(re.escape(JS_START)+r'.*?'+re.escape(JS_END),js,flags=re.S)
if not m:
    raise SystemExit('Cinematic block missing')
block=m.group(0)
urls=[
 'https://images.unsplash.com/photo-1771270731051-9cfbb7222946?auto=format&fit=crop&fm=jpg&q=90&w=2200',
 'https://images.unsplash.com/photo-1765766601532-90e9b96320c8?auto=format&fit=crop&fm=jpg&q=90&w=2200',
 'https://images.unsplash.com/photo-1769326541248-5e09a8ace25b?auto=format&fit=crop&fm=jpg&q=90&w=2200'
]
parts=list(re.finditer(r"src:'https://images\.unsplash\.com/[^']+'",block))
if len(parts)<3:
    raise SystemExit('Expected three cinematic scene sources')
for idx,match in enumerate(reversed(parts[:3])):
    target=urls[len(parts[:3])-1-idx]
    block=block[:match.start()]+"src:'"+target+"'"+block[match.end():]
block=re.sub(r"line:'[^']+'", "line:'أسلوب عصري'", block)
block=re.sub(r"accent:'[^']+'", "accent:'لمطبخك'", block)
block=re.sub(r"lead:'[^']+'", "lead:'اكتشف منتجات مبتكرة بعناية تمنح مطبخك الجمال والعملية التي تستحقها.'", block)
js=js[:m.start()]+block+js[m.end():]

layer=r'''/* BRANDO REFERENCE PREMIUM PROPORTION v0.7.3 START */
/* Keep the reference design. Correct only scale, breathing room, material finish and hero fidelity. */
body.brando-reference-070 .ref-shell{width:91.5%!important;max-width:1760px!important}

@media(min-width:1360px){
  /* Header: premium but still reference-faithful. */
  body.brando-reference-070 .ref-topbar{height:32px!important;font-size:12.5px!important}
  body.brando-reference-070 .ref-topbar__inner{height:32px!important}
  body.brando-reference-070 .ref-topbar__close{width:32px!important;height:32px!important;line-height:32px!important}
  body.brando-reference-070 .ref-header__inner{height:86px!important;grid-template-columns:1fr 315px 1fr!important}
  body.brando-reference-070 .ref-nav,body.brando-reference-070 .ref-nav a{height:86px!important}
  body.brando-reference-070 .ref-nav a{padding-inline:21px!important;font-size:14px!important}
  body.brando-reference-070 .ref-actions{gap:23px!important}
  body.brando-reference-070 .ref-action{width:30px!important;height:40px!important}
  body.brando-reference-070 .ref-action svg{width:27px!important;height:27px!important}
  body.brando-reference-070 .ref-brand__mark{width:52px!important;height:52px!important}
  body.brando-reference-070 .ref-brand__text strong{font-size:35px!important}
  body.brando-reference-070 .ref-brand__text small{font-size:13px!important}

  /* Hero: restore presence without becoming oversized. */
  body.brando-reference-070 .ref-hero__frame{height:440px!important;min-height:440px!important;grid-template-columns:63% 37%!important}
  body.brando-reference-070 .ref-hero__media{height:440px!important;min-height:440px!important;background:#070707!important}
  body.brando-reference-070 .ref-hero__media .brando-hero-scene{inset:-2.5%!important;background-size:cover!important;background-position:center 50%!important;filter:saturate(.78) contrast(1.14) brightness(.68) sepia(.05)!important}
  body.brando-reference-070 .ref-hero__media .brando-hero-scene::after{background:linear-gradient(90deg,rgba(0,0,0,.02),rgba(0,0,0,.06) 66%,rgba(0,0,0,.58) 100%)!important}
  body.brando-reference-070 .ref-hero__content{height:440px!important;min-height:440px!important;padding:48px 60px 40px!important;background:linear-gradient(90deg,#151515,#050505 35%)!important}
  body.brando-reference-070 .ref-hero__title{font-size:66px!important;line-height:.95!important;max-width:430px!important;letter-spacing:-2.4px!important}
  body.brando-reference-070 .ref-hero__lead{font-size:15.5px!important;line-height:1.68!important;max-width:430px!important;margin:21px 0 23px!important;color:#e3e3e3!important}
  body.brando-reference-070 .ref-btn{padding:12px 30px!important;font-size:14px!important;min-height:44px!important;border-radius:4px!important}
  body.brando-reference-070 .ref-hero-benefits{height:60px!important;min-height:60px!important}
  body.brando-reference-070 .ref-hero-benefits>div{font-size:13px!important;gap:12px!important}
  body.brando-reference-070 .ref-benefit-icon{font-size:21px!important}

  /* Section rhythm: more breathing, same structure. */
  body.brando-reference-070 .ref-section{padding:24px 0 16px!important}
  body.brando-reference-070 .ref-section-head{margin-bottom:17px!important}
  body.brando-reference-070 .ref-section-head h2{font-size:30px!important;letter-spacing:-.02em!important}
  body.brando-reference-070 .ref-section-head a{font-size:13.5px!important}

  /* Categories: six cards, premium scale, no redesign. */
  body.brando-reference-070 .ref-category-grid{gap:17px!important}
  body.brando-reference-070 .ref-category-card{border-radius:10px!important;padding-bottom:14px!important;box-shadow:0 5px 18px rgba(0,0,0,.035)!important}
  body.brando-reference-070 .ref-category-image{height:176px!important;padding:10px!important;background:#fafafa!important}
  body.brando-reference-070 .ref-category-image img{object-fit:contain!important;filter:saturate(.9) contrast(.99) brightness(1.03)!important}
  body.brando-reference-070 .ref-category-image span{width:33px!important;height:33px!important;font-size:16px!important;inset-inline-start:11px!important;bottom:9px!important}
  body.brando-reference-070 .ref-category-card h3{font-size:16.5px!important;margin:11px 12px 4px!important}
  body.brando-reference-070 .ref-category-card p{font-size:12.5px!important;line-height:1.48!important;margin-inline:12px!important}

  /* Best sellers: restore readable premium retail cards. */
  body.brando-reference-070 .ref-best{padding-top:11px!important}
  body.brando-reference-070 .ref-product-grid{gap:15px!important}
  body.brando-reference-070 .ref-product-card{border-radius:9px!important;padding:0 10px 10px!important;box-shadow:0 5px 18px rgba(0,0,0,.035)!important}
  body.brando-reference-070 .ref-product-image{height:192px!important;margin:0 -10px 9px!important;padding:9px!important;background:#fff!important}
  body.brando-reference-070 .ref-product-image img{object-fit:contain!important}
  body.brando-reference-070 .ref-heart{font-size:25px!important;top:9px!important;inset-inline-end:10px!important}
  body.brando-reference-070 .ref-product-name{font-size:13.5px!important;min-height:38px!important;margin-bottom:5px!important}
  body.brando-reference-070 .ref-rating{font-size:10px!important;margin-bottom:5px!important;gap:6px!important}
  body.brando-reference-070 .ref-rating small{font-size:10px!important}
  body.brando-reference-070 .ref-price{font-size:15.5px!important;margin-bottom:9px!important}
  body.brando-reference-070 .ref-cart-btn{height:34px!important;font-size:11.5px!important;border-radius:4px!important}
  body.brando-reference-070 .ref-slider-arrow{font-size:40px!important;width:30px!important;height:58px!important}
  body.brando-reference-070 .ref-slider-arrow--prev{right:-42px!important}
  body.brando-reference-070 .ref-slider-arrow--next{left:-42px!important}

  /* Promo: same 3-zone reference composition, stronger visual presence. */
  body.brando-reference-070 .ref-promo-section{padding:6px 0 10px!important}
  body.brando-reference-070 .ref-promo{height:226px!important;border-radius:9px!important;grid-template-columns:27% 35% 38%!important}
  body.brando-reference-070 .ref-promo-benefits{gap:18px!important;padding:17px 29px!important}
  body.brando-reference-070 .ref-promo-benefits>div{font-size:14px!important;gap:12px!important}
  body.brando-reference-070 .ref-promo-benefits b{font-size:24px!important}
  body.brando-reference-070 .ref-promo-copy h2{font-size:29px!important;margin-bottom:9px!important}
  body.brando-reference-070 .ref-promo-copy h2 strong{font-size:40px!important;margin-top:8px!important}
  body.brando-reference-070 .ref-promo-copy p{font-size:12.5px!important;margin-bottom:12px!important}
  body.brando-reference-070 .ref-promo-copy .ref-btn{padding:10px 26px!important;font-size:12.5px!important;min-height:38px!important}
  body.brando-reference-070 .ref-promo-image{height:226px!important;min-height:226px!important;background-image:url('https://images.unsplash.com/photo-1765766601532-90e9b96320c8?auto=format&fit=crop&fm=jpg&q=88&w=1800')!important;background-position:center 52%!important;filter:brightness(.62) saturate(.76) contrast(1.12)!important}

  /* New arrivals: secondary, but no longer compressed. */
  body.brando-reference-070 .ref-new{padding-top:9px!important;padding-bottom:17px!important}
  body.brando-reference-070 .ref-product-card--new .ref-product-image{height:170px!important;padding:9px!important}
  body.brando-reference-070 .ref-product-card--new .ref-product-name{min-height:35px!important}

  /* Trust, newsletter and footer: premium breathing while staying compact. */
  body.brando-reference-070 .ref-trust__grid{height:92px!important}
  body.brando-reference-070 .ref-trust article{gap:15px!important;padding-inline:23px!important}
  body.brando-reference-070 .ref-trust article>span{font-size:31px!important}
  body.brando-reference-070 .ref-trust h3{font-size:17px!important;margin-bottom:4px!important}
  body.brando-reference-070 .ref-trust p{font-size:11.5px!important}

  body.brando-reference-070 .ref-newsletter{padding:11px 0!important}
  body.brando-reference-070 .ref-newsletter__inner{height:70px!important;gap:22px!important}
  body.brando-reference-070 .ref-newsletter__icon{font-size:42px!important}
  body.brando-reference-070 .ref-newsletter h2{font-size:17px!important;margin-bottom:4px!important}
  body.brando-reference-070 .ref-newsletter p{font-size:11.5px!important}
  body.brando-reference-070 .ref-newsletter__form{grid-template-columns:1fr 185px!important;gap:14px!important}
  body.brando-reference-070 .ref-newsletter__form input,body.brando-reference-070 .ref-newsletter__form button{height:42px!important}
  body.brando-reference-070 .ref-newsletter__form button{font-size:15px!important}

  body.brando-reference-070 .ref-footer{padding:22px 0 10px!important}
  body.brando-reference-070 .ref-footer__grid{gap:38px!important}
  body.brando-reference-070 .ref-footer__brandline h2{font-size:34px!important}
  body.brando-reference-070 .ref-footer__mark{font-size:34px!important}
  body.brando-reference-070 .ref-footer__brand>p{font-size:12px!important;margin-bottom:14px!important}
  body.brando-reference-070 .ref-footer__brand li,body.brando-reference-070 .ref-footer nav a{font-size:11.5px!important;margin-block:6px!important}
  body.brando-reference-070 .ref-footer nav h3,body.brando-reference-070 .ref-footer__social h3{font-size:14.5px!important;margin-bottom:10px!important}
  body.brando-reference-070 .ref-footer__social>div:first-of-type a{width:30px!important;height:30px!important;font-size:13px!important}
}

@media(min-width:1800px){body.brando-reference-070 .ref-shell{max-width:1760px!important}}
/* BRANDO REFERENCE PREMIUM PROPORTION v0.7.3 END */'''

def w(rel,text):
    p=t/rel
    q=p.with_suffix(p.suffix+'.tmp-brando-073')
    q.write_text(text,encoding='utf-8')
    q.replace(p)

w('style.css',style)
w('functions.php',fn)
w('assets/css/luxury-v3.css',css+layer+'\n')
w('assets/js/luxury-motion.js',js)

print('PATCH_VERSION=0.7.3')
print('REFERENCE_MATCH_MODE=1TO1')
print('PREMIUM_PROPORTION_LOCK=YES')
print('REFERENCE_WIDTH_RESTORED=YES')
print('HEADER_PREMIUM_SCALE=YES')
print('HERO_PREMIUM_SCALE=YES')
print('HERO_DARK_KITCHEN_LOCK=YES')
print('CATEGORY_PREMIUM_SCALE=YES')
print('BEST_SELLERS_PREMIUM_SCALE=YES')
print('PROMO_PREMIUM_SCALE=YES')
print('NEW_ARRIVALS_PREMIUM_SCALE=YES')
print('TRUST_PREMIUM_SCALE=YES')
print('NEWSLETTER_PREMIUM_SCALE=YES')
print('FOOTER_PREMIUM_SCALE=YES')
print('TEMPLATES_CHANGED=NO')
print('WOOCOMMERCE_DATA_CHANGED=NO')
print('CINEMATIC_ENGINE_PRESERVED=YES')
