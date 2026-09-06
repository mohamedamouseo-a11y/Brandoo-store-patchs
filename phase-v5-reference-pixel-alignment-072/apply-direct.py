#!/usr/bin/env python3
from pathlib import Path
import re,sys

V='0.7.2'
S='/* BRANDO REFERENCE PIXEL ALIGNMENT v0.7.2 START */'
E='/* BRANDO REFERENCE PIXEL ALIGNMENT v0.7.2 END */'
if len(sys.argv)!=2: raise SystemExit('Usage: apply-direct.py /absolute/path/to/brando')
t=Path(sys.argv[1]).resolve()
req=['style.css','functions.php','header.php','front-page.php','footer.php','assets/css/luxury-v3.css','assets/js/luxury-motion.js']
if any(not (t/x).is_file() for x in req): raise SystemExit('Missing theme files')
r=lambda x:(t/x).read_text(encoding='utf-8')
style,fn,head,front,foot,css,js=[r(x) for x in req]
if 'BRANDO REFERENCE 1TO1 v0.7.0 START' not in css: raise SystemExit('Expected v0.7.0 reference layer missing')
if 'BRANDO REFERENCE VISUAL CORRECTION v0.7.1 START' not in css: raise SystemExit('Expected v0.7.1 correction missing')
if 'BRANDO CINEMATIC HERO v0.6.1' not in js: raise SystemExit('Expected cinematic runtime missing')
for token in ['ref-topbar','ref-header','ref-hero','ref-category-grid','ref-product-grid','ref-promo','ref-trust','ref-newsletter','ref-footer']:
    if token not in head+'\n'+front+'\n'+foot+'\n'+css: raise SystemExit('Reference structure missing: '+token)
style,n=re.subn(r'(?m)^Version:\s*[^\r\n]+$',f'Version: {V}',style,count=1)
if n!=1: raise SystemExit('Version update failed')
fn,n=re.subn(r"define\('BRANDO_THEME_VERSION',\s*'[^']+'\);",f"define('BRANDO_THEME_VERSION', '{V}');",fn,count=1)
if n!=1: raise SystemExit('Theme version update failed')
css=re.sub(re.escape(S)+r'.*?'+re.escape(E),'',css,flags=re.S).rstrip()+'\n\n'

# Lock the cinematic hero to one warm dark reference-like scene while preserving autoplay/Ken Burns/dots.
hero_url='https://images.unsplash.com/photo-1453614512568-c4024d13c247?auto=format&fit=crop&fm=jpg&q=86&w=2200'
js=re.sub(r"src:'https://images\.unsplash\.com/[^']+'", "src:'"+hero_url+"'", js)

