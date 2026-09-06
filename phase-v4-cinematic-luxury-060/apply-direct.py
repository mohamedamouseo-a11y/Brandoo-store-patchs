#!/usr/bin/env python3
from pathlib import Path
import re, sys

VERSION = '0.6.0'
CSS_START = '/* BRANDO CINEMATIC LUXURY v0.6.0 START */'
CSS_END = '/* BRANDO CINEMATIC LUXURY v0.6.0 END */'
JS_START = '/* BRANDO CINEMATIC HERO v0.6.0 START */'
JS_END = '/* BRANDO CINEMATIC HERO v0.6.0 END */'

if len(sys.argv) != 2:
    raise SystemExit('Usage: apply-direct.py /absolute/path/to/brando')

theme = Path(sys.argv[1]).resolve()
required = [
    'style.css','functions.php','header.php','front-page.php','footer.php',
    'assets/css/luxury-v3.css','assets/js/luxury-motion.js'
]
missing = [x for x in required if not (theme / x).is_file()]
if missing:
    raise SystemExit('Missing theme files: ' + ', '.join(missing))

def read(rel):
    return (theme / rel).read_text(encoding='utf-8')

def write_atomic(rel, text):
    p = theme / rel
    t = p.with_suffix(p.suffix + '.tmp-brando-060')
    t.write_text(text, encoding='utf-8')
    t.replace(p)

style, functions, header, front, footer, css, js = [read(x) for x in required]

# Exact approved baseline protection.
if 'BRANDO LUXURY SIGNATURE v0.5.7' not in css:
    raise SystemExit('Expected v0.5.7 signature baseline not found')
if 'BRANDO DEMO ART DIRECTION v0.5.5' not in js:
    raise SystemExit('Expected v0.5.5 art direction baseline not found')
if 'IntersectionObserver' not in js or 'scrollIntoView' not in js:
    raise SystemExit('Existing motion system is incomplete')

# Preserve homepage architecture/order and locale protections.
markers = [
    'class="brando-hero"','id="categories"','id="best-sellers"',
    'class="brando-promo"','class="brando-new-arrivals"'
]
pos = [front.find(x) for x in markers]
if any(x < 0 for x in pos) or pos != sorted(pos):
    raise SystemExit('Homepage structure/order check failed')
if any(x not in footer for x in ['brando-trust','brando-newsletter','brando-footer']):
    raise SystemExit('Footer structure check failed')
for bad in ['999 ر.س','WELCOME10','+966','brando.sa']:
    if bad in header + '\n' + front + '\n' + footer:
        raise SystemExit('Forbidden locale token returned: ' + bad)

style_new, n = re.subn(r'(?m)^Version:\s*[^\r\n]+$', f'Version: {VERSION}', style, count=1)
if n != 1:
    raise SystemExit('Could not update style version')
functions_new, n = re.subn(
    r"define\('BRANDO_THEME_VERSION',\s*'[^']+'\);",
    f"define('BRANDO_THEME_VERSION', '{VERSION}');",
    functions,
    count=1,
)
if n != 1:
    raise SystemExit('Could not update theme constant')

css = re.sub(re.escape(CSS_START) + r'.*?' + re.escape(CSS_END), '', css, flags=re.S).rstrip() + '\n\n'
js = re.sub(re.escape(JS_START) + r'.*?' + re.escape(JS_END), '', js, flags=re.S).rstrip() + '\n\n'

