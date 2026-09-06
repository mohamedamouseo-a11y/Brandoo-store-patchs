<?php
get_header();
$shop_url = function_exists('brando_shop_url') ? brando_shop_url() : home_url('/shop/');

$cat_fallbacks = [
 ['name'=>'تخزين المطبخ','desc'=>'حافظ على مساحتك مرتبة','image'=>'https://images.unsplash.com/photo-1698939586636-98209ecf8516?auto=format&fit=crop&fm=jpg&q=88&w=900'],
 ['name'=>'أدوات الطهي','desc'=>'أدوات عملية لكل يوم','image'=>'https://images.unsplash.com/photo-1621494547944-5ddbc84514b2?auto=format&fit=crop&fm=jpg&q=88&w=900'],
 ['name'=>'أدوات التقديم','desc'=>'لمسات أنيقة مع كل ضيافة','image'=>'https://images.unsplash.com/photo-1772453609632-2f4aa857f56e?auto=format&fit=crop&fm=jpg&q=88&w=900'],
 ['name'=>'الأجهزة الصغيرة','desc'=>'أداء ذكي لمهمة أسهل','image'=>'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&fm=jpg&q=88&w=900'],
 ['name'=>'التنظيم','desc'=>'ترتيب مثالي لمساحتك','image'=>'https://images.unsplash.com/photo-1676976500593-3dfec0b17754?auto=format&fit=crop&fm=jpg&q=88&w=900'],
 ['name'=>'الديكور','desc'=>'لمسة جمالية تكمل مطبخك','image'=>'https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?auto=format&fit=crop&fm=jpg&q=88&w=900'],
];
$cats=[];
if (taxonomy_exists('product_cat')) {
 $terms=get_terms(['taxonomy'=>'product_cat','hide_empty'=>false,'number'=>6,'orderby'=>'name','order'=>'ASC']);
 if (!is_wp_error($terms)) foreach($terms as $i=>$term){
  if($term->slug==='uncategorized') continue;
  $url=get_term_link($term); if(is_wp_error($url)) continue;
  $thumb=(int)get_term_meta($term->term_id,'thumbnail_id',true);
  $img=$thumb?wp_get_attachment_image_url($thumb,'woocommerce_thumbnail'):'';
  $f=$cat_fallbacks[$i%6];
  $cats[]=['name'=>$term->name,'desc'=>$f['desc'],'image'=>$img?:$f['image'],'url'=>$url];
 }
}
for($i=0;count($cats)<6 && $i<6;$i++){ $f=$cat_fallbacks[$i]; $f['url']=$shop_url; $cats[]=$f; }
$cats=array_slice($cats,0,6);

$best_fallbacks=[
 ['name'=>'عربة تنظيم متعددة الرفوف','image'=>'https://images.unsplash.com/photo-1698939586636-98209ecf8516?auto=format&fit=crop&fm=jpg&q=88&w=900','price'=>49.99,'rating'=>5,'reviews'=>1463],
 ['name'=>'طقم أواني طهي متكامل','image'=>'https://images.unsplash.com/photo-1621494547944-5ddbc84514b2?auto=format&fit=crop&fm=jpg&q=88&w=900','price'=>79.99,'rating'=>5,'reviews'=>1220],
 ['name'=>'طقم أوعية محكمة الغلق','image'=>'https://images.unsplash.com/photo-1484154218962-a197022b5858?auto=format&fit=crop&fm=jpg&q=88&w=900','price'=>24.99,'rating'=>5,'reviews'=>1105],
 ['name'=>'طقم أدوات مائدة ستانلس','image'=>'https://images.unsplash.com/photo-1584990347449-a4fb2f9c05a9?auto=format&fit=crop&fm=jpg&q=88&w=900','price'=>29.99,'rating'=>5,'reviews'=>846],
 ['name'=>'سلة تنظيم عملية','image'=>'https://images.unsplash.com/photo-1519710164239-da123dc03ef4?auto=format&fit=crop&fm=jpg&q=88&w=900','price'=>14.99,'rating'=>5,'reviews'=>753],
 ['name'=>'وعاء تقديم خشبي دائري','image'=>'https://images.unsplash.com/photo-1610701596007-11502861dcfa?auto=format&fit=crop&fm=jpg&q=88&w=900','price'=>9.99,'rating'=>5,'reviews'=>753],
];
$new_fallbacks=[
 ['name'=>'وحدة رفوف 3 طبقات','image'=>'https://images.unsplash.com/photo-1595428774223-ef52624120d2?auto=format&fit=crop&fm=jpg&q=88&w=900','price'=>59.99],
 ['name'=>'مصباح LED مرن','image'=>'https://images.unsplash.com/photo-1513506003901-1e6a229e2d15?auto=format&fit=crop&fm=jpg&q=88&w=900','price'=>24.99],
 ['name'=>'وعاء تقديم سيراميك','image'=>'https://images.unsplash.com/photo-1610701596007-11502861dcfa?auto=format&fit=crop&fm=jpg&q=88&w=900','price'=>16.99],
 ['name'=>'زجاجة تخزين زجاجية','image'=>'https://images.unsplash.com/photo-1602143407151-7111542de6e8?auto=format&fit=crop&fm=jpg&q=88&w=900','price'=>4.99],
 ['name'=>'صندوق تخزين قابل للطي','image'=>'https://images.unsplash.com/photo-1519710164239-da123dc03ef4?auto=format&fit=crop&fm=jpg&q=88&w=900','price'=>8.99],
 ['name'=>'وحدة أدراج خشبية','image'=>'https://images.unsplash.com/photo-1595428774223-ef52624120d2?auto=format&fit=crop&fm=jpg&q=88&w=900','price'=>29.99],
];

