<?php
get_header();
?>
<main id="main" class="site-main">
    <div class="brando-container content-stack">
        <?php if (have_posts()) : ?>
            <?php while (have_posts()) : the_post(); ?>
                <article <?php post_class('content-card'); ?>>
                    <h1><a href="<?php the_permalink(); ?>"><?php the_title(); ?></a></h1>
                    <?php the_excerpt(); ?>
                </article>
            <?php endwhile; ?>

            <?php the_posts_pagination(); ?>
        <?php else : ?>
            <p><?php esc_html_e('لا يوجد محتوى حتى الآن.', 'brando'); ?></p>
        <?php endif; ?>
    </div>
</main>
<?php
get_footer();
