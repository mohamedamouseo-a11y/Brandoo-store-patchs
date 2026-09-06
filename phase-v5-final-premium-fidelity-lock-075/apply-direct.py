#!/usr/bin/env python3
from pathlib import Path
import re,sys

V='0.7.5'
S='/* BRANDO FINAL PREMIUM FIDELITY LOCK v0.7.5 START */'
E='/* BRANDO FINAL PREMIUM FIDELITY LOCK v0.7.5 END */'
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

if 'BRANDO PREMIUM FIDELITY POLISH v0.7.4 START' not in css:
    raise SystemExit('Expected v0.7.4 baseline not found')
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

# Preserve the cinematic engine, but lock all three scenes to the same reference-safe copy.
m=re.search(re.escape(JS_START)+r'.*?'+re.escape(JS_END),js,flags=re.S)
if not m: raise SystemExit('Cinematic block missing')
block=m.group(0)
block=re.sub(r"line:'[^']+'", "line:'أسلوب عصري'", block)
block=re.sub(r"accent:'[^']+'", "accent:'لمطبخك'", block)
block=re.sub(r"lead:'[^']+'", "lead:'اكتشف منتجات مبتكرة بعناية تمنح مطبخك الجمال والعملية التي تستحقها.'", block)
js=js[:m.start()]+block+js[m.end():]