css_layer = r'''/* BRANDO CINEMATIC LUXURY v0.6.0 START */
:root{
  --br-cinema-ink:#070807;
  --br-cinema-copper:#8f4821;
  --br-cinema-copper-soft:#b86d3e;
  --br-cinema-paper:#f7f1e8;
  --br-cinema-line:rgba(104,75,51,.14);
}

/* Header: quieter at top, glass luxury after scroll. */
.brando-header{
  position:sticky!important;top:0;z-index:990!important;
  background:rgba(7,8,8,.94)!important;
  border-bottom:1px solid rgba(184,109,62,.08)!important;
  box-shadow:none!important;
  transition:background .35s ease,box-shadow .35s ease,backdrop-filter .35s ease!important;
}
.admin-bar .brando-header{top:32px}
.brando-header.is-scrolled{
  background:rgba(7,8,8,.82)!important;
  backdrop-filter:blur(18px) saturate(1.15)!important;
  -webkit-backdrop-filter:blur(18px) saturate(1.15)!important;
  box-shadow:0 18px 52px rgba(0,0,0,.24)!important;
}
.brando-brand__text strong{letter-spacing:-.045em!important}
.site-nav__menu>li>a{font-weight:680!important}

/* Real cinematic hero: three layered scenes, crossfade + Ken Burns. */
.brando-hero__frame{min-height:700px!important;background:#050606!important}
.brando-hero__media.brando-cinematic-ready{
  min-height:700px!important;background-image:none!important;filter:none!important;animation:none!important;overflow:hidden!important;
}
.brando-hero-scene{
  position:absolute;inset:-2.5%;z-index:0;opacity:0;
  background-size:cover;background-repeat:no-repeat;background-position:center;
  transform:scale(1.035);will-change:opacity,transform;
  transition:opacity 1.45s cubic-bezier(.22,.61,.36,1);
}
.brando-hero-scene::after{
  content:"";position:absolute;inset:0;
  background:
    linear-gradient(90deg,rgba(3,3,3,.04) 0%,rgba(4,4,4,.10) 42%,rgba(4,4,4,.46) 68%,rgba(4,4,4,.92) 100%),
    linear-gradient(180deg,rgba(0,0,0,.03),rgba(0,0,0,.20));
}
.brando-hero-scene.is-active{opacity:1;z-index:1}
.brando-hero-scene.scene-a.is-active{animation:brandoCinemaA 7.4s ease-out both}
.brando-hero-scene.scene-b.is-active{animation:brandoCinemaB 7.4s ease-out both}
.brando-hero-scene.scene-c.is-active{animation:brandoCinemaC 7.4s ease-out both}
.brando-hero__content{min-height:700px!important;z-index:4!important;background:linear-gradient(90deg,rgba(4,4,4,0),rgba(4,4,4,.18) 28%,rgba(4,4,4,.68) 72%,rgba(4,4,4,.95) 100%)!important}
.brando-hero__content.is-cinema-refreshing{animation:brandoCinemaCopy .78s cubic-bezier(.2,.7,.2,1)}
.brando-hero__title{font-size:clamp(64px,5.65vw,92px)!important;line-height:.98!important}
.brando-hero__lead{font-size:16px!important;max-width:520px!important;color:#d5d0ca!important}
.brando-hero__cta{background:var(--br-cinema-copper)!important;border-radius:4px!important;box-shadow:0 18px 44px rgba(143,72,33,.22)!important}
.brando-hero__dots{display:flex!important;align-items:center!important;gap:8px!important;z-index:7!important;bottom:28px!important}
.brando-hero__dots span{width:7px!important;height:7px!important;border-radius:999px!important;background:rgba(255,255,255,.48)!important;cursor:pointer;transition:width .3s ease,background .3s ease,opacity .3s ease!important}
.brando-hero__dots span.is-active{width:34px!important;background:var(--br-cinema-copper-soft)!important;animation:none!important}
.brando-hero-progress{position:absolute;z-index:7;left:0;right:0;bottom:0;height:2px;background:rgba(255,255,255,.08);overflow:hidden}
.brando-hero-progress::after{content:"";display:block;width:100%;height:100%;background:linear-gradient(90deg,transparent,var(--br-cinema-copper-soft));transform:translateX(-100%)}
.brando-hero-progress.is-running::after{animation:brandoCinemaProgress 6.5s linear forwards}

/* Collection gallery: same six categories, less UI and more image. */
.brando-category-card{border-radius:3px!important;box-shadow:0 18px 52px rgba(17,13,10,.095)!important}
.brando-category-card__media{aspect-ratio:4/5.25!important}
.brando-category-card__media img{transition:transform .8s cubic-bezier(.2,.7,.2,1),filter .45s ease!important}
.brando-category-card:hover .brando-category-card__media img{transform:scale(1.07)!important}
.brando-category-card__icon{opacity:.65;transform:translateY(4px);transition:opacity .3s ease,transform .3s ease!important}
.brando-category-card:hover .brando-category-card__icon{opacity:1;transform:none}

/* Best Sellers: luxury retail language instead of boxed Woo cards. */
.brando-best-sellers__grid{gap:34px!important}
.brando-product-card{background:transparent!important;border:0!important;box-shadow:none!important;overflow:visible!important}
.brando-product-card:hover{transform:none!important;box-shadow:none!important}
.brando-product-card__media{border-radius:3px!important;box-shadow:0 20px 52px rgba(18,14,10,.10)!important;transition:box-shadow .35s ease,transform .35s ease!important}
.brando-product-card:hover .brando-product-card__media{transform:translateY(-5px);box-shadow:0 34px 78px rgba(18,14,10,.15)!important}
.brando-product-card__content{background:transparent!important;padding:20px 4px 0!important;min-height:156px!important}
.brando-product-card__name{font-size:17px!important;font-weight:730!important;min-height:44px!important}
.brando-product-card__rating{opacity:.2!important;margin-top:3px!important}
.brando-product-card__price{font-size:20px!important;font-weight:880!important}
.brando-product-card__cart,.brando-product-card .button,.brando-product-card .add_to_cart_button{
  min-height:auto!important;padding:7px 0 6px!important;border:0!important;border-bottom:1px solid rgba(17,16,14,.58)!important;border-radius:0!important;
  background:transparent!important;color:#151411!important;font-size:10.5px!important;font-weight:800!important;
}
.brando-product-card__cart:hover,.brando-product-card .button:hover,.brando-product-card .add_to_cart_button:hover{background:transparent!important;color:var(--br-cinema-copper)!important;border-bottom-color:var(--br-cinema-copper)!important}
.brando-product-card__wishlist{background:rgba(8,8,7,.58)!important;color:#fff!important;border-color:rgba(255,255,255,.22)!important;backdrop-filter:blur(8px)}

/* Promo: luxury campaign reveal + subtle living image. */
.brando-promo__card{position:relative!important;overflow:hidden!important}
.brando-promo__visual{transform:translate3d(0,var(--br-promo-y,0px),0) scale(1.045);transition:transform .12s linear!important;will-change:transform}
.brando-promo__card::after{content:"";position:absolute;z-index:5;top:-30%;bottom:-30%;width:24%;left:-32%;transform:skewX(-16deg);background:linear-gradient(90deg,transparent,rgba(255,255,255,.10),transparent);pointer-events:none}
.brando-promo__card.is-visible::after{animation:brandoCinemaSweep 1.45s .35s ease-out both}
.brando-promo__badge{opacity:.78!important}

/* New arrivals: editorial and lighter than Best Sellers. */
.brando-new-arrivals .woocommerce ul.products li.product{background:transparent!important;border:0!important;box-shadow:none!important;overflow:visible!important}
.brando-new-arrivals .woocommerce ul.products li.product:hover{transform:none!important;box-shadow:none!important}
.brando-new-arrivals .woocommerce ul.products li.product a img{border-radius:2px!important;box-shadow:0 14px 38px rgba(18,14,10,.07)!important;transition:transform .55s ease,box-shadow .35s ease!important}
.brando-new-arrivals .woocommerce ul.products li.product:hover a img{transform:translateY(-4px) scale(1.015)!important;box-shadow:0 25px 58px rgba(18,14,10,.11)!important}
.brando-new-arrivals .woocommerce ul.products li.product .woocommerce-loop-product__title,.brando-new-arrivals .woocommerce ul.products li.product .price{padding-inline:2px!important;margin-inline:2px!important}
.brando-new-arrivals .woocommerce ul.products li.product .button,.brando-new-arrivals .woocommerce ul.products li.product .add_to_cart_button{margin-inline:2px!important;background:transparent!important;border:0!important;border-bottom:1px solid rgba(35,31,27,.45)!important;border-radius:0!important;color:#24211d!important;padding-inline:0!important}

/* Trust + dark ending: restrained, branded, editorial. */
.brando-trust__inner{max-width:1420px!important}.brando-trust__item{padding-block:36px!important}.brando-trust__item h3{letter-spacing:-.015em!important}
.brando-newsletter__inner{border-radius:4px!important;background:radial-gradient(circle at 88% 8%,rgba(143,72,33,.10),transparent 24%),linear-gradient(135deg,#060707,#111212)!important}
.brando-newsletter__form{border:0!important;border-bottom:1px solid rgba(255,255,255,.22)!important;border-radius:0!important;background:transparent!important;padding:0!important}
.brando-newsletter__form input{padding-inline:4px!important}
.brando-newsletter__form button{border-radius:2px!important;background:var(--br-cinema-copper)!important}
.brando-footer__brand-name{font-size:46px!important;color:var(--br-cinema-copper-soft)!important}
.brando-footer__social a{transition:transform .25s ease,border-color .25s ease,color .25s ease!important}.brando-footer__social a:hover{transform:translateY(-2px)}

@keyframes brandoCinemaA{from{transform:scale(1.08) translate3d(0,0,0)}to{transform:scale(1.015) translate3d(-1.2%,.8%,0)}}
@keyframes brandoCinemaB{from{transform:scale(1.04) translate3d(-1.4%,0,0)}to{transform:scale(1.10) translate3d(1.1%,-.6%,0)}}
@keyframes brandoCinemaC{from{transform:scale(1.09) translate3d(.8%,-.8%,0)}to{transform:scale(1.025) translate3d(-.8%,.4%,0)}}
@keyframes brandoCinemaCopy{0%{opacity:.58;transform:translateY(12px)}100%{opacity:1;transform:none}}
@keyframes brandoCinemaProgress{to{transform:translateX(0)}}
@keyframes brandoCinemaSweep{from{left:-32%}to{left:118%}}

@media(max-width:980px){
  .admin-bar .brando-header{top:46px}
  .brando-hero__frame,.brando-hero__media.brando-cinematic-ready{min-height:0!important}
  .brando-hero__media.brando-cinematic-ready{min-height:390px!important}
  .brando-hero__content{min-height:0!important}
  .brando-hero-scene::after{background:linear-gradient(180deg,rgba(0,0,0,.04),rgba(0,0,0,.25))}
  .brando-promo__visual{transform:scale(1.03)!important}
}
@media(max-width:720px){
  .brando-hero__media.brando-cinematic-ready{min-height:310px!important}
  .brando-hero__title{font-size:48px!important}
  .brando-best-sellers__grid{gap:22px!important}
}
@media(prefers-reduced-motion:reduce){
  .brando-hero-scene.is-active,.brando-hero-progress::after,.brando-promo__card.is-visible::after{animation:none!important}
  .brando-hero-scene{transition:none!important}.brando-promo__visual{transform:none!important}
}
/* BRANDO CINEMATIC LUXURY v0.6.0 END */'''

