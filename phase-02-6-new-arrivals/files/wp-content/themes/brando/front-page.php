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

$brando_product_fallbacks = [
    [
        'name'       => 'طقم أواني طهي عملي',
        'image'      => 'https://images.unsplash.com/photo-1556911220-bff31c812dba?auto=format&fit=crop&fm=jpg&q=82&w=800',
        'price_text' => '349 ر.س',
        'rating'     => 5,
        'reviews'    => 24,
    ],
    [
        'name'       => 'طقم تقديم أنيق',
        'image'      => 'https://images.unsplash.com/photo-1556910103-1c02745aae4d?auto=format&fit=crop&fm=jpg&q=82&w=800',
        'price_text' => '229 ر.س',
        'rating'     => 5,
        'reviews'    => 18,
    ],
    [
        'name'       => 'منظم مطبخ متعدد الاستخدام',
        'image'      => 'https://images.unsplash.com/photo-1484154218962-a197022b5858?auto=format&fit=crop&fm=jpg&q=82&w=800',
        'price_text' => '179 ر.س',
        'rating'     => 4,
        'reviews'    => 31,
    ],
    [
        'name'       => 'مجموعة مستلزمات الخَبز',
        'image'      => 'https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&fm=jpg&q=82&w=800',
        'price_text' => '199 ر.س',
        'rating'     => 5,
        'reviews'    => 15,
    ],
];

$brando_best_sellers = [];
if (class_exists('WooCommerce') && function_exists('wc_get_product')) {
    $product_query = new WP_Query([
        'post_type'           => 'product',
        'post_status'         => 'publish',
        'posts_per_page'      => 4,
        'fields'              => 'ids',
        'meta_key'            => 'total_sales',
        'orderby'             => [
            'meta_value_num' => 'DESC',
            'date'           => 'DESC',
        ],
        'no_found_rows'       => true,
        'ignore_sticky_posts' => true,
    ]);

    foreach ($product_query->posts as $product_id) {
        $product = wc_get_product($product_id);
        if (!$product || !$product->is_visible()) {
            continue;
        }

        $image_id = (int) $product->get_image_id();
        $image = $image_id ? wp_get_attachment_image_url($image_id, 'woocommerce_thumbnail') : '';
        if (!$image && function_exists('wc_placeholder_img_src')) {
            $image = wc_placeholder_img_src('woocommerce_thumbnail');
        }

        $brando_best_sellers[] = [
            'real'       => true,
            'id'         => (int) $product->get_id(),
            'sku'        => (string) $product->get_sku(),
            'name'       => $product->get_name(),
            'image'      => $image ?: $brando_product_fallbacks[count($brando_best_sellers) % count($brando_product_fallbacks)]['image'],
            'url'        => $product->get_permalink(),
            'price_html' => $product->get_price_html(),
            'rating'     => (float) $product->get_average_rating(),
            'reviews'    => (int) $product->get_review_count(),
            'cart_url'   => $product->add_to_cart_url(),
            'cart_text'  => $product->add_to_cart_text(),
            'ajax'       => $product->supports('ajax_add_to_cart') && $product->is_purchasable() && $product->is_in_stock(),
        ];
    }
}

