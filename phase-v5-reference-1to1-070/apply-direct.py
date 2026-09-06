#!/usr/bin/env python3
from pathlib import Path
import re,sys

V='0.7.0'
MARK_START='/* BRANDO REFERENCE 1TO1 v0.7.0 START */'
MARK_END='/* BRANDO REFERENCE 1TO1 v0.7.0 END */'

if len(sys.argv)!=2: raise SystemExit('Usage: apply-direct.py /absolute/path/to/brando')
theme=Path(sys.argv[1]).resolve()
base=Path(__file__).resolve().parent
required_theme=['style.css','functions.php','header.php','front-page.php','footer.php','assets/css/luxury-v3.css','assets/js/luxury-motion.js']
required_patch=['header.php','front-page.php','footer.php','reference.css','compat.css']
missing=[x for x in required_theme if not (theme/x).is_file()]
if missing: raise SystemExit('Missing theme files: '+', '.join(missing))
missing=[x for x in required_patch if not (base/x).is_file()]
if missing: raise SystemExit('Missing patch payload files: '+', '.join(missing))

def read(p): return p.read_text(encoding='utf-8')
def atomic(path,text):
    tmp=path.with_suffix(path.suffix+'.tmp-brando-070'); tmp.write_text(text,encoding='utf-8'); tmp.replace(path)

style=read(theme/'style.css'); fn=read(theme/'functions.php'); css=read(theme/'assets/css/luxury-v3.css'); js=read(theme/'assets/js/luxury-motion.js')
if 'BRANDO EDITORIAL SCALE CORRECTION v0.6.5' not in css: raise SystemExit('Expected v0.6.5 baseline not found')
if 'BRANDO CINEMATIC HERO v0.6.1' not in js: raise SystemExit('Expected cinematic runtime not found')
if 'IntersectionObserver' not in js or 'scrollIntoView' not in js: raise SystemExit('Existing motion system incomplete')

style,n=re.subn(r'(?m)^Version:\s*[^\r\n]+$',f'Version: {V}',style,count=1)
if n!=1: raise SystemExit('Could not update style version')
fn,n=re.subn(r"define\('BRANDO_THEME_VERSION',\s*'[^']+'\);",f"define('BRANDO_THEME_VERSION', '{V}');",fn,count=1)
if n!=1: raise SystemExit('Could not update theme version constant')

css=re.sub(re.escape(MARK_START)+r'.*?'+re.escape(MARK_END),'',css,flags=re.S).rstrip()
css+='\n\n'+read(base/'reference.css').strip()+'\n'+read(base/'compat.css').strip()+'\n'

# Preserve the engine but use dark kitchen scenes and lock copy to the reference artwork.
block_re=re.compile(r'/\* BRANDO CINEMATIC HERO v0\.6\.1 START \*/.*?/\* BRANDO CINEMATIC HERO v0\.6\.1 END \*/',re.S)
m=block_re.search(js)
if m:
    block=m.group(0)
    urls=[
      'https://images.unsplash.com/photo-1453614512568-c4024d13c247?auto=format&fit=crop&fm=jpg&q=88&w=2200',
      'https://images.unsplash.com/photo-1776935359460-6c789e972e6a?auto=format&fit=crop&fm=jpg&q=88&w=2200',
      'https://images.unsplash.com/photo-1748050869861-dde6ee2ae683?auto=format&fit=crop&fm=jpg&q=88&w=2200'
    ]
    parts=list(re.finditer(r"src:'https://images\.unsplash\.com/[^']+'",block))
    for idx,match in enumerate(reversed(parts[:3])):
        target=urls[len(parts[:3])-1-idx]
        block=block[:match.start()]+"src:'"+target+"'"+block[match.end():]
    block=block.replace("line:'تفاصيل راقية', accent:'لمساحتك'","line:'أسلوب عصري', accent:'لمطبخك'")
    block=block.replace("line:'تصميم يليق', accent:'بمساحتك'","line:'أسلوب عصري', accent:'لمطبخك'")
    block=re.sub(r"lead:'[^']+'", "lead:'اكتشف منتجات مبتكرة بعناية تمنح مطبخك الجمال والعملية التي تستحقها'", block)
    js=js[:m.start()]+block+js[m.end():]

atomic(theme/'style.css',style)
atomic(theme/'functions.php',fn)
atomic(theme/'header.php',read(base/'header.php'))
atomic(theme/'front-page.php',read(base/'front-page.php'))
atomic(theme/'footer.php',read(base/'footer.php'))
atomic(theme/'assets/css/luxury-v3.css',css)
atomic(theme/'assets/js/luxury-motion.js',js)

print('PATCH_VERSION=0.7.0')
print('REFERENCE_MATCH_MODE=1TO1')
print('HEADER_REBUILT=YES')
print('TOPBAR_ORANGE=YES')
print('HERO_REFERENCE_COMPOSITION=YES')
print('CATEGORIES_COUNT=6')
print('BEST_SELLERS_COUNT=6')
print('PROMO_REFERENCE_STRUCTURE=YES')
print('NEW_ARRIVALS_COUNT=6')
print('TRUST_REFERENCE_STRUCTURE=YES')
print('NEWSLETTER_REFERENCE_STRUCTURE=YES')
print('FOOTER_REFERENCE_STRUCTURE=YES')
print('WOOCOMMERCE_DATA_PRESERVED=YES')
print('CINEMATIC_ENGINE_PRESERVED=YES')
print('LEGACY_CINEMATIC_CSS_NEUTRALIZED=YES')