layer=r'''/* BRANDO FINAL PREMIUM FIDELITY LOCK v0.7.5 START */
body.brando-reference-070{
  --pf-orange:#ff7000;
  --pf-orange-dark:#e95d00;
  --pf-ink:#060606;
  --pf-line:#d9d9d9;
  --pf-soft:#f8f8f8;
  --pf-shadow:0 10px 26px rgba(0,0,0,.055);
}

/* 1) HERO — stay reference-faithful, but create a richer dark/warm luxury mood. */
body.brando-reference-070 .ref-hero__media{background:#080706!important}
body.brando-reference-070 .ref-hero__media .brando-hero-scene{
  filter:saturate(.66) contrast(1.24) brightness(.50) sepia(.13)!important;
  background-position:center 54%!important;
}
body.brando-reference-070 .ref-hero__media .brando-hero-scene::before{
  content:"";position:absolute;inset:0;z-index:1;pointer-events:none;
  background:radial-gradient(circle at 38% 44%,rgba(184,100,40,.13),transparent 34%),linear-gradient(180deg,rgba(0,0,0,.02),rgba(0,0,0,.20));
  mix-blend-mode:soft-light;
}
body.brando-reference-070 .ref-hero__media .brando-hero-scene::after{
  z-index:2!important;
  background:linear-gradient(90deg,rgba(0,0,0,.04),rgba(0,0,0,.10) 48%,rgba(0,0,0,.48) 76%,rgba(0,0,0,.78) 100%)!important;
}
body.brando-reference-070 .ref-hero__content{
  background:linear-gradient(90deg,#17130f,#060606 37%)!important;
  box-shadow:inset 1px 0 0 rgba(255,255,255,.025)!important;
}
body.brando-reference-070 .ref-hero__title{font-weight:950!important;text-shadow:0 8px 28px rgba(0,0,0,.34)!important}
body.brando-reference-070 .ref-hero__title strong{color:var(--pf-orange)!important}
body.brando-reference-070 .ref-hero__lead{color:#e8e4df!important}
body.brando-reference-070 .ref-btn--orange{
  background:linear-gradient(180deg,#ff7d18,var(--pf-orange-dark))!important;
  box-shadow:0 12px 30px rgba(233,93,0,.28)!important;
  border:1px solid rgba(255,255,255,.08)!important;
}
body.brando-reference-070 .ref-hero-benefits{box-shadow:0 8px 22px rgba(0,0,0,.08)!important}

/* 2) CATEGORIES + PRODUCT IMAGERY — cleaner retail presentation, no structure change. */
body.brando-reference-070 .ref-category-card,
body.brando-reference-070 .ref-product-card{
  border-color:var(--pf-line)!important;
  box-shadow:var(--pf-shadow)!important;
  background:#fff!important;
}
body.brando-reference-070 .ref-category-card:hover,
body.brando-reference-070 .ref-product-card:hover{
  transform:translateY(-3px)!important;
  box-shadow:0 16px 36px rgba(0,0,0,.085)!important;
}
body.brando-reference-070 .ref-category-image,
body.brando-reference-070 .ref-product-image{
  background:linear-gradient(180deg,#fff 0%,#fafafa 70%,#f5f5f5 100%)!important;
  overflow:hidden!important;
}
body.brando-reference-070 .ref-category-image img,
body.brando-reference-070 .ref-product-image img{
  object-fit:contain!important;
  object-position:center!important;
  filter:saturate(.92) contrast(1.01) brightness(1.03)!important;
  transform:scale(.965)!important;
  transition:transform .32s ease,filter .32s ease!important;
}
body.brando-reference-070 .ref-category-card:hover .ref-category-image img,
body.brando-reference-070 .ref-product-card:hover .ref-product-image img{
  transform:scale(.99)!important;
}
body.brando-reference-070 .ref-category-card h3,
body.brando-reference-070 .ref-product-name{color:#0b0b0b!important;font-weight:900!important}
body.brando-reference-070 .ref-category-card p{color:#626262!important}
body.brando-reference-070 .ref-rating span{color:#ff8400!important}
body.brando-reference-070 .ref-price{font-weight:950!important;letter-spacing:-.01em!important}
body.brando-reference-070 .ref-cart-btn{
  background:linear-gradient(180deg,#111,#030303)!important;
  border:1px solid #000!important;
  box-shadow:0 5px 12px rgba(0,0,0,.12)!important;
  transition:background .22s ease,transform .22s ease!important;
}
body.brando-reference-070 .ref-cart-btn:hover{background:var(--pf-orange-dark)!important;transform:translateY(-1px)!important}
body.brando-reference-070 .ref-heart{filter:drop-shadow(0 2px 6px rgba(255,255,255,.45))!important}

/* 3) PROMO — strengthen the campaign image side and central message. */
body.brando-reference-070 .ref-promo{
  box-shadow:0 14px 36px rgba(0,0,0,.10)!important;
  border:1px solid rgba(0,0,0,.05)!important;
}
body.brando-reference-070 .ref-promo-benefits{
  background:linear-gradient(90deg,#ff7600,#ed6100 66%,#26140a)!important;
}
body.brando-reference-070 .ref-promo-copy{
  background:radial-gradient(circle at 55% 35%,rgba(255,118,0,.055),transparent 30%),linear-gradient(90deg,#161616,#050505)!important;
}
body.brando-reference-070 .ref-promo-copy h2{font-weight:950!important}
body.brando-reference-070 .ref-promo-copy h2 strong{color:var(--pf-orange)!important;text-shadow:0 6px 18px rgba(255,112,0,.12)!important}
body.brando-reference-070 .ref-promo-image{
  filter:brightness(.48) saturate(.70) contrast(1.22) sepia(.08)!important;
  background-position:center 48%!important;
  position:relative!important;
}
body.brando-reference-070 .ref-promo-image::after{
  content:"";position:absolute;inset:0;pointer-events:none;
  background:linear-gradient(90deg,rgba(0,0,0,.62),rgba(0,0,0,.08) 52%,rgba(0,0,0,.16))!important;
}

/* 4) TRUST — stronger authority and contrast, same four blocks. */
body.brando-reference-070 .ref-trust{background:#fff!important;border-color:#d8d8d8!important}
body.brando-reference-070 .ref-trust article{background:linear-gradient(180deg,#fff,#fcfcfc)!important}
body.brando-reference-070 .ref-trust article>span{
  color:#111!important;opacity:1!important;filter:grayscale(1) contrast(2.3)!important;
  transform:scale(1.04)!important;
}
body.brando-reference-070 .ref-trust h3{color:#111!important;font-weight:950!important}
body.brando-reference-070 .ref-trust p{color:#565656!important;font-weight:600!important}

/* 5) NEWSLETTER + FOOTER — denser premium ending, no structural change. */
body.brando-reference-070 .ref-newsletter{
  background:linear-gradient(180deg,#090909,#030303)!important;
  border-top:1px solid #171717!important;
  border-bottom:1px solid #171717!important;
}
body.brando-reference-070 .ref-newsletter__icon{color:var(--pf-orange)!important;filter:drop-shadow(0 0 12px rgba(255,112,0,.16))!important}
body.brando-reference-070 .ref-newsletter h2{font-weight:950!important}
body.brando-reference-070 .ref-newsletter p{color:#bdbdbd!important}
body.brando-reference-070 .ref-newsletter__form input{
  border:1px solid #dedede!important;
  box-shadow:inset 0 1px 2px rgba(0,0,0,.04)!important;
}
body.brando-reference-070 .ref-newsletter__form button{
  background:linear-gradient(180deg,#ff7c15,#ef6200)!important;
  box-shadow:0 8px 18px rgba(239,98,0,.20)!important;
}
body.brando-reference-070 .ref-footer{
  background:radial-gradient(circle at 90% 0,rgba(255,112,0,.045),transparent 22%),#030303!important;
}
body.brando-reference-070 .ref-footer__brandline h2{font-weight:950!important}
body.brando-reference-070 .ref-footer__mark{color:var(--pf-orange)!important}
body.brando-reference-070 .ref-footer nav h3,
body.brando-reference-070 .ref-footer__social h3{color:#fff!important;font-weight:900!important}
body.brando-reference-070 .ref-footer nav a,
body.brando-reference-070 .ref-footer__brand li{color:#d1d1d1!important}
body.brando-reference-070 .ref-footer nav a:hover{color:var(--pf-orange)!important}
body.brando-reference-070 .ref-footer__social>div:first-of-type a{border-color:#555!important;background:#090909!important}
body.brando-reference-070 .ref-payments span{box-shadow:0 2px 6px rgba(0,0,0,.20)!important}

@media(max-width:980px){
 body.brando-reference-070 .ref-category-card:hover,
 body.brando-reference-070 .ref-product-card:hover{transform:none!important}
 body.brando-reference-070 .ref-hero__media .brando-hero-scene{filter:saturate(.70) contrast(1.16) brightness(.58) sepia(.08)!important}
}
/* BRANDO FINAL PREMIUM FIDELITY LOCK v0.7.5 END */'''

def w(rel,text):
    p=t/rel
    q=p.with_suffix(p.suffix+'.tmp-brando-075')
    q.write_text(text,encoding='utf-8')
    q.replace(p)

w('style.css',style)
w('functions.php',fn)
w('assets/css/luxury-v3.css',css+layer+'\n')
w('assets/js/luxury-motion.js',js)

print('PATCH_VERSION=0.7.5')
print('REFERENCE_MATCH_MODE=1TO1')
print('FINAL_PREMIUM_FIDELITY_LOCK=YES')
print('HERO_FINAL_PREMIUM_FINISH=YES')
print('CATEGORY_IMAGERY_FINAL_FINISH=YES')
print('BEST_SELLERS_FINAL_FINISH=YES')
print('PROMO_FINAL_CAMPAIGN_FINISH=YES')
print('NEW_ARRIVALS_FINAL_FINISH=YES')
print('TRUST_FINAL_AUTHORITY=YES')
print('NEWSLETTER_FOOTER_FINAL_FINISH=YES')
print('TEMPLATES_CHANGED=NO')
print('SECTION_ORDER_CHANGED=NO')
print('WOOCOMMERCE_DATA_CHANGED=NO')
print('CINEMATIC_ENGINE_PRESERVED=YES')