js_layer = r'''/* BRANDO CINEMATIC HERO v0.6.0 START */
(() => {
  'use strict';

  const ready = () => {
    const hero = document.querySelector('.brando-hero');
    const media = hero ? hero.querySelector('.brando-hero__media') : null;
    const content = hero ? hero.querySelector('.brando-hero__content') : null;
    const dotsWrap = hero ? hero.querySelector('.brando-hero__dots') : null;
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (hero && media && !media.dataset.brandoCinema060) {
      const scenes = [
        ['scene-a','https://images.unsplash.com/photo-1771270731051-9cfbb7222946?auto=format&fit=crop&fm=jpg&q=88&w=2100','center 46%'],
        ['scene-b','https://images.unsplash.com/photo-1556910602-38f53e68e15d?auto=format&fit=crop&fm=jpg&q=88&w=2100','center 52%'],
        ['scene-c','https://images.unsplash.com/photo-1600566753086-00f18fb6b3ea?auto=format&fit=crop&fm=jpg&q=88&w=2100','center 48%']
      ];

      scenes.forEach((scene, index) => {
        const preload = new Image(); preload.src = scene[1];
        const el = document.createElement('span');
        el.className = `brando-hero-scene ${scene[0]}${index === 0 ? ' is-active' : ''}`;
        el.style.backgroundImage = `url("${scene[1]}")`;
        el.style.backgroundPosition = scene[2];
        el.setAttribute('aria-hidden','true');
        media.prepend(el);
      });

      media.dataset.brandoCinema060 = 'yes';
      media.classList.add('brando-cinematic-ready');

      const progress = document.createElement('span');
      progress.className = 'brando-hero-progress';
      progress.setAttribute('aria-hidden','true');
      media.appendChild(progress);

      let dots = dotsWrap ? Array.from(dotsWrap.querySelectorAll('span')).slice(0,3) : [];
      if (dotsWrap && dots.length < 3) {
        dotsWrap.innerHTML = '<span></span><span></span><span></span>';
        dots = Array.from(dotsWrap.querySelectorAll('span'));
      }
      dots.forEach((dot, index) => {
        dot.classList.toggle('is-active', index === 0);
        dot.setAttribute('role','button');
        dot.setAttribute('tabindex','0');
        dot.setAttribute('aria-label', `المشهد ${index + 1} من 3`);
      });

      const sceneEls = Array.from(media.querySelectorAll('.brando-hero-scene'));
      let current = 0, timer = null, pointerX = null;
      const interval = 6500;

      const resetProgress = () => {
        progress.classList.remove('is-running');
        void progress.offsetWidth;
        if (!reduce && !document.hidden) progress.classList.add('is-running');
      };

      const refreshCopy = () => {
        if (!content || reduce) return;
        content.classList.remove('is-cinema-refreshing');
        void content.offsetWidth;
        content.classList.add('is-cinema-refreshing');
        window.setTimeout(() => content.classList.remove('is-cinema-refreshing'), 850);
      };

      const activate = (index) => {
        current = (index + sceneEls.length) % sceneEls.length;
        sceneEls.forEach((el, i) => el.classList.toggle('is-active', i === current));
        dots.forEach((el, i) => {
          el.classList.toggle('is-active', i === current);
          el.setAttribute('aria-current', i === current ? 'true' : 'false');
        });
        refreshCopy(); resetProgress();
      };

      const stop = () => { if (timer) { window.clearInterval(timer); timer = null; } progress.classList.remove('is-running'); };
      const start = () => {
        stop();
        if (reduce || document.hidden) return;
        resetProgress();
        timer = window.setInterval(() => activate(current + 1), interval);
      };

      dots.forEach((dot, index) => {
        const choose = () => { activate(index); start(); };
        dot.addEventListener('click', choose);
        dot.addEventListener('keydown', (event) => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); choose(); } });
      });

      media.addEventListener('pointerdown', (event) => { pointerX = event.clientX; }, {passive:true});
      media.addEventListener('pointerup', (event) => {
        if (pointerX === null) return;
        const dx = event.clientX - pointerX; pointerX = null;
        if (Math.abs(dx) < 48) return;
        activate(current + (dx < 0 ? 1 : -1)); start();
      }, {passive:true});
      hero.addEventListener('mouseenter', stop);
      hero.addEventListener('mouseleave', start);
      hero.addEventListener('focusin', stop);
      hero.addEventListener('focusout', start);
      document.addEventListener('visibilitychange', () => document.hidden ? stop() : start());
      activate(0); start();
    }

    const header = document.querySelector('.brando-header');
    const promo = document.querySelector('.brando-promo__visual');
    let ticking = false;
    const renderScroll = () => {
      ticking = false;
      if (header) header.classList.toggle('is-scrolled', window.scrollY > 42);
      if (promo && !reduce) {
        const rect = promo.getBoundingClientRect();
        const vh = window.innerHeight || 1;
        if (rect.bottom > 0 && rect.top < vh) {
          const p = ((rect.top + rect.height / 2) - vh / 2) / vh;
          promo.style.setProperty('--br-promo-y', `${Math.max(-14, Math.min(14, p * -18)).toFixed(2)}px`);
        }
      }
    };
    const onScroll = () => { if (!ticking) { ticking = true; window.requestAnimationFrame(renderScroll); } };
    renderScroll();
    window.addEventListener('scroll', onScroll, {passive:true});
    window.addEventListener('resize', onScroll, {passive:true});
  };

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', ready, {once:true});
  else ready();
})();
/* BRANDO CINEMATIC HERO v0.6.0 END */'''

