#!/usr/bin/env python3
from pathlib import Path
import re,sys
V='0.7.1'; S='/* BRANDO REFERENCE VISUAL CORRECTION v0.7.1 START */'; E='/* BRANDO REFERENCE VISUAL CORRECTION v0.7.1 END */'
if len(sys.argv)!=2: raise SystemExit('Usage: apply-direct.py /absolute/path/to/brando')
t=Path(sys.argv[1]).resolve(); req=['style.css','functions.php','header.php','front-page.php','footer.php','assets/css/luxury-v3.css','assets/js/luxury-motion.js']
if any(not (t/x).is_file() for x in req): raise SystemExit('Missing theme files')
r=lambda x:(t/x).read_text(encoding='utf-8')
style,fn,head,front,foot,css,js=[r(x) for x in req]
if 'BRANDO REFERENCE 1TO1 v0.7.0 START' not in css: raise SystemExit('Expected v0.7.0 reference baseline not found')
if 'BRANDO CINEMATIC HERO v0.6.1' not in js: raise SystemExit('Expected cinematic runtime not found')
for token in ['ref-topbar','ref-header','ref-hero','ref-category-grid','ref-product-grid','ref-promo','ref-trust','ref-newsletter','ref-footer']:
    if token not in head+'\n'+front+'\n'+foot+'\n'+css: raise SystemExit('Reference structure missing: '+token)
