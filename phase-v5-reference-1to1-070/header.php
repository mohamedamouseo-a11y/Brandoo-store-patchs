<?php
if (!defined('ABSPATH')) { exit; }
$account_url = wp_login_url();
$cart_url = home_url('/cart/');
$shop_url = function_exists('brando_shop_url') ? brando_shop_url() : home_url('/shop/');
$currency_symbol = '';
if (class_exists('WooCommerce')) {
    $account_url = wc_get_page_permalink('myaccount');
    $cart_url = wc_get_cart_url();
    if (function_exists('get_woocommerce_currency_symbol')) { $currency_symbol = get_woocommerce_currency_symbol(); }
}
?><!doctype html>
<html <?php language_attributes(); ?>>
<head>
<meta charset="<?php bloginfo('charset'); ?>">
<meta name="viewport" content="width=device-width, initial-scale=1">
<?php wp_head(); ?>
</head>
<body <?php body_class('brando-reference-070'); ?>>
<?php wp_body_open(); ?>
<a class="screen-reader-text" href="#main"><?php esc_html_e('تخطي إلى المحتوى','brando'); ?></a>

<div class="ref-topbar" data-brando-topbar>
  <div class="ref-shell ref-topbar__inner">
    <div class="ref-topbar__copy">
      <span class="ref-topbar__shipping">🚚 <?php echo esc_html(sprintf(__('شحن مجاني للطلبات فوق 399 %s','brando'), $currency_symbol)); ?></span>
      <span class="ref-topbar__sep">•</span>
      <span><?php esc_html_e('خصم 10% على طلبك الأول – استخدم الكود: WELCOME10','brando'); ?></span>
    </div>
    <button class="ref-topbar__close" type="button" aria-label="<?php esc_attr_e('إغلاق','brando'); ?>" data-brando-topbar-close>×</button>
  </div>
</div>

<header class="site-header brando-header ref-header" role="banner">
  <div class="ref-shell ref-header__inner">
    <div class="ref-actions" aria-label="<?php esc_attr_e('إجراءات المتجر','brando'); ?>">
      <a class="ref-action ref-cart" href="<?php echo esc_url($cart_url); ?>" aria-label="<?php esc_attr_e('السلة','brando'); ?>">
        <svg viewBox="0 0 24 24"><path d="M3 4h2l2.2 10h9.9l2-7H7"/><circle cx="9" cy="19" r="1.5"/><circle cx="17" cy="19" r="1.5"/></svg>
        <?php echo wp_kses_post(brando_cart_count_markup()); ?>
      </a>
      <button class="ref-action ref-wishlist" type="button" aria-label="<?php esc_attr_e('المفضلة','brando'); ?>"><svg viewBox="0 0 24 24"><path d="M20.8 4.6a5.4 5.4 0 0 0-7.6 0L12 5.8l-1.2-1.2a5.4 5.4 0 0 0-7.6 7.6L12 21l8.8-8.8a5.4 5.4 0 0 0 0-7.6Z"/></svg><span>0</span></button>
      <a class="ref-action" href="<?php echo esc_url($account_url); ?>" aria-label="<?php esc_attr_e('حسابي','brando'); ?>"><svg viewBox="0 0 24 24"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4.4 3.6-7 8-7s8 2.6 8 7"/></svg></a>
      <button class="ref-action" type="button" aria-expanded="false" aria-controls="brando-header-search" data-brando-search-toggle aria-label="<?php esc_attr_e('بحث','brando'); ?>"><svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="m16 16 5 5"/></svg></button>
    </div>

    <div class="ref-branding">
      <?php if (has_custom_logo()) : ?>
        <?php the_custom_logo(); ?>
      <?php else : ?>
        <a class="ref-brand" href="<?php echo esc_url(home_url('/')); ?>">
          <span class="ref-brand__text"><strong>براندو</strong><small><?php esc_html_e('لمسة عصرية لمطبخك','brando'); ?></small></span>
          <span class="ref-brand__mark" aria-hidden="true"><svg viewBox="0 0 48 48"><circle cx="24" cy="24" r="19"/><path d="M12 28c5-13 16-17 25-11M14 34c8 3 20-1 24-11M17 16c3 10 12 17 22 17"/></svg></span>
        </a>
      <?php endif; ?>
    </div>

    <button class="brando-mobile-toggle ref-mobile-toggle" type="button" aria-expanded="false" aria-controls="brando-primary-nav" data-brando-menu-toggle><span></span><span></span><span></span></button>
    <nav id="brando-primary-nav" class="ref-nav" aria-label="<?php esc_attr_e('القائمة الرئيسية','brando'); ?>" data-brando-menu>
      <a class="is-active" href="<?php echo esc_url(home_url('/')); ?>"><?php esc_html_e('الرئيسية','brando'); ?></a>
      <a href="<?php echo esc_url($shop_url); ?>"><?php esc_html_e('المنتجات','brando'); ?></a>
      <a href="<?php echo esc_url(home_url('/#categories')); ?>"><?php esc_html_e('التصنيفات','brando'); ?></a>
      <a href="<?php echo esc_url(add_query_arg('orderby','popularity',$shop_url)); ?>"><?php esc_html_e('الأكثر مبيعًا','brando'); ?></a>
      <a href="<?php echo esc_url(home_url('/#offers')); ?>"><?php esc_html_e('العروض','brando'); ?></a>
    </nav>
  </div>
  <div id="brando-header-search" class="brando-header-search ref-search" hidden data-brando-search><div class="ref-shell"><form role="search" method="get" action="<?php echo esc_url(home_url('/')); ?>"><input type="search" name="s" placeholder="<?php esc_attr_e('ابحث عن منتج...','brando'); ?>"><?php if (class_exists('WooCommerce')) : ?><input type="hidden" name="post_type" value="product"><?php endif; ?><button type="submit"><?php esc_html_e('بحث','brando'); ?></button></form></div></div>
</header>
