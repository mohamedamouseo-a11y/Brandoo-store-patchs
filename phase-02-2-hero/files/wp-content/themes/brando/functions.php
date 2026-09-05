<?php
if (!defined('ABSPATH')) {
    exit;
}

define('BRANDO_THEME_VERSION', '0.2.2');

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
    wp_enqueue_style('brando-main', get_template_directory_uri() . '/assets/css/main.css', [], BRANDO_THEME_VERSION);
    wp_enqueue_style('brando-rtl', get_template_directory_uri() . '/assets/css/rtl.css', ['brando-main'], BRANDO_THEME_VERSION);
    wp_enqueue_style('brando-header', get_template_directory_uri() . '/assets/css/header.css', ['brando-main', 'brando-rtl'], BRANDO_THEME_VERSION);

    if (is_front_page()) {
        wp_enqueue_style('brando-hero', get_template_directory_uri() . '/assets/css/hero.css', ['brando-header'], BRANDO_THEME_VERSION);
    }

    wp_enqueue_script('brando-main', get_template_directory_uri() . '/assets/js/main.js', [], BRANDO_THEME_VERSION, true);
    wp_enqueue_script('brando-header', get_template_directory_uri() . '/assets/js/header.js', ['brando-main'], BRANDO_THEME_VERSION, true);
}
add_action('wp_enqueue_scripts', 'brando_enqueue_assets');

function brando_force_rtl_language_attributes(string $output): string
{
    if (preg_match('/\sdir=("|\')[^"\']*("|\')/i', $output)) {
        return (string) preg_replace('/\sdir=("|\')[^"\']*("|\')/i', ' dir="rtl"', $output, 1);
    }
    return trim($output) . ' dir="rtl"';
}
add_filter('language_attributes', 'brando_force_rtl_language_attributes');

function brando_body_classes(array $classes): array
{
    $classes[] = 'brando-site';
    $classes[] = 'brando-rtl';
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

function brando_shop_url(): string
{
    if (class_exists('WooCommerce')) {
        $url = wc_get_page_permalink('shop');
        if (is_string($url) && $url !== '') {
            return $url;
        }
    }
    return home_url('/shop/');
}

function brando_header_fallback_menu(): void
{
    $shop = brando_shop_url();
    $items = [
        ['label' => 'الرئيسية', 'url' => home_url('/'), 'class' => is_front_page() ? 'current-menu-item' : ''],
        ['label' => 'المنتجات', 'url' => $shop, 'class' => 'menu-item-has-children'],
        ['label' => 'الأكثر مبيعًا', 'url' => add_query_arg('orderby', 'popularity', $shop), 'class' => ''],
        ['label' => 'التصنيفات', 'url' => home_url('/#categories'), 'class' => ''],
        ['label' => 'العروض', 'url' => home_url('/#offers'), 'class' => ''],
        ['label' => 'تواصل معنا', 'url' => home_url('/#footer'), 'class' => ''],
    ];

    echo '<ul class="site-nav__menu">';
    foreach ($items as $item) {
        $class = trim('menu-item ' . $item['class']);
        echo '<li class="' . esc_attr($class) . '"><a href="' . esc_url($item['url']) . '">' . esc_html($item['label']) . '</a></li>';
    }
    echo '</ul>';
}

function brando_cart_count_markup(): string
{
    $count = 0;
    if (function_exists('WC') && WC()->cart) {
        $count = (int) WC()->cart->get_cart_contents_count();
    }
    return '<span class="brando-action-count brando-cart-count" aria-label="' . esc_attr(sprintf(__('عدد المنتجات في السلة: %d', 'brando'), $count)) . '">' . esc_html((string) $count) . '</span>';
}

function brando_cart_count_fragment(array $fragments): array
{
    $fragments['span.brando-cart-count'] = brando_cart_count_markup();
    return $fragments;
}
add_filter('woocommerce_add_to_cart_fragments', 'brando_cart_count_fragment');