if front.count('ref-category-card')<1 or front.count('ref-product-card')<2: raise SystemExit('Reference cards missing')
style,n=re.subn(r'(?m)^Version:\s*[^\r\n]+$',f'Version: {V}',style,count=1)
if n!=1: raise SystemExit('Version update failed')
fn,n=re.subn(r"define\('BRANDO_THEME_VERSION',\s*'[^']+'\);",f"define('BRANDO_THEME_VERSION', '{V}');",fn,count=1)
if n!=1: raise SystemExit('Theme version update failed')
css=re.sub(re.escape(S)+r'.*?'+re.escape(E),'',css,flags=re.S).rstrip()+'\n\n'
layer=r'''/* BRANDO REFERENCE VISUAL CORRECTION v0.7.1 START */
/* Match the supplied reference proportions on wide desktop instead of clamping the whole page to 1180px. */
body.brando-reference-070 .ref-shell{width:91.5%!important;max-width:1760px!important}

@media(min-width:1360px){
  body.brando-reference-070 .ref-topbar{height:34px!important;font-size:13px!important}
  body.brando-reference-070 .ref-topbar__inner{height:34px!important}
  body.brando-reference-070 .ref-topbar__close{width:34px!important;height:34px!important;line-height:34px!important}

  body.brando-reference-070 .ref-header__inner{height:92px!important;grid-template-columns:1fr 330px 1fr!important}
  body.brando-reference-070 .ref-nav{height:92px!important}
  body.brando-reference-070 .ref-nav a{height:92px!important;padding-inline:24px!important;font-size:15px!important}
  body.brando-reference-070 .ref-actions{gap:25px!important}
  body.brando-reference-070 .ref-action{width:32px!important;height:42px!important}
  body.brando-reference-070 .ref-action svg{width:29px!important;height:29px!important}
  body.brando-reference-070 .ref-brand__mark{width:56px!important;height:56px!important}
  body.brando-reference-070 .ref-brand__text strong{font-size:38px!important}
  body.brando-reference-070 .ref-brand__text small{font-size:14px!important}

  body.brando-reference-070 .ref-hero__frame{height:clamp(430px,29.8vw,572px)!important;min-height:430px!important;grid-template-columns:62% 38%!important}
  body.brando-reference-070 .ref-hero__media{height:100%!important;min-height:430px!important}
  body.brando-reference-070 .ref-hero__content{height:100%!important;min-height:430px!important;padding:54px 68px 46px!important}
  body.brando-reference-070 .ref-hero__title{font-size:clamp(66px,4.65vw,90px)!important;max-width:520px!important;letter-spacing:-3px!important}
  body.brando-reference-070 .ref-hero__lead{font-size:17px!important;max-width:500px!important;margin:24px 0 26px!important;line-height:1.7!important}
  body.brando-reference-070 .ref-btn{padding:14px 34px!important;font-size:16px!important;min-height:50px!important}
  body.brando-reference-070 .ref-hero-benefits{height:66px!important;min-height:66px!important}
  body.brando-reference-070 .ref-hero-benefits>div{font-size:14px!important;gap:14px!important}
  body.brando-reference-070 .ref-benefit-icon{font-size:23px!important}

  body.brando-reference-070 .ref-section{padding:28px 0 18px!important}
  body.brando-reference-070 .ref-section-head{margin-bottom:20px!important}
  body.brando-reference-070 .ref-section-head h2{font-size:34px!important}
  body.brando-reference-070 .ref-section-head a{font-size:15px!important}

  body.brando-reference-070 .ref-category-grid{gap:20px!important}
  body.brando-reference-070 .ref-category-card{border-radius:11px!important;padding-bottom:16px!important}
  body.brando-reference-070 .ref-category-image{height:205px!important}
  body.brando-reference-070 .ref-category-image span{width:36px!important;height:36px!important;font-size:17px!important;inset-inline-start:12px!important;bottom:10px!important}
  body.brando-reference-070 .ref-category-card h3{font-size:18px!important;margin:13px 14px 5px!important}
  body.brando-reference-070 .ref-category-card p{font-size:13.5px!important;line-height:1.5!important;margin-inline:14px!important}

  body.brando-reference-070 .ref-best{padding-top:14px!important}
  body.brando-reference-070 .ref-product-grid{gap:18px!important}
  body.brando-reference-070 .ref-product-card{border-radius:10px!important;padding:0 11px 11px!important}
  body.brando-reference-070 .ref-product-image{height:224px!important;margin:0 -11px 10px!important}
  body.brando-reference-070 .ref-heart{font-size:27px!important;top:10px!important;inset-inline-end:12px!important}
  body.brando-reference-070 .ref-product-name{font-size:14.5px!important;min-height:42px!important;margin-bottom:6px!important}
  body.brando-reference-070 .ref-rating{font-size:11px!important;margin-bottom:6px!important;gap:7px!important}
  body.brando-reference-070 .ref-rating small{font-size:11px!important}
  body.brando-reference-070 .ref-price{font-size:17px!important;margin-bottom:10px!important}
  body.brando-reference-070 .ref-cart-btn{height:38px!important;font-size:13px!important}
  body.brando-reference-070 .ref-slider-arrow{font-size:42px!important;width:34px!important;height:64px!important}
  body.brando-reference-070 .ref-slider-arrow--prev{right:-48px!important}
  body.brando-reference-070 .ref-slider-arrow--next{left:-48px!important}

  body.brando-reference-070 .ref-promo-section{padding:8px 0 12px!important}
  body.brando-reference-070 .ref-promo{height:272px!important;border-radius:10px!important;grid-template-columns:27% 35% 38%!important}
  body.brando-reference-070 .ref-promo-benefits{gap:21px!important;padding:20px 34px!important}
  body.brando-reference-070 .ref-promo-benefits>div{font-size:15px!important;gap:14px!important}
  body.brando-reference-070 .ref-promo-benefits b{font-size:27px!important}
  body.brando-reference-070 .ref-promo-copy h2{font-size:34px!important;margin-bottom:11px!important}
  body.brando-reference-070 .ref-promo-copy h2 strong{font-size:48px!important;margin-top:10px!important}
  body.brando-reference-070 .ref-promo-copy p{font-size:14px!important;margin-bottom:14px!important}
  body.brando-reference-070 .ref-promo-copy .ref-btn{padding:11px 30px!important;font-size:14px!important;min-height:42px!important}
  body.brando-reference-070 .ref-promo-image{height:272px!important;min-height:272px!important}

  body.brando-reference-070 .ref-new{padding-top:12px!important;padding-bottom:20px!important}
  body.brando-reference-070 .ref-product-card--new .ref-product-image{height:205px!important}
  body.brando-reference-070 .ref-product-card--new .ref-product-name{min-height:38px!important}

  body.brando-reference-070 .ref-trust__grid{height:110px!important}
  body.brando-reference-070 .ref-trust article{gap:18px!important;padding-inline:28px!important}
  body.brando-reference-070 .ref-trust article>span{font-size:36px!important}
  body.brando-reference-070 .ref-trust h3{font-size:20px!important;margin-bottom:5px!important}
  body.brando-reference-070 .ref-trust p{font-size:13px!important}

  body.brando-reference-070 .ref-newsletter{padding:14px 0!important}
  body.brando-reference-070 .ref-newsletter__inner{height:82px!important;gap:28px!important}
  body.brando-reference-070 .ref-newsletter__icon{font-size:48px!important}
  body.brando-reference-070 .ref-newsletter h2{font-size:20px!important;margin-bottom:5px!important}
  body.brando-reference-070 .ref-newsletter p{font-size:13px!important}
  body.brando-reference-070 .ref-newsletter__form{grid-template-columns:1fr 220px!important;gap:16px!important}
  body.brando-reference-070 .ref-newsletter__form input,body.brando-reference-070 .ref-newsletter__form button{height:48px!important}
  body.brando-reference-070 .ref-newsletter__form button{font-size:17px!important}

  body.brando-reference-070 .ref-footer{padding:28px 0 14px!important}
  body.brando-reference-070 .ref-footer__grid{gap:46px!important}
  body.brando-reference-070 .ref-footer__brandline h2{font-size:38px!important}
  body.brando-reference-070 .ref-footer__mark{font-size:38px!important}
  body.brando-reference-070 .ref-footer__brand>p{font-size:13px!important;margin-bottom:16px!important}
  body.brando-reference-070 .ref-footer__brand li,body.brando-reference-070 .ref-footer nav a{font-size:13px!important;margin-block:7px!important}
  body.brando-reference-070 .ref-footer nav h3,body.brando-reference-070 .ref-footer__social h3{font-size:16px!important;margin-bottom:12px!important}
  body.brando-reference-070 .ref-footer__social>div:first-of-type a{width:34px!important;height:34px!important;font-size:15px!important}
}

@media(min-width:1800px){body.brando-reference-070 .ref-shell{max-width:1770px!important}}
/* BRANDO REFERENCE VISUAL CORRECTION v0.7.1 END */'''
def w(rel,text):
 p=t/rel; q=p.with_suffix(p.suffix+'.tmp-brando-071'); q.write_text(text,encoding='utf-8'); q.replace(p)
w('style.css',style); w('functions.php',fn); w('assets/css/luxury-v3.css',css+layer+'\n')
print('PATCH_VERSION=0.7.1')
print('REFERENCE_MATCH_MODE=1TO1')
print('REFERENCE_WIDTH_CORRECTED=YES')
print('HEADER_SCALE_CORRECTED=YES')
print('HERO_SCALE_CORRECTED=YES')
print('CATEGORY_SCALE_CORRECTED=YES')
print('BEST_SELLERS_SCALE_CORRECTED=YES')
print('PROMO_SCALE_CORRECTED=YES')
print('NEW_ARRIVALS_SCALE_CORRECTED=YES')
print('TRUST_SCALE_CORRECTED=YES')
print('NEWSLETTER_FOOTER_SCALE_CORRECTED=YES')
print('TEMPLATES_CHANGED=NO')
print('WOOCOMMERCE_DATA_CHANGED=NO')
print('CINEMATIC_ENGINE_PRESERVED=YES')