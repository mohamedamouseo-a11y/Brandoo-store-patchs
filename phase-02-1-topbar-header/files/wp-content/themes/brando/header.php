<?php
if (!defined('ABSPATH')) {
    exit;
}

$account_url = wp_login_url();
$cart_url = home_url('/cart/');
if (class_exists('WooCommerce')) {
    $account_url = wc_get_page_permalink('myaccount');
    $cart_url = wc_get_cart_url();
}
?><!doctype html>
<html <?php language_attributes(); ?>>
<head>
    <meta charset="<?php bloginfo('charset'); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>
<a class="screen-reader-text" href="#main"><?php esc_html_e('تخطي إلى المحتوى', 'brando'); ?></a>

<div class="brando-topbar" data-brando-topbar>
    <div class="brando-container brando-topbar__inner">
        <button class="brando-topbar__close" type="button" aria-label="<?php esc_attr_e('إغلاق شريط العرض', 'brando'); ?>" data-brando-topbar-close>×</button>
        <div class="brando-topbar__message brando-topbar__shipping">
            <span class="brando-topbar__icon" aria-hidden="true">
                <svg viewBox="0 0 24 24"><path d="M3 6h11v9H3zM14 9h4l3 3v3h-7zM6.5 18a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3ZM18 18a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3Z"/></svg>
            </span>
            <span><?php esc_html_e('شحن مجاني للطلبات فوق 999 ر.س', 'brando'); ?></span>
        </div>
        <span class="brando-topbar__divider" aria-hidden="true"></span>
        <div class="brando-topbar__message">
            <span><?php esc_html_e('خصم 10% على أول طلب — استخدم الكود:', 'brando'); ?></span>
            <strong>WELCOME10</strong>
        </div>
    </div>
</div>

<header class="site-header brando-header" role="banner">
    <div class="brando-container brando-header__inner">
        <div class="site-branding brando-branding">
            <?php if (has_custom_logo()) : ?>
                <?php the_custom_logo(); ?>
            <?php else : ?>
                <a class="brando-brand" href="<?php echo esc_url(home_url('/')); ?>" aria-label="<?php esc_attr_e('براندو - الرئيسية', 'brando'); ?>">
                    <span class="brando-brand__mark" aria-hidden="true">
                        <svg viewBox="0 0 48 48"><circle cx="24" cy="24" r="19"/><path d="M12 28c5-13 16-17 25-11M14 34c8 3 20-1 24-11M17 16c3 10 12 17 22 17"/></svg>
                    </span>
                    <span class="brando-brand__text">
                        <strong>براندو</strong>
                        <small><?php esc_html_e('لمسة عصرية لمطبخك', 'brando'); ?></small>
                    </span>
                </a>
            <?php endif; ?>
        </div>

        <button class="brando-mobile-toggle" type="button" aria-expanded="false" aria-controls="brando-primary-nav" data-brando-menu-toggle>
            <span></span><span></span><span></span>
            <span class="screen-reader-text"><?php esc_html_e('فتح القائمة', 'brando'); ?></span>
        </button>

        <nav id="brando-primary-nav" class="site-nav brando-nav" aria-label="<?php esc_attr_e('القائمة الرئيسية', 'brando'); ?>" data-brando-menu>
            <?php
            wp_nav_menu([
                'theme_location' => 'primary',
                'container'      => false,
                'fallback_cb'    => 'brando_header_fallback_menu',
                'menu_class'     => 'site-nav__menu',
            ]);
            ?>
        </nav>

        <div class="site-actions brando-actions" aria-label="<?php esc_attr_e('إجراءات المتجر', 'brando'); ?>">
            <button class="brando-action brando-search-toggle" type="button" aria-expanded="false" aria-controls="brando-header-search" data-brando-search-toggle>
                <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m16 16 5 5"/></svg>
                <span class="screen-reader-text"><?php esc_html_e('بحث', 'brando'); ?></span>
            </button>

            <a class="brando-action" href="<?php echo esc_url($account_url); ?>" aria-label="<?php esc_attr_e('حسابي', 'brando'); ?>">
                <svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4.4 3.6-7 8-7s8 2.6 8 7"/></svg>
            </a>

            <button class="brando-action brando-wishlist" type="button" aria-label="<?php esc_attr_e('المفضلة', 'brando'); ?>">
                <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20.8 4.6a5.4 5.4 0 0 0-7.6 0L12 5.8l-1.2-1.2a5.4 5.4 0 0 0-7.6 7.6L12 21l8.8-8.8a5.4 5.4 0 0 0 0-7.6Z"/></svg>
                <span class="brando-action-count">0</span>
            </button>

            <a class="brando-action brando-cart" href="<?php echo esc_url($cart_url); ?>" aria-label="<?php esc_attr_e('السلة', 'brando'); ?>">
                <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 4h2l2.2 10h9.9l2-7H7"/><circle cx="9" cy="19" r="1.5"/><circle cx="17" cy="19" r="1.5"/></svg>
                <?php echo wp_kses_post(brando_cart_count_markup()); ?>
            </a>
        </div>
    </div>

    <div id="brando-header-search" class="brando-header-search" hidden data-brando-search>
        <div class="brando-container">
            <form role="search" method="get" class="brando-search-form" action="<?php echo esc_url(home_url('/')); ?>">
                <label class="screen-reader-text" for="brando-search-field"><?php esc_html_e('ابحث عن منتج', 'brando'); ?></label>
                <input id="brando-search-field" type="search" name="s" placeholder="<?php esc_attr_e('ابحث عن منتج...', 'brando'); ?>" autocomplete="off">
                <?php if (class_exists('WooCommerce')) : ?><input type="hidden" name="post_type" value="product"><?php endif; ?>
                <button type="submit"><?php esc_html_e('بحث', 'brando'); ?></button>
            </form>
        </div>
    </div>
</header>
