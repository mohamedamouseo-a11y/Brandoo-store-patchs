#!/usr/bin/env python3
from pathlib import Path
import re
import shutil
import sys

if len(sys.argv) != 2:
    raise SystemExit("Usage: apply.py /absolute/path/to/wp-content/themes/brando")

theme = Path(sys.argv[1]).resolve()
if not theme.is_dir():
    raise SystemExit(f"Theme directory not found: {theme}")

required = ["style.css", "functions.php", "header.php", "front-page.php", "footer.php"]
missing = [name for name in required if not (theme / name).is_file()]
if missing:
    raise SystemExit("Missing theme files: " + ", ".join(missing))

patch_root = Path(__file__).resolve().parent / "files" / "wp-content" / "themes" / "brando"
css_src = patch_root / "assets" / "css" / "luxury-v3.css"
js_src = patch_root / "assets" / "js" / "luxury-motion.js"
if not css_src.is_file() or not js_src.is_file():
    raise SystemExit("Patch asset files are missing")

files = {name: (theme / name).read_text(encoding="utf-8") for name in required}

style = files["style.css"]
style_new, n = re.subn(r"(?m)^Version:\s*[^\r\n]+$", "Version: 0.5.1", style, count=1)
if n != 1:
    raise SystemExit("Could not update style.css Version")

functions = files["functions.php"]
functions_new, n = re.subn(
    r"define\('BRANDO_THEME_VERSION',\s*'[^']+'\);",
    "define('BRANDO_THEME_VERSION', '0.5.1');",
    functions,
    count=1,
)
if n != 1:
    raise SystemExit("Could not update BRANDO_THEME_VERSION")

luxury_enqueue_pattern = re.compile(
    r"(?m)^\s*wp_enqueue_style\('brando-luxury-(?:pass|v3)',\s*get_template_directory_uri\(\)\s*\.\s*'/assets/css/(?:luxury-pass|luxury-v3)\.css',\s*\['brando-new-arrivals',\s*'brando-footer'\],\s*BRANDO_THEME_VERSION\);\s*$"
)
luxury_line = "        wp_enqueue_style('brando-luxury-v3', get_template_directory_uri() . '/assets/css/luxury-v3.css', ['brando-new-arrivals', 'brando-footer'], BRANDO_THEME_VERSION);"
functions_new, n = luxury_enqueue_pattern.subn(luxury_line, functions_new, count=1)
if n != 1:
    raise SystemExit("Could not replace luxury stylesheet enqueue")

motion_line = "        wp_enqueue_script('brando-luxury-motion', get_template_directory_uri() . '/assets/js/luxury-motion.js', ['brando-header'], BRANDO_THEME_VERSION, true);"
if "brando-luxury-motion" not in functions_new:
    functions_new = functions_new.replace(luxury_line, luxury_line + "\n" + motion_line, 1)

header = files["header.php"]
old_shipping = "<span><?php esc_html_e('شحن مجاني للطلبات فوق 999 ر.س', 'brando'); ?></span>"
new_shipping = "<span><?php esc_html_e('شحن مجاني على الطلبات المؤهلة', 'brando'); ?></span>"
if old_shipping not in header:
    raise SystemExit("Expected Saudi shipping text not found in header.php")
header_new = header.replace(old_shipping, new_shipping, 1)

old_coupon = """<span><?php esc_html_e('خصم 10% على أول طلب — استخدم الكود:', 'brando'); ?></span>
            <strong>WELCOME10</strong>"""
new_coupon = """<span><?php esc_html_e('خصم 10% على أول طلب للعملاء الجدد', 'brando'); ?></span>"""
if old_coupon not in header_new:
    raise SystemExit("Expected WELCOME10 block not found in header.php")
header_new = header_new.replace(old_coupon, new_coupon, 1)

front = files["front-page.php"]
front_new, price_count = re.subn(
    r"('price_text'\s*=>\s*')([0-9]+)\s*ر\.س(')",
    r"\1\2\3",
    front,
)
if price_count < 4:
    raise SystemExit(f"Expected at least 4 hardcoded Saudi demo prices, found {price_count}")

footer = files["footer.php"]
footer_new = footer.replace(
    "<?php bloginfo('name'); ?>",
    "<?php esc_html_e('براندو', 'brando'); ?>",
)

