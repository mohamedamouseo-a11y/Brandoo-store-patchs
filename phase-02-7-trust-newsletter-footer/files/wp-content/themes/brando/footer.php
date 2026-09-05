<?php
if (!defined('ABSPATH')) {
    exit;
}

$brando_shop_url = function_exists('brando_shop_url') ? brando_shop_url() : home_url('/shop/');
?>

<?php if (is_front_page()) : ?>
    <section class="brando-trust" aria-label="<?php esc_attr_e('مزايا التسوق من براندو', 'brando'); ?>">
        <div class="brando-trust__inner">
            <article class="brando-trust__item">
                <span class="brando-trust__icon" aria-hidden="true">
                    <svg viewBox="0 0 24 24"><path d="M12 3l7 3v5c0 4.8-2.8 8.1-7 10-4.2-1.9-7-5.2-7-10V6z"/><path d="m9 12 2 2 4-4"/></svg>
                </span>
                <div>
                    <h3><?php esc_html_e('دفع آمن', 'brando'); ?></h3>
                    <p><?php esc_html_e('خيارات دفع موثوقة ومحمية', 'brando'); ?></p>
                </div>
            </article>

            <article class="brando-trust__item">
                <span class="brando-trust__icon" aria-hidden="true">
                    <svg viewBox="0 0 24 24"><path d="M4 7h11v10H4z"/><path d="M15 10h3l3 3v4h-6z"/><circle cx="8" cy="18" r="2"/><circle cx="18" cy="18" r="2"/></svg>
                </span>
                <div>
                    <h3><?php esc_html_e('توصيل موثوق', 'brando'); ?></h3>
                    <p><?php esc_html_e('تغليف مرتب وشحن بعناية', 'brando'); ?></p>
                </div>
            </article>

            <article class="brando-trust__item">
                <span class="brando-trust__icon" aria-hidden="true">
                    <svg viewBox="0 0 24 24"><path d="M12 2 4 6v6c0 5 3.4 8.3 8 10 4.6-1.7 8-5 8-10V6z"/><path d="M8.5 12.5 11 15l4.5-6"/></svg>
                </span>
                <div>
                    <h3><?php esc_html_e('جودة مختارة', 'brando'); ?></h3>
                    <p><?php esc_html_e('منتجات عملية بمعايير واضحة', 'brando'); ?></p>
                </div>
            </article>

            <article class="brando-trust__item">
                <span class="brando-trust__icon" aria-hidden="true">
                    <svg viewBox="0 0 24 24"><path d="M4 13v-2a8 8 0 0 1 16 0v2"/><path d="M4 13h3v6H5a2 2 0 0 1-2-2v-2a2 2 0 0 1 1-2zM20 13h-3v6h2a2 2 0 0 0 2-2v-2a2 2 0 0 0-1-2z"/><path d="M17 19c0 1.7-1.3 3-3 3h-2"/></svg>
                </span>
                <div>
                    <h3><?php esc_html_e('دعم العملاء', 'brando'); ?></h3>
                    <p><?php esc_html_e('نساعدك قبل وبعد الطلب', 'brando'); ?></p>
                </div>
            </article>
        </div>
    </section>

    <section class="brando-newsletter" aria-labelledby="brando-newsletter-title">
        <div class="brando-newsletter__inner">
            <div class="brando-newsletter__copy">
                <span class="brando-newsletter__eyebrow"><?php esc_html_e('كن قريبًا من الجديد', 'brando'); ?></span>
                <h2 id="brando-newsletter-title"><?php esc_html_e('عروض وأفكار لمطبخك تصلك أولًا', 'brando'); ?></h2>
                <p><?php esc_html_e('اشترك لتصلك أحدث المنتجات والعروض المختارة من براندو.', 'brando'); ?></p>
            </div>

            <form class="brando-newsletter__form" action="#" method="post" onsubmit="return false;">
                <label class="screen-reader-text" for="brando-newsletter-email"><?php esc_html_e('البريد الإلكتروني', 'brando'); ?></label>
                <input id="brando-newsletter-email" type="email" name="brando_newsletter_email" placeholder="<?php esc_attr_e('بريدك الإلكتروني', 'brando'); ?>" autocomplete="email">
                <button type="submit"><?php esc_html_e('اشترك الآن', 'brando'); ?></button>
            </form>
        </div>
    </section>
