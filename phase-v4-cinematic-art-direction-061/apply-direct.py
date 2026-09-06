#!/usr/bin/env python3
from pathlib import Path
import re, sys

VERSION = '0.6.1'
CSS_START = '/* BRANDO CINEMATIC ART DIRECTION v0.6.1 START */'
CSS_END = '/* BRANDO CINEMATIC ART DIRECTION v0.6.1 END */'
JS060_START = '/* BRANDO CINEMATIC HERO v0.6.0 START */'
JS060_END = '/* BRANDO CINEMATIC HERO v0.6.0 END */'
JS_START = '/* BRANDO CINEMATIC HERO v0.6.1 START */'
JS_END = '/* BRANDO CINEMATIC HERO v0.6.1 END */'

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
    t = p.with_suffix(p.suffix + '.tmp-brando-061')
    t.write_text(text, encoding='utf-8')
    t.replace(p)

style, functions, header, front, footer, css, js = [read(x) for x in required]

# Require exact cinematic baseline and preserve all approved architecture/data protections.
if 'BRANDO CINEMATIC LUXURY v0.6.0' not in css:
    raise SystemExit('Expected v0.6.0 cinematic CSS baseline not found')
if JS060_START not in js and JS_START not in js:
    raise SystemExit('Expected v0.6.0/0.6.1 cinematic JS baseline not found')
if 'BRANDO DEMO ART DIRECTION v0.5.5' not in js:
    raise SystemExit('Expected v0.5.5 demo art direction baseline not found')
if 'IntersectionObserver' not in js or 'scrollIntoView' not in js:
    raise SystemExit('Existing motion system is incomplete')

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

# Idempotent 0.6.1 CSS overlay.
css = re.sub(re.escape(CSS_START) + r'.*?' + re.escape(CSS_END), '', css, flags=re.S).rstrip() + '\n\n'

# Replace the 0.6.0 cinematic runtime completely; keep earlier reveal/smooth-scroll/demo-art code intact.
js = re.sub(re.escape(JS060_START) + r'.*?' + re.escape(JS060_END), '', js, flags=re.S)
js = re.sub(re.escape(JS_START) + r'.*?' + re.escape(JS_END), '', js, flags=re.S).rstrip() + '\n\n'

css_layer = r'''/* BRANDO CINEMATIC ART DIRECTION v0.6.1 START */
/* Three scenes now share one dark/warm luxury-kitchen world. */
.brando-hero-scene{
  filter:saturate(.74) contrast(1.08) brightness(.84);
  transition:opacity 1.05s cubic-bezier(.22,.61,.36,1)!important;
}
.brando-hero-scene::before{
  content:"";position:absolute;inset:0;z-index:1;pointer-events:none;
  background:linear-gradient(120deg,rgba(115,58,27,.055),transparent 34%,rgba(0,0,0,.08));
  mix-blend-mode:soft-light;
}
.brando-hero-scene::after{
  z-index:2!important;
  background:
    linear-gradient(90deg,rgba(2,3,3,.03) 0%,rgba(3,3,3,.08) 38%,rgba(3,3,3,.42) 65%,rgba(3,3,3,.91) 100%),
    linear-gradient(180deg,rgba(0,0,0,.03),rgba(0,0,0,.22))!important;
}
.brando-hero-scene.scene-a{filter:saturate(.72) contrast(1.10) brightness(.82)}
.brando-hero-scene.scene-b{filter:saturate(.68) contrast(1.09) brightness(.78)}
.brando-hero-scene.scene-c{filter:saturate(.66) contrast(1.07) brightness(.80)}
.brando-hero-scene.scene-a.is-active{animation:brandoCinema061A 7.1s cubic-bezier(.16,.7,.2,1) both!important}
.brando-hero-scene.scene-b.is-active{animation:brandoCinema061B 7.1s cubic-bezier(.16,.7,.2,1) both!important}
.brando-hero-scene.scene-c.is-active{animation:brandoCinema061C 7.1s cubic-bezier(.16,.7,.2,1) both!important}
.brando-hero__content{
  background:linear-gradient(90deg,rgba(4,4,4,0),rgba(4,4,4,.14) 24%,rgba(4,4,4,.62) 68%,rgba(4,4,4,.94) 100%)!important;
}
.brando-hero__content.is-cinema-refreshing{animation:brandoCinema061Copy .68s cubic-bezier(.2,.7,.2,1)!important}
.brando-header.is-scrolled{
  background:rgba(7,8,8,.74)!important;
  backdrop-filter:blur(22px) saturate(1.18)!important;
  -webkit-backdrop-filter:blur(22px) saturate(1.18)!important;
  border-bottom-color:rgba(184,109,62,.16)!important;
  box-shadow:0 18px 56px rgba(0,0,0,.27)!important;
}
.brando-hero__dots span{opacity:.72!important}.brando-hero__dots span.is-active{opacity:1!important}

@keyframes brandoCinema061A{
  from{transform:scale(1.12) translate3d(.4%,-.4%,0)}
  to{transform:scale(1.02) translate3d(-1.6%,1%,0)}
}
@keyframes brandoCinema061B{
  from{transform:scale(1.055) translate3d(-2%,.4%,0)}
  to{transform:scale(1.125) translate3d(1.3%,-.9%,0)}
}
@keyframes brandoCinema061C{
  from{transform:scale(1.13) translate3d(1.1%,-1%,0)}
  to{transform:scale(1.025) translate3d(-1.2%,.7%,0)}
}
@keyframes brandoCinema061Copy{0%{opacity:.45;transform:translateY(16px)}100%{opacity:1;transform:none}}

@media(max-width:980px){
  .brando-hero-scene{filter:saturate(.72) contrast(1.06) brightness(.86)}
  .brando-hero-scene::after{background:linear-gradient(180deg,rgba(0,0,0,.05),rgba(0,0,0,.30))!important}
}
@media(prefers-reduced-motion:reduce){
  .brando-hero-scene.is-active{animation:none!important;transform:scale(1.02)!important}
  .brando-hero-scene{transition:none!important}
}
/* BRANDO CINEMATIC ART DIRECTION v0.6.1 END */'''

