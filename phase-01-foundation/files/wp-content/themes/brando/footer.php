<?php
if (!defined('ABSPATH')) {
    exit;
}
?>
<footer class="site-footer">
    <div class="brando-container site-footer__grid">
        <section>
            <h2 class="site-footer__title"><?php bloginfo('name'); ?></h2>
            <p><?php esc_html_e('كل ما يحتاجه مطبخك بتجربة تسوق عربية عصرية.', 'brando'); ?></p>
        </section>

        <nav aria-label="<?php esc_attr_e('روابط التذييل', 'brando'); ?>">
            <?php
            wp_nav_menu([
                'theme_location' => 'footer',
                'container'      => false,
                'fallback_cb'    => false,
                'menu_class'     => 'site-footer__menu',
            ]);
            ?>
        </nav>
    </div>

    <div class="brando-container site-footer__bottom">
        <small>
            &copy; <?php echo esc_html(wp_date('Y')); ?>
            <?php bloginfo('name'); ?>.
            <?php esc_html_e('جميع الحقوق محفوظة.', 'brando'); ?>
        </small>
    </div>
</footer>

<?php wp_footer(); ?>
</body>
</html>