layer=r'''/* BRANDO REFERENCE PIXEL ALIGNMENT v0.7.2 START */
/* Keep 0.7.0 geometry but align visual treatment to supplied reference. */
body.brando-reference-070{background:#fff!important;color:#111!important}
body.brando-reference-070 .ref-shell{width:91.5%!important;max-width:1460px!important}

/* Header/topbar: same compact black/orange rhythm as reference. */
body.brando-reference-070 .ref-topbar{background:#ff7300!important;height:30px!important;font-size:12px!important}
body.brando-reference-070 .ref-topbar__inner{height:30px!important}
body.brando-reference-070 .ref-header__inner{height:76px!important;grid-template-columns:1fr 290px 1fr!important}
body.brando-reference-070 .ref-nav,body.brando-reference-070 .ref-nav a{height:76px!important}
body.brando-reference-070 .ref-nav a{padding-inline:18px!important;font-size:13px!important}
body.brando-reference-070 .ref-brand__mark{width:48px!important;height:48px!important}
body.brando-reference-070 .ref-brand__text strong{font-size:32px!important}
body.brando-reference-070 .ref-brand__text small{font-size:12px!important}
body.brando-reference-070 .ref-actions{gap:20px!important}

/* Hero: warm/dark photographic treatment and exact compact split. */
body.brando-reference-070 .ref-hero__frame{height:310px!important;min-height:310px!important;grid-template-columns:63.5% 36.5%!important}
body.brando-reference-070 .ref-hero__media{height:310px!important;min-height:310px!important;background:#080808!important}
body.brando-reference-070 .ref-hero__media .brando-hero-scene{inset:-2%!important;background-size:cover!important;background-position:center 52%!important;filter:saturate(.82) contrast(1.18) brightness(.62) sepia(.08)!important}
body.brando-reference-070 .ref-hero__media .brando-hero-scene::after{background:linear-gradient(90deg,rgba(0,0,0,.02),rgba(0,0,0,.05) 62%,rgba(0,0,0,.55) 100%)!important}
body.brando-reference-070 .ref-hero__content{height:310px!important;min-height:310px!important;padding:34px 46px 28px!important;background:linear-gradient(90deg,#171717,#050505 34%)!important}
body.brando-reference-070 .ref-hero__title{font-size:51px!important;line-height:.96!important;max-width:340px!important;letter-spacing:-2px!important}
body.brando-reference-070 .ref-hero__lead{font-size:14px!important;line-height:1.6!important;max-width:330px!important;margin:17px 0 18px!important}
body.brando-reference-070 .ref-btn{min-height:0!important;padding:10px 24px!important;font-size:13px!important}
body.brando-reference-070 .ref-hero-benefits{height:48px!important;min-height:48px!important}
body.brando-reference-070 .ref-hero-benefits>div{font-size:12px!important;gap:10px!important}
body.brando-reference-070 .ref-benefit-icon{font-size:18px!important;color:#ff7300!important}

/* Section typography exactly compact like reference. */
body.brando-reference-070 .ref-section{padding:18px 0 12px!important}
body.brando-reference-070 .ref-section-head{margin-bottom:13px!important}
body.brando-reference-070 .ref-section-head h2{font-size:24px!important}
body.brando-reference-070 .ref-section-head a{font-size:12px!important}

/* Categories: convert current lifestyle thumbnails toward clean packshot cards. */
body.brando-reference-070 .ref-category-grid{gap:14px!important}
body.brando-reference-070 .ref-category-card{border:1px solid #ddd!important;border-radius:9px!important;background:#fff!important;padding-bottom:12px!important;box-shadow:0 1px 4px rgba(0,0,0,.025)!important}
body.brando-reference-070 .ref-category-image{height:112px!important;background:#f7f7f7!important;padding:8px!important}
body.brando-reference-070 .ref-category-image img{width:100%!important;height:100%!important;object-fit:contain!important;filter:saturate(.88) contrast(.98) brightness(1.04)!important;transform:none!important;border-radius:0!important}
body.brando-reference-070 .ref-category-image span{width:28px!important;height:28px!important;inset-inline-start:10px!important;bottom:8px!important;background:#050505!important;color:#ff7300!important;border:1px solid #ff7300!important}
body.brando-reference-070 .ref-category-card h3{font-size:14px!important;margin:9px 10px 3px!important}
body.brando-reference-070 .ref-category-card p{font-size:11px!important;line-height:1.45!important;margin-inline:10px!important;color:#555!important}

/* Best sellers: clean white retail cards like reference, not editorial crops. */
body.brando-reference-070 .ref-best{padding-top:8px!important}
body.brando-reference-070 .ref-product-grid{gap:12px!important}
body.brando-reference-070 .ref-product-card{background:#fff!important;border:1px solid #ddd!important;border-radius:8px!important;padding:0 8px 8px!important;box-shadow:0 1px 4px rgba(0,0,0,.025)!important}
body.brando-reference-070 .ref-product-image{height:122px!important;margin:0 -8px 7px!important;background:#fff!important;padding:7px!important}
body.brando-reference-070 .ref-product-image img{width:100%!important;height:100%!important;object-fit:contain!important;filter:none!important;transform:none!important;box-shadow:none!important}
body.brando-reference-070 .ref-heart{font-size:22px!important;top:7px!important;inset-inline-end:8px!important;color:#111!important}
body.brando-reference-070 .ref-product-name{font-size:11.5px!important;line-height:1.35!important;min-height:32px!important;margin-bottom:4px!important}
body.brando-reference-070 .ref-rating{font-size:9px!important;margin-bottom:4px!important;gap:5px!important}
body.brando-reference-070 .ref-rating small{font-size:9px!important}
body.brando-reference-070 .ref-price{font-size:13px!important;margin-bottom:7px!important}
body.brando-reference-070 .ref-cart-btn{height:27px!important;font-size:10px!important;border-radius:4px!important;background:#050505!important;color:#fff!important}
body.brando-reference-070 .ref-slider-arrow{font-size:36px!important;width:26px!important;height:50px!important}
body.brando-reference-070 .ref-slider-arrow--prev{right:-35px!important}
body.brando-reference-070 .ref-slider-arrow--next{left:-35px!important}

/* Promo: reference three-zone campaign, warm image grading. */
body.brando-reference-070 .ref-promo-section{padding:3px 0 7px!important}
body.brando-reference-070 .ref-promo{height:150px!important;border-radius:8px!important;grid-template-columns:27% 35% 38%!important}
body.brando-reference-070 .ref-promo-benefits{gap:13px!important;padding:12px 23px!important;background:linear-gradient(90deg,#ff6f00,#ee6200 64%,#24130b)!important}
body.brando-reference-070 .ref-promo-benefits>div{font-size:12px!important;gap:10px!important}
body.brando-reference-070 .ref-promo-benefits b{font-size:20px!important}
body.brando-reference-070 .ref-promo-copy h2{font-size:23px!important;margin-bottom:7px!important}
body.brando-reference-070 .ref-promo-copy h2 strong{font-size:31px!important;margin-top:7px!important;color:#ff7300!important}
body.brando-reference-070 .ref-promo-copy p{font-size:11px!important;margin-bottom:9px!important}
body.brando-reference-070 .ref-promo-copy .ref-btn{padding:8px 22px!important;font-size:11px!important;min-height:0!important}
body.brando-reference-070 .ref-promo-image{height:150px!important;min-height:150px!important;background-image:url('https://images.unsplash.com/photo-1453614512568-c4024d13c247?auto=format&fit=crop&fm=jpg&q=84&w=1400')!important;background-position:center 58%!important;background-size:cover!important;filter:brightness(.58) saturate(.78) contrast(1.12)!important}

/* New arrivals: clean product packshot language. */
body.brando-reference-070 .ref-new{padding-top:5px!important;padding-bottom:13px!important}
body.brando-reference-070 .ref-product-card--new .ref-product-image{height:112px!important;background:#fff!important;padding:7px!important}
body.brando-reference-070 .ref-product-card--new .ref-product-image img{object-fit:contain!important;filter:none!important}
body.brando-reference-070 .ref-product-card--new .ref-product-name{min-height:30px!important}
body.brando-reference-070 .ref-product-card--new .ref-price{margin-bottom:0!important}

/* Trust: reference black line-art feel, no colored emoji look. */
body.brando-reference-070 .ref-trust__grid{height:78px!important}
body.brando-reference-070 .ref-trust article{gap:13px!important;padding:8px 20px!important}
body.brando-reference-070 .ref-trust article>span{font-size:27px!important;filter:grayscale(1) contrast(2)!important;color:#111!important}
body.brando-reference-070 .ref-trust h3{font-size:15px!important;margin-bottom:3px!important}
body.brando-reference-070 .ref-trust p{font-size:10px!important}

/* Newsletter was horizontally reversed vs reference: copy left, form right. */
body.brando-reference-070 .ref-newsletter{padding:9px 0!important;background:#050505!important}
body.brando-reference-070 .ref-newsletter__inner{height:60px!important;display:grid!important;grid-template-columns:44% 56%!important;gap:18px!important;direction:ltr!important}
body.brando-reference-070 .ref-newsletter__copy{grid-column:1!important;direction:rtl!important;justify-self:stretch!important}
body.brando-reference-070 .ref-newsletter__form{grid-column:2!important;display:grid!important;grid-template-columns:1fr 160px!important;gap:12px!important;direction:ltr!important}
body.brando-reference-070 .ref-newsletter__form input{grid-column:1!important;text-align:right!important;height:38px!important}
body.brando-reference-070 .ref-newsletter__form button{grid-column:2!important;height:38px!important;font-size:14px!important;background:#ff7300!important}
body.brando-reference-070 .ref-newsletter__icon{font-size:38px!important;color:#ff7300!important}
body.brando-reference-070 .ref-newsletter h2{font-size:15px!important;margin-bottom:3px!important}
body.brando-reference-070 .ref-newsletter p{font-size:10px!important}

/* Footer: return to compact reference density. */
body.brando-reference-070 .ref-footer{padding:17px 0 8px!important}
body.brando-reference-070 .ref-footer__grid{gap:30px!important}
body.brando-reference-070 .ref-footer__brandline h2{font-size:30px!important}
body.brando-reference-070 .ref-footer__mark{font-size:30px!important;color:#ff7300!important}
body.brando-reference-070 .ref-footer__brand>p{font-size:11px!important;margin-bottom:12px!important}
body.brando-reference-070 .ref-footer__brand li,body.brando-reference-070 .ref-footer nav a{font-size:10.5px!important;margin-block:5px!important}
body.brando-reference-070 .ref-footer nav h3,body.brando-reference-070 .ref-footer__social h3{font-size:13px!important;margin-bottom:9px!important}
body.brando-reference-070 .ref-footer__social>div:first-of-type a{width:26px!important;height:26px!important;font-size:12px!important}

@media(max-width:980px){
 body.brando-reference-070 .ref-shell{width:94%!important}
 body.brando-reference-070 .ref-newsletter__inner{height:auto!important;grid-template-columns:1fr!important;padding-block:12px!important}
 body.brando-reference-070 .ref-newsletter__copy,body.brando-reference-070 .ref-newsletter__form{grid-column:1!important}
}
/* BRANDO REFERENCE PIXEL ALIGNMENT v0.7.2 END */'''

def w(rel,text):
 p=t/rel; q=p.with_suffix(p.suffix+'.tmp-brando-072'); q.write_text(text,encoding='utf-8'); q.replace(p)
w('style.css',style); w('functions.php',fn); w('assets/css/luxury-v3.css',css+layer+'\n'); w('assets/js/luxury-motion.js',js)
print('PATCH_VERSION=0.7.2')
print('REFERENCE_MATCH_MODE=1TO1')
print('REFERENCE_PIXEL_ALIGNMENT=YES')
print('HERO_WARM_DARK_LOCK=YES')
print('CATEGORY_PACKSHOT_TREATMENT=YES')
print('BEST_SELLERS_PACKSHOT_TREATMENT=YES')
print('PROMO_WARM_DARK_LOCK=YES')
print('NEW_ARRIVALS_PACKSHOT_TREATMENT=YES')
print('TRUST_ICON_TREATMENT=REFERENCE')
print('NEWSLETTER_DIRECTION_FIXED=YES')
print('FOOTER_DENSITY_FIXED=YES')
print('TEMPLATES_CHANGED=NO')
print('WOOCOMMERCE_DATA_CHANGED=NO')
print('CINEMATIC_ENGINE_PRESERVED=YES')