js_layer = r'''/* BRANDO CINEMATIC HERO v0.6.1 START */
(() => {
  'use strict';

  const ready = () => {
    const hero = document.querySelector('.brando-hero');
    const media = hero ? hero.querySelector('.brando-hero__media') : null;
    const content = hero ? hero.querySelector('.brando-hero__content') : null;
    const dotsWrap = hero ? hero.querySelector('.brando-hero__dots') : null;
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (hero && media && !media.dataset.brandoCinema061) {
      const scenes = [
        {
          cls:'scene-a',
          src:'https://images.unsplash.com/photo-1771270731051-9cfbb7222946?auto=format&fit=crop&fm=jpg&q=90&w=2200',
          pos:'center 46%',
          line:'أسلوب عصري', accent:'لمطبخك',
          lead:'اكتشف منتجات مختارة بعناية تمنح مطبخك العملية والأناقة التي تستحقها.'
        },
        {
          cls:'scene-b',
          src:'https://images.unsplash.com/photo-1765766601532-90e9b96320c8?auto=format&fit=crop&fm=jpg&q=90&w=2200',
          pos:'center 51%',
          line:'تفاصيل راقية', accent:'لمساحتك',
          lead:'خامات دافئة وتكوينات متوازنة تمنح المطبخ حضورًا هادئًا وفخامة تدوم.'
        },
        {
          cls:'scene-c',
          src:'https://images.unsplash.com/photo-1769326541248-5e09a8ace25b?auto=format&fit=crop&fm=jpg&q=90&w=2200',
          pos:'center 50%',
          line:'تصميم يليق', accent:'بمساحتك',
          lead:'اختيارات عصرية تجمع بين الجمال والعملية لتصنع مطبخًا أكثر حضورًا كل يوم.'
        }
      ];

      const titleLine = content ? content.querySelector('.brando-hero__title span') : null;
      const titleAccent = content ? content.querySelector('.brando-hero__title strong') : null;
      const lead = content ? content.querySelector('.brando-hero__lead') : null;

      const preloadTasks = scenes.map((scene) => {
        const img = new Image();
        img.decoding = 'async'; img.src = scene.src;
        if (typeof img.decode === 'function') return img.decode().catch(() => null);
        return new Promise((resolve) => { img.onload = img.onerror = resolve; });
      });

      scenes.forEach((scene) => {
        const el = document.createElement('span');
        el.className = `brando-hero-scene ${scene.cls}`;
        el.style.backgroundImage = `url("${scene.src}")`;
        el.style.backgroundPosition = scene.pos;
        el.setAttribute('aria-hidden','true');
        media.prepend(el);
      });

      media.dataset.brandoCinema061 = 'yes';
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
        dot.setAttribute('role','button'); dot.setAttribute('tabindex','0');
        dot.setAttribute('aria-label', `المشهد ${index + 1} من 3`);
      });

      const sceneEls = Array.from(media.querySelectorAll('.brando-hero-scene'));
      let current = 0, timer = null, pointerX = null, readyToRun = false;
      const interval = 6500;

      const resetProgress = () => {
        progress.classList.remove('is-running'); void progress.offsetWidth;
        if (readyToRun && !reduce && !document.hidden) progress.classList.add('is-running');
      };
      const refreshCopy = () => {
        const scene = scenes[current];
        if (titleLine) titleLine.textContent = scene.line;
        if (titleAccent) titleAccent.textContent = scene.accent;
        if (lead) lead.textContent = scene.lead;
        if (!content || reduce) return;
        content.classList.remove('is-cinema-refreshing'); void content.offsetWidth;
        content.classList.add('is-cinema-refreshing');
        window.setTimeout(() => content.classList.remove('is-cinema-refreshing'), 760);
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
      const stop = () => {
        if (timer) { window.clearInterval(timer); timer = null; }
        progress.classList.remove('is-running');
      };
      const start = () => {
        stop();
        if (!readyToRun || reduce || document.hidden) return;
        resetProgress(); timer = window.setInterval(() => activate(current + 1), interval);
      };

      dots.forEach((dot, index) => {
        const choose = () => { activate(index); start(); };
        dot.addEventListener('click', choose);
        dot.addEventListener('keydown', (event) => {
          if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); choose(); }
        });
      });
      media.addEventListener('pointerdown', (event) => { pointerX = event.clientX; }, {passive:true});
      media.addEventListener('pointerup', (event) => {
        if (pointerX === null) return;
        const dx = event.clientX - pointerX; pointerX = null;
        if (Math.abs(dx) < 48) return;
        activate(current + (dx < 0 ? 1 : -1)); start();
      }, {passive:true});
      hero.addEventListener('mouseenter', stop); hero.addEventListener('mouseleave', start);
      hero.addEventListener('focusin', stop); hero.addEventListener('focusout', start);
      document.addEventListener('visibilitychange', () => document.hidden ? stop() : start());

      Promise.allSettled(preloadTasks).then(() => {
        readyToRun = true;
        media.classList.add('brando-cinematic-ready');
        activate(0); start();
      });
    }

    const header = document.querySelector('.brando-header');
    const promo = document.querySelector('.brando-promo__visual');
    let ticking = false;
    const renderScroll = () => {
      ticking = false;
      if (header) header.classList.toggle('is-scrolled', window.scrollY > 34);
      if (promo && !reduce) {
        const rect = promo.getBoundingClientRect(); const vh = window.innerHeight || 1;
        if (rect.bottom > 0 && rect.top < vh) {
          const p = ((rect.top + rect.height / 2) - vh / 2) / vh;
          promo.style.setProperty('--br-promo-y', `${Math.max(-16, Math.min(16, p * -21)).toFixed(2)}px`);
        }
      }
    };
    const onScroll = () => { if (!ticking) { ticking = true; window.requestAnimationFrame(renderScroll); } };
    renderScroll(); window.addEventListener('scroll', onScroll, {passive:true}); window.addEventListener('resize', onScroll, {passive:true});
  };

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', ready, {once:true});
  else ready();
})();
/* BRANDO CINEMATIC HERO v0.6.1 END */'''

