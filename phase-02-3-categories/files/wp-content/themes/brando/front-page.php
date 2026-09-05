<?php
get_header();
$shop_url = function_exists('brando_shop_url') ? brando_shop_url() : home_url('/shop/');

$brando_category_fallbacks = [
    ['name' => 'أدوات الطبخ', 'image' => 'https://images.unsplash.com/photo-1556911220-bff31c812dba?auto=format&fit=crop&fm=jpg&q=80&w=700'],
    ['name' => 'أواني التقديم', 'image' => 'https://images.unsplash.com/photo-1556910103-1c02745aae4d?auto=format&fit=crop&fm=jpg&q=80&w=700'],
    ['name' => 'التخزين والتنظيم', 'image' => 'https://images.unsplash.com/photo-1484154218962-a197022b5858?auto=format&fit=crop&fm=jpg&q=80&w=700'],
    ['name' => 'مستلزمات الخَبز', 'image' => 'https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&fm=jpg&q=80&w=700'],
    ['name' => 'أدوات المائدة', 'image' => 'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&fm=jpg&q=80&w=700'],
    ['name' => 'تجهيزات المطبخ', 'image' => 'https://images.unsplash.com/photo-1600566753086-00f18fb6b3ea?auto=format&fit=crop&fm=jpg&q=80&w=700'],
];

$brando_category_cards = [];
if (taxonomy_exists('product_cat')) {
    $terms = get_terms([
        'taxonomy'   => 'product_cat',
        'hide_empty' => false,
        'number'     => 6,
        'orderby'    => 'name',
        'order'      => 'ASC',
    ]);

    if (!is_wp_error($terms)) {
        foreach ($terms as $index => $term) {
            if ($term->slug === 'uncategorized') {
                continue;
            }

            $term_link = get_term_link($term);
            if (is_wp_error($term_link)) {
                continue;
            }

            $thumbnail_id = (int) get_term_meta($term->term_id, 'thumbnail_id', true);
            $image = $thumbnail_id ? wp_get_attachment_image_url($thumbnail_id, 'woocommerce_thumbnail') : '';
            if (!$image) {
                $fallback = $brando_category_fallbacks[$index % count($brando_category_fallbacks)];
                $image = $fallback['image'];
            }

            $brando_category_cards[] = [
                'name'  => $term->name,
                'image' => $image,
                'url'   => $term_link,
            ];
        }
    }
}

$fallback_index = 0;
while (count($brando_category_cards) < 6 && $fallback_index < count($brando_category_fallbacks)) {
    $fallback = $brando_category_fallbacks[$fallback_index];
    $brando_category_cards[] = [
        'name'  => $fallback['name'],
        'image' => $fallback['image'],
        'url'   => $shop_url,
    ];
    $fallback_index++;
}
$brando_category_cards = array_slice($brando_category_cards, 0, 6);
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

    <section id="categories" class="brando-categories" aria-labelledby="brando-categories-title">
        <div class="brando-categories__inner">
            <header class="brando-categories__head">
                <span class="brando-categories__eyebrow"><?php esc_html_e('اكتشف مجموعتنا', 'brando'); ?></span>
                <h2 id="brando-categories-title" class="brando-categories__title"><?php esc_html_e('تسوق حسب الفئة', 'brando'); ?></h2>
                <p class="brando-categories__subtitle"><?php esc_html_e('اختيارات مرتبة لكل احتياجات مطبخك، من الأدوات اليومية إلى التفاصيل التي تكمل المساحة.', 'brando'); ?></p>
            </header>

            <div class="brando-categories__grid">
                <?php foreach ($brando_category_cards as $card) : ?>
                    <a class="brando-category-card" href="<?php echo esc_url($card['url']); ?>">
                        <span class="brando-category-card__media">
                            <img src="<?php echo esc_url($card['image']); ?>" alt="<?php echo esc_attr($card['name']); ?>" loading="lazy" decoding="async">
                            <span class="brando-category-card__icon" aria-hidden="true">
                                <svg viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></svg>
                            </span>
                        </span>
                        <span class="brando-category-card__content">
                            <strong class="brando-category-card__name"><?php echo esc_html($card['name']); ?></strong>
                            <span class="brando-category-card__hint"><?php esc_html_e('اكتشف المجموعة', 'brando'); ?></span>
                        </span>
                    </a>
                <?php endforeach; ?>
            </div>
        </div>
    </section>
</main>
<?php
get_footer();