$product_fallback_index = 0;
while (count($brando_best_sellers) < 4 && $product_fallback_index < count($brando_product_fallbacks)) {
    $fallback = $brando_product_fallbacks[$product_fallback_index];
    $brando_best_sellers[] = [
        'real'       => false,
        'id'         => 0,
        'sku'        => '',
        'name'       => $fallback['name'],
        'image'      => $fallback['image'],
        'url'        => $shop_url,
        'price_text' => $fallback['price_text'],
        'rating'     => $fallback['rating'],
        'reviews'    => $fallback['reviews'],
        'cart_url'   => $shop_url,
        'cart_text'  => 'تسوق الآن',
        'ajax'       => false,
    ];
    $product_fallback_index++;
}
$brando_best_sellers = array_slice($brando_best_sellers, 0, 4);
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

    <section id="best-sellers" class="brando-best-sellers" aria-labelledby="brando-best-sellers-title">
        <div class="brando-best-sellers__inner">
            <header class="brando-best-sellers__head">
                <div class="brando-best-sellers__copy">
                    <span class="brando-best-sellers__eyebrow"><?php esc_html_e('اختيارات عملائنا', 'brando'); ?></span>
                    <h2 id="brando-best-sellers-title" class="brando-best-sellers__title"><?php esc_html_e('الأكثر مبيعًا', 'brando'); ?></h2>
                    <p class="brando-best-sellers__subtitle"><?php esc_html_e('منتجات اختارها عملاؤنا لتجمع بين العملية، الجودة والتصميم العصري.', 'brando'); ?></p>
                </div>
                <a class="brando-best-sellers__all" href="<?php echo esc_url(add_query_arg('orderby', 'popularity', $shop_url)); ?>">
                    <span><?php esc_html_e('عرض الكل', 'brando'); ?></span>
                    <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M19 12H5M11 6l-6 6 6 6"/></svg>
                </a>
            </header>

            <div class="brando-best-sellers__grid">
                <?php foreach ($brando_best_sellers as $index => $card) :
                    $filled_stars = max(0, min(5, (int) round((float) $card['rating'])));
                    $cart_classes = 'brando-product-card__cart';
                    if (!empty($card['ajax'])) {
                        $cart_classes .= ' add_to_cart_button ajax_add_to_cart';
                    }
                ?>
                    <article class="brando-product-card">
                        <a class="brando-product-card__media" href="<?php echo esc_url($card['url']); ?>">
                            <img src="<?php echo esc_url($card['image']); ?>" alt="<?php echo esc_attr($card['name']); ?>" loading="lazy" decoding="async">
                            <span class="brando-product-card__wishlist" aria-hidden="true">
                                <svg viewBox="0 0 24 24"><path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.6l-1-1a5.5 5.5 0 0 0-7.8 7.8l1 1L12 21l7.8-7.6 1-1a5.5 5.5 0 0 0 0-7.8z"/></svg>
                            </span>
                        </a>

                        <div class="brando-product-card__content">
                            <a class="brando-product-card__name" href="<?php echo esc_url($card['url']); ?>"><?php echo esc_html($card['name']); ?></a>

                            <div class="brando-product-card__rating" aria-label="<?php echo esc_attr(sprintf(__('التقييم %.1f من 5', 'brando'), (float) $card['rating'])); ?>">
                                <span class="brando-product-card__stars" aria-hidden="true">
                                    <?php for ($star = 1; $star <= 5; $star++) : ?>
                                        <span<?php echo $star <= $filled_stars ? ' class="is-filled"' : ''; ?>>★</span>
                                    <?php endfor; ?>
                                </span>
                                <span class="brando-product-card__reviews"><?php echo esc_html('(' . (int) $card['reviews'] . ')'); ?></span>
                            </div>

                            <div class="brando-product-card__footer">
                                <div class="brando-product-card__price">
                                    <?php if (!empty($card['real'])) : ?>
                                        <?php echo wp_kses_post($card['price_html']); ?>
                                    <?php else : ?>
                                        <?php echo esc_html($card['price_text']); ?>
                                    <?php endif; ?>
                                </div>

                                <a class="<?php echo esc_attr($cart_classes); ?>" href="<?php echo esc_url($card['cart_url']); ?>"<?php if (!empty($card['real'])) : ?> data-product_id="<?php echo esc_attr((string) $card['id']); ?>" data-product_sku="<?php echo esc_attr($card['sku']); ?>" data-quantity="1" rel="nofollow"<?php endif; ?>>
                                    <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 3h2l2.4 10.2a2 2 0 0 0 2 1.6h7.9a2 2 0 0 0 2-1.6L21 7H6"/><circle cx="10" cy="20" r="1"/><circle cx="18" cy="20" r="1"/></svg>
                                    <span><?php echo esc_html($card['cart_text']); ?></span>
                                </a>
                            </div>
                        </div>
                    </article>
                <?php endforeach; ?>
            </div>
        </div>
    </section>

    <section id="offers" class="brando-promo" aria-labelledby="brando-promo-title">
        <div class="brando-promo__inner">
            <div class="brando-promo__card">
                <div class="brando-promo__content">
                    <span class="brando-promo__eyebrow"><?php esc_html_e('لفترة محدودة', 'brando'); ?></span>
                    <h2 id="brando-promo-title" class="brando-promo__title">
                        <span><?php esc_html_e('عروض الربيع', 'brando'); ?></span>
                        <strong><?php esc_html_e('خصم حتى 30%', 'brando'); ?></strong>
                    </h2>
                    <p class="brando-promo__text"><?php esc_html_e('جدّد مطبخك باختيارات عملية وأنيقة بأسعار مميزة لفترة محدودة.', 'brando'); ?></p>
                    <a class="brando-promo__cta" href="<?php echo esc_url($shop_url); ?>">
                        <span><?php esc_html_e('تسوق العروض', 'brando'); ?></span>
                        <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M19 12H5M11 6l-6 6 6 6"/></svg>
                    </a>
                </div>
                <div class="brando-promo__visual" role="img" aria-label="<?php esc_attr_e('مطبخ عصري ضمن عروض الربيع', 'brando'); ?>">
                    <div class="brando-promo__badge" aria-hidden="true">
                        <span><?php esc_html_e('خصم حتى', 'brando'); ?></span>
                        <strong>30%</strong>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <section id="new-arrivals" class="brando-new-arrivals" aria-labelledby="brando-new-arrivals-title">
        <div class="brando-new-arrivals__inner">
            <header class="brando-new-arrivals__head">
                <div class="brando-new-arrivals__copy">
                    <span class="brando-new-arrivals__eyebrow"><?php esc_html_e('أحدث الإضافات', 'brando'); ?></span>
                    <h2 id="brando-new-arrivals-title" class="brando-new-arrivals__title"><?php esc_html_e('وصل حديثًا', 'brando'); ?></h2>
                    <p class="brando-new-arrivals__subtitle"><?php esc_html_e('اكتشف أحدث المنتجات المضافة إلى براندو، باختيارات عملية تناسب مطبخك كل يوم.', 'brando'); ?></p>
                </div>
                <a class="brando-new-arrivals__all" href="<?php echo esc_url(add_query_arg('orderby', 'date', $shop_url)); ?>">
                    <span><?php esc_html_e('عرض كل الجديد', 'brando'); ?></span>
                    <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M19 12H5M11 6l-6 6 6 6"/></svg>
                </a>
            </header>

            <div class="brando-new-arrivals__products">
                <?php
                $brando_new_arrivals = [];
                if (class_exists('WooCommerce') && function_exists('wc_get_product')) {
                    $latest_query = new WP_Query([
                        'post_type'           => 'product',
                        'post_status'         => 'publish',
                        'posts_per_page'      => 4,
                        'fields'              => 'ids',
                        'orderby'             => 'date',
                        'order'               => 'DESC',
                        'no_found_rows'       => true,
                        'ignore_sticky_posts' => true,
                    ]);

                    foreach ($latest_query->posts as $product_id) {
                        $product = wc_get_product($product_id);
                        if (!$product || !$product->is_visible()) {
                            continue;
                        }

                        $image_id = (int) $product->get_image_id();
                        $image = $image_id ? wp_get_attachment_image_url($image_id, 'woocommerce_thumbnail') : '';
                        if (!$image && function_exists('wc_placeholder_img_src')) {
                            $image = wc_placeholder_img_src('woocommerce_thumbnail');
                        }

                        $brando_new_arrivals[] = [
                            'real'       => true,
                            'id'         => (int) $product->get_id(),
                            'sku'        => (string) $product->get_sku(),
                            'name'       => $product->get_name(),
                            'image'      => $image ?: 'https://images.unsplash.com/photo-1556911220-bff31c812dba?auto=format&fit=crop&fm=jpg&q=82&w=800',
                            'url'        => $product->get_permalink(),
                            'price_html' => $product->get_price_html(),
                            'cart_url'   => $product->add_to_cart_url(),
                            'cart_text'  => $product->add_to_cart_text(),
                            'ajax'       => $product->supports('ajax_add_to_cart') && $product->is_purchasable() && $product->is_in_stock(),
                        ];
                    }
                }

                $brando_new_arrival_fallbacks = [
                    ['name' => 'طقم أدوات تحضير عصري', 'image' => 'https://images.unsplash.com/photo-1556910103-1c02745aae4d?auto=format&fit=crop&fm=jpg&q=82&w=800', 'price_text' => '149 ر.س'],
                    ['name' => 'علب تخزين محكمة الإغلاق', 'image' => 'https://images.unsplash.com/photo-1484154218962-a197022b5858?auto=format&fit=crop&fm=jpg&q=82&w=800', 'price_text' => '129 ر.س'],
                    ['name' => 'طقم تقديم يومي أنيق', 'image' => 'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&fm=jpg&q=82&w=800', 'price_text' => '189 ر.س'],
                    ['name' => 'مجموعة أدوات خبز جديدة', 'image' => 'https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&fm=jpg&q=82&w=800', 'price_text' => '169 ر.س'],
                ];

                $new_fallback_index = 0;
                while (count($brando_new_arrivals) < 4 && $new_fallback_index < count($brando_new_arrival_fallbacks)) {
                    $fallback = $brando_new_arrival_fallbacks[$new_fallback_index];
                    $brando_new_arrivals[] = [
                        'real'       => false,
                        'id'         => 0,
                        'sku'        => '',
                        'name'       => $fallback['name'],
                        'image'      => $fallback['image'],
                        'url'        => $shop_url,
                        'price_text' => $fallback['price_text'],
                        'cart_url'   => $shop_url,
                        'cart_text'  => 'تسوق الآن',
                        'ajax'       => false,
                    ];
                    $new_fallback_index++;
                }
                $brando_new_arrivals = array_slice($brando_new_arrivals, 0, 4);
                ?>

                <div class="woocommerce columns-4">
                    <ul class="products columns-4">
                        <?php foreach ($brando_new_arrivals as $card) :
                            $new_cart_classes = 'button product_type_simple';
                            if (!empty($card['ajax'])) {
                                $new_cart_classes .= ' add_to_cart_button ajax_add_to_cart';
                            }
                        ?>
                            <li class="product type-product brando-new-arrival-card">
                                <a class="woocommerce-LoopProduct-link woocommerce-loop-product__link" href="<?php echo esc_url($card['url']); ?>">
                                    <img src="<?php echo esc_url($card['image']); ?>" alt="<?php echo esc_attr($card['name']); ?>" loading="lazy" decoding="async">
                                    <h2 class="woocommerce-loop-product__title"><?php echo esc_html($card['name']); ?></h2>
                                </a>
                                <span class="price">
                                    <?php if (!empty($card['real'])) : ?>
                                        <?php echo wp_kses_post($card['price_html']); ?>
                                    <?php else : ?>
                                        <?php echo esc_html($card['price_text']); ?>
                                    <?php endif; ?>
                                </span>
                                <a class="<?php echo esc_attr($new_cart_classes); ?>" href="<?php echo esc_url($card['cart_url']); ?>"<?php if (!empty($card['real'])) : ?> data-product_id="<?php echo esc_attr((string) $card['id']); ?>" data-product_sku="<?php echo esc_attr($card['sku']); ?>" data-quantity="1" rel="nofollow"<?php endif; ?>><?php echo esc_html($card['cart_text']); ?></a>
                            </li>
                        <?php endforeach; ?>
                    </ul>
                </div>
            </div>
        </div>
    </section>
</main>
<?php
get_footer();