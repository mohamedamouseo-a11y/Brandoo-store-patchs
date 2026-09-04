<?php
if (!defined('ABSPATH')) {
    exit;
}

define('BRANDO_THEME_VERSION', '0.1.0');

function brando_setup(): void
{
    load_theme_textdomain('brando', get_template_directory() . '/languages');

    add_theme_support('title-tag');
    add_theme_support('post-thumbnails');
    add_theme_support('custom-logo');
    add_theme_support('html5', [
        'search-form',
        'comment-form',
        'comment-list',
        'gallery',
        'caption',
        'style',
        'script',
    ]);

    add_theme_support('woocommerce');
    add_theme_support('wc-product-gallery-zoom');
    add_theme_support('wc-product-gallery-lightbox');
    add_theme_support('wc-product-gallery-slider');

    register_nav_menus([
        'primary' => __('القائمة الرئيسية', 'brando'),
        'footer'  => __('روابط التذييل', 'brando'),
    ]);
}
add_action('after_setup_theme', 'brando_setup');

function brando_enqueue_assets(): void
{
    wp_enqueue_style(
        'brando-main',
        get_template_directory_uri() . '/assets/css/main.css',
        [],
        BRANDO_THEME_VERSION
    );

    if (is_rtl()) {
        wp_enqueue_style(
            'brando-rtl',
            get_template_directory_uri() . '/assets/css/rtl.css',
            ['brando-main'],
            BRANDO_THEME_VERSION
        );
    }

    wp_enqueue_script(
        'brando-main',
        get_template_directory_uri() . '/assets/js/main.js',
        [],
        BRANDO_THEME_VERSION,
        true
    );
}
add_action('wp_enqueue_scripts', 'brando_enqueue_assets');

function brando_body_classes(array $classes): array
{
    $classes[] = 'brando-site';

    if (class_exists('WooCommerce')) {
        $classes[] = 'brando-woocommerce';
    }

    return $classes;
}
add_filter('body_class', 'brando_body_classes');

function brando_require_woocommerce_notice(): void
{
    if (!current_user_can('activate_plugins') || class_exists('WooCommerce')) {
        return;
    }

    echo '<div class="notice notice-warning"><p>';
    echo esc_html__('قالب براندو مصمم للعمل مع WooCommerce. يرجى تثبيت وتفعيل WooCommerce.', 'brando');
    echo '</p></div>';
}
add_action('admin_notices', 'brando_require_woocommerce_notice');
