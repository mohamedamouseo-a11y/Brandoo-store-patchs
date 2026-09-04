<?php
if (!defined('ABSPATH')) {
    exit;
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

<header class="site-header" role="banner">
    <div class="brando-container site-header__inner">
        <div class="site-branding">
            <?php if (has_custom_logo()) : ?>
                <?php the_custom_logo(); ?>
            <?php else : ?>
                <a class="site-title" href="<?php echo esc_url(home_url('/')); ?>">
                    <?php bloginfo('name'); ?>
                </a>
            <?php endif; ?>
        </div>

        <nav class="site-nav" aria-label="<?php esc_attr_e('القائمة الرئيسية', 'brando'); ?>">
            <?php
            wp_nav_menu([
                'theme_location' => 'primary',
                'container'      => false,
                'fallback_cb'    => false,
                'menu_class'     => 'site-nav__menu',
            ]);
            ?>
        </nav>

        <div class="site-actions" aria-label="<?php esc_attr_e('إجراءات المتجر', 'brando'); ?>">
            <?php if (class_exists('WooCommerce')) : ?>
                <a href="<?php echo esc_url(wc_get_page_permalink('myaccount')); ?>">
                    <?php esc_html_e('حسابي', 'brando'); ?>
                </a>
                <a href="<?php echo esc_url(wc_get_cart_url()); ?>">
                    <?php esc_html_e('السلة', 'brando'); ?>
                </a>
            <?php endif; ?>
        </div>
    </div>
</header>
