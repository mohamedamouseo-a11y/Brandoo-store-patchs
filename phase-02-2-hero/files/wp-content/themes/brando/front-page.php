<?php
get_header();
$shop_url = function_exists('brando_shop_url') ? brando_shop_url() : home_url('/shop/');
?>
<main id="main" class="site-main brando-home">
    <section class="brando-hero" aria-labelledby="brando-hero-title">
        <div class="brando-hero__frame">
            <div class="brando-hero__media" role="img" aria-label="<?php esc_attr_e('مطبخ عصري داكن من براندو', 'brando'); ?>">
                <div class="brando-hero__dots" aria-hidden="true">
                    <span class="is-active"></span><span></span><span></span>
                </div>
            </div>

            <div class="brando-hero__content">
                <h1 id="brando-hero-title" class="brando-hero__title">
                    <span><?php esc_html_e('أسلوب عصري', 'brando'); ?></span>
                    <strong><?php esc_html_e('لمطبخك', 'brando'); ?></strong>
                </h1>
                <p class="brando-hero__lead"><?php esc_html_e('اكتشف منتجات مختارة بعناية تمنح مطبخك العملية والأناقة التي تستحقها.', 'brando'); ?></p>
                <a class="brando-hero__cta" href="<?php echo esc_url($shop_url); ?>">
                    <span><?php esc_html_e('تسوق الآن', 'brando'); ?></span>
                    <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M19 12H5M11 6l-6 6 6 6"/></svg>
                </a>
            </div>
        </div>

        <div class="brando-hero__benefits" aria-label="<?php esc_attr_e('مميزات براندو', 'brando'); ?>">
            <div class="brando-hero__benefit">
                <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3l7 3v5c0 4.8-2.8 8.1-7 10-4.2-1.9-7-5.2-7-10V6z"/><path d="m9 12 2 2 4-4"/></svg>
                <span><?php esc_html_e('جودة يمكنك الوثوق بها', 'brando'); ?></span>
            </div>
            <div class="brando-hero__benefit">
                <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 20 20 4M8 4l12 12M3 8l5-5 13 13-5 5z"/></svg>
                <span><?php esc_html_e('تصميم يلهمك', 'brando'); ?></span>
            </div>
            <div class="brando-hero__benefit">
                <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2 4 6v6c0 5 3.4 8.3 8 10 4.6-1.7 8-5 8-10V6z"/><path d="M12 7v10M8 12h8"/></svg>
                <span><?php esc_html_e('منتجات عملية تدوم', 'brando'); ?></span>
            </div>
        </div>
    </section>
</main>
<?php
get_footer();