$collect_products=function($orderby,$fallbacks,$limit=6){
 global $shop_url;
 $items=[];
 if(class_exists('WooCommerce') && function_exists('wc_get_product')){
  $args=['post_type'=>'product','post_status'=>'publish','posts_per_page'=>$limit,'fields'=>'ids','no_found_rows'=>true,'ignore_sticky_posts'=>true];
  if($orderby==='sales'){ $args['meta_key']='total_sales'; $args['orderby']=['meta_value_num'=>'DESC','date'=>'DESC']; }
  else { $args['orderby']='date'; $args['order']='DESC'; }
  $q=new WP_Query($args);
  foreach($q->posts as $id){
   $p=wc_get_product($id); if(!$p || !$p->is_visible()) continue;
   $image=$p->get_image_id()?wp_get_attachment_image_url($p->get_image_id(),'woocommerce_thumbnail'):'';
   if(!$image && function_exists('wc_placeholder_img_src')) $image=wc_placeholder_img_src('woocommerce_thumbnail');
   $items[]=['real'=>true,'id'=>$p->get_id(),'sku'=>$p->get_sku(),'name'=>$p->get_name(),'image'=>$image,'url'=>$p->get_permalink(),'price_html'=>$p->get_price_html(),'rating'=>(float)$p->get_average_rating(),'reviews'=>(int)$p->get_review_count(),'cart_url'=>$p->add_to_cart_url(),'cart_text'=>$p->add_to_cart_text(),'ajax'=>$p->supports('ajax_add_to_cart')&&$p->is_purchasable()&&$p->is_in_stock()];
  }
 }
 for($i=0;count($items)<$limit && $i<count($fallbacks);$i++){
  $f=$fallbacks[$i];
  $items[]=['real'=>false,'id'=>0,'sku'=>'','name'=>$f['name'],'image'=>$f['image'],'url'=>$shop_url,'price_text'=>function_exists('wc_price')?wp_strip_all_tags(wc_price($f['price'])):(string)$f['price'],'rating'=>$f['rating']??5,'reviews'=>$f['reviews']??0,'cart_url'=>$shop_url,'cart_text'=>'أضف إلى السلة','ajax'=>false];
 }
 return array_slice($items,0,$limit);
};
$best=$collect_products('sales',$best_fallbacks,6);
$new=$collect_products('date',$new_fallbacks,6);
?>
<main id="main" class="site-main ref-home">
<section class="brando-hero ref-hero" aria-labelledby="brando-hero-title">
 <div class="brando-hero__frame ref-hero__frame">
  <div class="brando-hero__media ref-hero__media" role="img" aria-label="<?php esc_attr_e('مطبخ عصري من براندو','brando'); ?>"><div class="brando-hero__dots"><span class="is-active"></span><span></span><span></span></div></div>
  <div class="brando-hero__content ref-hero__content">
   <h1 id="brando-hero-title" class="brando-hero__title ref-hero__title"><span><?php esc_html_e('أسلوب عصري','brando'); ?></span><strong><?php esc_html_e('لمطبخك','brando'); ?></strong></h1>
   <p class="brando-hero__lead ref-hero__lead"><?php esc_html_e('اكتشف منتجات مبتكرة بعناية تمنح مطبخك الجمال والعملية التي تستحقها','brando'); ?></p>
   <a class="brando-hero__cta ref-btn ref-btn--orange" href="<?php echo esc_url($shop_url); ?>"><?php esc_html_e('تسوق الآن','brando'); ?><span>←</span></a>
  </div>
 </div>
 <div class="brando-hero__benefits ref-hero-benefits">
  <div><span class="ref-benefit-icon">🏅</span><b><?php esc_html_e('جودة يمكنك الوثوق بها','brando'); ?></b></div>
  <div><span class="ref-benefit-icon">✿</span><b><?php esc_html_e('تصميم يواكبك','brando'); ?></b></div>
  <div><span class="ref-benefit-icon">♢</span><b><?php esc_html_e('شحن سريع وآمن','brando'); ?></b></div>
 </div>
</section>

<section id="categories" class="ref-section ref-categories">
 <div class="ref-shell">
  <div class="ref-section-head"><div><h2><?php esc_html_e('تسوق حسب الفئة','brando'); ?></h2></div><a href="<?php echo esc_url($shop_url); ?>"><?php esc_html_e('عرض كل الفئات','brando'); ?> ←</a></div>
  <div class="ref-category-grid">
   <?php foreach($cats as $i=>$c): ?><a class="ref-category-card" href="<?php echo esc_url($c['url']); ?>"><div class="ref-category-image"><img src="<?php echo esc_url($c['image']); ?>" alt="<?php echo esc_attr($c['name']); ?>"><span>✿</span></div><h3><?php echo esc_html($c['name']); ?></h3><p><?php echo esc_html($c['desc']); ?></p></a><?php endforeach; ?>
  </div>
 </div>