write_atomic('style.css', style_new)
write_atomic('functions.php', functions_new)
write_atomic('assets/css/luxury-v3.css', css + css_layer + '\n')
write_atomic('assets/js/luxury-motion.js', js + js_layer + '\n')

print('PATCH_VERSION=0.6.1')
print('LAYOUT_STRUCTURE_CHANGED=NO')
print('SECTION_ORDER_CHANGED=NO')
print('TEMPLATES_CHANGED=NO')
print('WOOCOMMERCE_DATA_CHANGED=NO')
print('DEMO_ART_DIRECTION_PRESERVED=YES')
print('HERO_ART_DIRECTION_LOCK=YES')
print('HERO_SCENES_KITCHEN_ONLY=YES')
print('HERO_RUNTIME_SCENES=3')
print('HERO_CROSSFADE_DURATION_MS=1050')
print('HERO_KEN_BURNS_STRENGTH=ENHANCED')
print('HERO_COPY_ROTATION=YES')
print('HERO_AUTOPLAY_INTERVAL=6500')
print('HERO_PRELOAD_GATE=YES')
print('HEADER_GLASS_STRENGTH=ENHANCED')
print('PROMO_PARALLAX_PRESERVED=YES')
print('MOTION_SYSTEM_PRESERVED=YES')