write_atomic('style.css', style_new)
write_atomic('functions.php', functions_new)
write_atomic('assets/css/luxury-v3.css', css + css_layer + '\n')
write_atomic('assets/js/luxury-motion.js', js + js_layer + '\n')

print('PATCH_VERSION=0.6.0')
print('LAYOUT_STRUCTURE_CHANGED=NO')
print('SECTION_ORDER_CHANGED=NO')
print('TEMPLATES_CHANGED=NO')
print('WOOCOMMERCE_DATA_CHANGED=NO')
print('DEMO_ART_DIRECTION_PRESERVED=YES')
print('HERO_RUNTIME_SCENES=3')
print('HERO_CROSSFADE=YES')
print('HERO_KEN_BURNS=YES')
print('HERO_AUTOPLAY=YES')
print('HERO_DOTS_INTERACTIVE=YES')
print('HERO_SWIPE_SUPPORT=YES')
print('HERO_VISIBILITY_PAUSE=YES')
print('REDUCED_MOTION_SUPPORTED=YES')
print('HEADER_GLASS_SCROLL=YES')
print('PROMO_PARALLAX=YES')
print('PRODUCT_CARD_LANGUAGE_UPGRADED=YES')
print('NEWSLETTER_FOOTER_DARK_LUXURY=YES')
print('MOTION_SYSTEM_PRESERVED=YES')