</section>

<section id="best-sellers" class="ref-section ref-best">
 <div class="ref-shell">
  <div class="ref-section-head"><div><h2><?php esc_html_e('الأكثر مبيعًا','brando'); ?></h2></div><a href="<?php echo esc_url(add_query_arg('orderby','popularity',$shop_url)); ?>"><?php esc_html_e('عرض الكل','brando'); ?> ←</a></div>
  <div class="ref-slider-wrap"><button class="ref-slider-arrow ref-slider-arrow--prev" type="button" aria-label="السابق">‹</button><div class="ref-product-grid">
   <?php foreach($best as $card): $stars=max(0,min(5,(int)round($card['rating']))); $cc='ref-cart-btn'; if(!empty($card['ajax'])) $cc.=' add_to_cart_button ajax_add_to_cart'; ?>
   <article class="brando-product-card ref-product-card"><a class="ref-product-image" href="<?php echo esc_url($card['url']); ?>"><img src="<?php echo esc_url($card['image']); ?>" alt="<?php echo esc_attr($card['name']); ?>"><span class="ref-heart">♡</span></a><a class="ref-product-name" href="<?php echo esc_url($card['url']); ?>"><?php echo esc_html($card['name']); ?></a><div class="ref-rating"><span><?php for($s=1;$s<=5;$s++) echo $s<=$stars?'★':'☆'; ?></span><small>(<?php echo (int)$card['reviews']; ?>)</small></div><div class="ref-price"><?php echo !empty($card['real'])?wp_kses_post($card['price_html']):esc_html($card['price_text']); ?></div><a class="<?php echo esc_attr($cc); ?>" href="<?php echo esc_url($card['cart_url']); ?>"<?php if(!empty($card['real'])): ?> data-product_id="<?php echo esc_attr((string)$card['id']); ?>" data-product_sku="<?php echo esc_attr($card['sku']); ?>" data-quantity="1" rel="nofollow"<?php endif; ?>><?php esc_html_e('أضف إلى السلة','brando'); ?></a></article>
   <?php endforeach; ?>
  </div><button class="ref-slider-arrow ref-slider-arrow--next" type="button" aria-label="التالي">›</button></div>
 </div>
</section>

<section id="offers" class="ref-promo-section"><div class="ref-shell"><div class="ref-promo">
 <div class="ref-promo-benefits"><div><b>🏅</b><span><?php esc_html_e('أسعار مناسبة لكل ميزانية','brando'); ?></span></div><div><b>🏅</b><span><?php esc_html_e('جودة عالية مضمونة','brando'); ?></span></div><div><b>♢</b><span><?php esc_html_e('منتجات مختارة بعناية','brando'); ?></span></div></div>
 <div class="ref-promo-copy"><h2><?php esc_html_e('عروض الربيع','brando'); ?><strong><?php esc_html_e('خصم حتى 30%','brando'); ?></strong></h2><p><?php esc_html_e('على مختارات من مستلزمات المطبخ والديكور','brando'); ?></p><a class="ref-btn ref-btn--orange" href="<?php echo esc_url($shop_url); ?>"><?php esc_html_e('تسوق العروض','brando'); ?></a></div>
 <div class="brando-promo__visual ref-promo-image"></div>
 </div></div></section>

<section id="new-arrivals" class="ref-section ref-new"><div class="ref-shell">
 <div class="ref-section-head"><div><h2><?php esc_html_e('وصل حديثًا','brando'); ?></h2></div><a href="<?php echo esc_url(add_query_arg('orderby','date',$shop_url)); ?>"><?php esc_html_e('عرض كل الجديد','brando'); ?> ←</a></div>
 <div class="ref-slider-wrap"><button class="ref-slider-arrow ref-slider-arrow--prev" type="button" aria-label="السابق">‹</button><div class="ref-product-grid ref-product-grid--new">
 <?php foreach($new as $card): $cc='ref-cart-btn'; if(!empty($card['ajax'])) $cc.=' add_to_cart_button ajax_add_to_cart'; ?>
 <article class="ref-product-card ref-product-card--new"><a class="ref-product-image" href="<?php echo esc_url($card['url']); ?>"><img src="<?php echo esc_url($card['image']); ?>" alt="<?php echo esc_attr($card['name']); ?>"></a><a class="ref-product-name" href="<?php echo esc_url($card['url']); ?>"><?php echo esc_html($card['name']); ?></a><div class="ref-price"><?php echo !empty($card['real'])?wp_kses_post($card['price_html']):esc_html($card['price_text']); ?></div></article>
 <?php endforeach; ?>
 </div><button class="ref-slider-arrow ref-slider-arrow--next" type="button" aria-label="التالي">›</button></div>
 </div></section>
</main>
<?php get_footer(); ?>
