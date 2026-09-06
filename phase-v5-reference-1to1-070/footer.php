<?php
if (!defined('ABSPATH')) { exit; }
$shop_url = function_exists('brando_shop_url') ? brando_shop_url() : home_url('/shop/');
?>
<?php if (is_front_page()) : ?>
<section class="ref-trust" aria-label="<?php esc_attr_e('مزايا التسوق من براندو','brando'); ?>"><div class="ref-shell ref-trust__grid">
  <article><span>🚚</span><div><h3><?php esc_html_e('توصيل سريع','brando'); ?></h3><p><?php esc_html_e('توصيل خلال 1-3 أيام عمل','brando'); ?></p></div></article>
  <article><span>🔒</span><div><h3><?php esc_html_e('دفع آمن','brando'); ?></h3><p><?php esc_html_e('مدفوعات آمنة وحماية بياناتك','brando'); ?></p></div></article>
  <article><span>🏅</span><div><h3><?php esc_html_e('منتجات عالية الجودة','brando'); ?></h3><p><?php esc_html_e('مواد منتقاة لتناسب احتياجاتك','brando'); ?></p></div></article>
  <article><span>🎧</span><div><h3><?php esc_html_e('دعم العملاء','brando'); ?></h3><p><?php esc_html_e('نحن هنا لمساعدتك في أي وقت','brando'); ?></p></div></article>
</div></section>

<section class="ref-newsletter" aria-labelledby="ref-newsletter-title"><div class="ref-shell ref-newsletter__inner">
  <div class="ref-newsletter__copy"><span class="ref-newsletter__icon">✉</span><div><h2 id="ref-newsletter-title"><?php esc_html_e('اشترك للحصول على العروض والمعلومات','brando'); ?></h2><p><?php esc_html_e('كن أول من يعرف عن أحدث العروض والمنتجات الجديدة','brando'); ?></p></div></div>
  <form class="ref-newsletter__form" action="#" method="post" onsubmit="return false;"><input type="email" placeholder="<?php esc_attr_e('ادخل بريدك الإلكتروني','brando'); ?>" autocomplete="email"><button type="submit"><?php esc_html_e('اشترك الآن','brando'); ?></button></form>
</div></section>
<?php endif; ?>

<footer id="footer" class="ref-footer"><div class="ref-shell ref-footer__inner">
  <div class="ref-footer__grid">
    <section class="ref-footer__brand"><div class="ref-footer__brandline"><span class="ref-footer__mark">◉</span><h2>براندو</h2></div><p><?php esc_html_e('لمسة عصرية لمطبخك','brando'); ?></p><ul><li>📍 <?php esc_html_e('القاهرة - مصر','brando'); ?></li><li>☎ 0100 123 4567</li><li>✉ info@brando.com</li></ul></section>
    <nav><h3><?php esc_html_e('جميع المتجر','brando'); ?></h3><a href="<?php echo esc_url($shop_url); ?>"><?php esc_html_e('جميع المنتجات','brando'); ?></a><a href="<?php echo esc_url(home_url('/#categories')); ?>"><?php esc_html_e('أدوات الطهي','brando'); ?></a><a href="<?php echo esc_url(home_url('/#categories')); ?>"><?php esc_html_e('التنظيم والتخزين','brando'); ?></a><a href="<?php echo esc_url(home_url('/#categories')); ?>"><?php esc_html_e('أدوات التقديم','brando'); ?></a><a href="<?php echo esc_url(home_url('/#categories')); ?>"><?php esc_html_e('الأجهزة الصغيرة','brando'); ?></a><a href="<?php echo esc_url(home_url('/#offers')); ?>"><?php esc_html_e('العروض','brando'); ?></a></nav>
    <nav><h3><?php esc_html_e('خدمة العملاء','brando'); ?></h3><a href="#"><?php esc_html_e('الأسئلة الشائعة','brando'); ?></a><a href="#"><?php esc_html_e('تتبع الطلب','brando'); ?></a><a href="#"><?php esc_html_e('طرق الشحن','brando'); ?></a><a href="#"><?php esc_html_e('الاستبدال والاسترجاع','brando'); ?></a></nav>
    <nav><h3><?php esc_html_e('عن براندو','brando'); ?></h3><a href="#"><?php esc_html_e('قصتنا','brando'); ?></a><a href="#"><?php esc_html_e('سياسة الخصوصية','brando'); ?></a><a href="#"><?php esc_html_e('الشروط والأحكام','brando'); ?></a><a href="#"><?php esc_html_e('سياسة الاسترجاع','brando'); ?></a><a href="#"><?php esc_html_e('اتصل بنا','brando'); ?></a></nav>
    <section class="ref-footer__social"><h3><?php esc_html_e('تابعنا','brando'); ?></h3><div><a href="#">◎</a><a href="#">f</a><a href="#">▶</a><a href="#">𝕏</a></div><h3><?php esc_html_e('طرق الدفع','brando'); ?></h3><div class="ref-payments"><span>mada</span><span>Pay</span><span>VISA</span><span>VISA</span><span>●</span></div></section>
  </div>
  <div class="ref-footer__bottom">© <?php echo esc_html(wp_date('Y')); ?> <?php esc_html_e('براندو. جميع الحقوق محفوظة','brando'); ?></div>
</div></footer>
<?php wp_footer(); ?>
</body></html>