<?php endif; ?>

<footer id="footer" class="site-footer brando-footer">
    <div class="brando-footer__inner">
        <div class="brando-footer__grid">
            <section class="brando-footer__brand" aria-labelledby="brando-footer-brand-title">
                <h2 id="brando-footer-brand-title" class="brando-footer__brand-name"><?php bloginfo('name'); ?></h2>
                <p><?php esc_html_e('كل ما يحتاجه مطبخك بتجربة تسوق عربية عصرية تجمع بين العملية والأناقة.', 'brando'); ?></p>
                <div class="brando-footer__social" aria-label="<?php esc_attr_e('روابط التواصل الاجتماعي', 'brando'); ?>">
                    <a href="#" aria-label="Instagram">IG</a>
                    <a href="#" aria-label="TikTok">TT</a>
                    <a href="#" aria-label="X">X</a>
                </div>
            </section>

            <nav class="brando-footer__column" aria-label="<?php esc_attr_e('التسوق', 'brando'); ?>">
                <h3><?php esc_html_e('التسوق', 'brando'); ?></h3>
                <ul>
                    <li><a href="<?php echo esc_url($brando_shop_url); ?>"><?php esc_html_e('كل المنتجات', 'brando'); ?></a></li>
                    <li><a href="<?php echo esc_url(add_query_arg('orderby', 'popularity', $brando_shop_url)); ?>"><?php esc_html_e('الأكثر مبيعًا', 'brando'); ?></a></li>
                    <li><a href="<?php echo esc_url(home_url('/#categories')); ?>"><?php esc_html_e('التصنيفات', 'brando'); ?></a></li>
                    <li><a href="<?php echo esc_url(home_url('/#offers')); ?>"><?php esc_html_e('العروض', 'brando'); ?></a></li>
                </ul>
            </nav>

            <nav class="brando-footer__column" aria-label="<?php esc_attr_e('خدمة العملاء', 'brando'); ?>">
                <h3><?php esc_html_e('خدمة العملاء', 'brando'); ?></h3>
                <ul>
                    <li><a href="<?php echo esc_url(home_url('/#footer')); ?>"><?php esc_html_e('تواصل معنا', 'brando'); ?></a></li>
                    <li><a href="#"><?php esc_html_e('الشحن والتوصيل', 'brando'); ?></a></li>
                    <li><a href="#"><?php esc_html_e('الاستبدال والاسترجاع', 'brando'); ?></a></li>
                    <li><a href="#"><?php esc_html_e('سياسة الخصوصية', 'brando'); ?></a></li>
                </ul>
            </nav>

            <section class="brando-footer__column brando-footer__contact">
                <h3><?php esc_html_e('تواصل معنا', 'brando'); ?></h3>
                <p><a href="mailto:hello@brando.sa">hello@brando.sa</a></p>
                <p><a href="tel:+966500000000" dir="ltr">+966 50 000 0000</a></p>
                <span><?php esc_html_e('السبت – الخميس', 'brando'); ?><br><?php esc_html_e('9 صباحًا – 6 مساءً', 'brando'); ?></span>
            </section>
        </div>

        <div class="brando-footer__payments" aria-label="<?php esc_attr_e('وسائل الدفع', 'brando'); ?>">
            <span><?php esc_html_e('دفع آمن عبر', 'brando'); ?></span>
            <div class="brando-footer__payment-list" aria-hidden="true">
                <b>mada</b>
                <b>VISA</b>
                <b>Mastercard</b>
                <b>Apple Pay</b>
            </div>
        </div>

        <div class="brando-footer__bottom">
            <small>&copy; <?php echo esc_html(wp_date('Y')); ?> <?php bloginfo('name'); ?>. <?php esc_html_e('جميع الحقوق محفوظة.', 'brando'); ?></small>
            <span><?php esc_html_e('تجربة تسوق صُممت لمطبخ أجمل.', 'brando'); ?></span>
        </div>
    </div>
</footer>

<?php wp_footer(); ?>
</body>
</html>