social_replacements = {
    '<a href="#" aria-label="Instagram">IG</a>':
        '<a href="#" aria-label="<?php esc_attr_e(\'إنستغرام\', \'brando\'); ?>"><?php esc_html_e(\'إنستغرام\', \'brando\'); ?></a>',
    '<a href="#" aria-label="TikTok">TT</a>':
        '<a href="#" aria-label="<?php esc_attr_e(\'تيك توك\', \'brando\'); ?>"><?php esc_html_e(\'تيك توك\', \'brando\'); ?></a>',
    '<a href="#" aria-label="X">X</a>':
        '<a href="#" aria-label="<?php esc_attr_e(\'إكس\', \'brando\'); ?>"><?php esc_html_e(\'إكس\', \'brando\'); ?></a>',
}
for old, new in social_replacements.items():
    if old not in footer_new:
        raise SystemExit(f"Expected social label not found: {old}")
    footer_new = footer_new.replace(old, new, 1)

contact_pattern = re.compile(
    r'''<section class="brando-footer__column brando-footer__contact">\s*
\s*<h3><\?php esc_html_e\('تواصل معنا', 'brando'\); \?></h3>\s*
\s*<p><a href="mailto:hello@brando\.sa">hello@brando\.sa</a></p>\s*
\s*<p><a href="tel:\+966500000000" dir="ltr">\+966 50 000 0000</a></p>\s*
\s*<span><\?php esc_html_e\('السبت – الخميس', 'brando'\); \?><br><\?php esc_html_e\('9 صباحًا – 6 مساءً', 'brando'\); \?></span>\s*
\s*</section>''',
    re.S,
)
contact_block = '''<section class="brando-footer__column brando-footer__contact">
                <h3><?php esc_html_e('تواصل معنا', 'brando'); ?></h3>
                <p><a href="<?php echo esc_url(home_url('/#footer')); ?>"><?php esc_html_e('راسل فريق خدمة العملاء', 'brando'); ?></a></p>
                <p><?php esc_html_e('يسعدنا مساعدتك في الاستفسارات والطلبات', 'brando'); ?></p>
                <span><?php esc_html_e('أوقات الخدمة حسب ساعات العمل المعلنة', 'brando'); ?></span>
            </section>'''
footer_new, n = contact_pattern.subn(contact_block, footer_new, count=1)
if n != 1:
    raise SystemExit("Could not replace Saudi contact block in footer.php")

payments = {
    "<b>mada</b>": "<b>بطاقات الدفع</b>",
    "<b>VISA</b>": "<b>الدفع الإلكتروني</b>",
    "<b>Mastercard</b>": "<b>المحافظ الرقمية</b>",
    "<b>Apple Pay</b>": "<b>دفع آمن</b>",
}
for old, new in payments.items():
    if old not in footer_new:
        raise SystemExit(f"Expected payment label not found: {old}")
    footer_new = footer_new.replace(old, new, 1)

combined_visible_templates = "\n".join([header_new, front_new, footer_new])
for forbidden in ["999 ر.س", "WELCOME10", " ر.س", "+966", "brando.sa", ">mada<", ">VISA<", ">Mastercard<", ">Apple Pay<"]:
    if forbidden in combined_visible_templates:
        raise SystemExit(f"Forbidden hardcoded locale/English token remains: {forbidden}")

outputs = {
    "style.css": style_new,
    "functions.php": functions_new,
    "header.php": header_new,
    "front-page.php": front_new,
    "footer.php": footer_new,
}
for name, content in outputs.items():
    path = theme / name
    tmp = path.with_suffix(path.suffix + ".tmp-brando")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(path)

(theme / "assets" / "css").mkdir(parents=True, exist_ok=True)
(theme / "assets" / "js").mkdir(parents=True, exist_ok=True)
shutil.copy2(css_src, theme / "assets" / "css" / "luxury-v3.css")
shutil.copy2(js_src, theme / "assets" / "js" / "luxury-motion.js")

print("PATCH_VERSION=0.5.1")
print("LAYOUT_STRUCTURE_CHANGED=NO")
print("HARDCODED_SAUDI_REFERENCES=0")
print("ARABIC_UI_PATCHED=YES")
print("LUXURY_V3_CSS_INSTALLED=YES")
print("LUXURY_MOTION_JS_INSTALLED=YES")
