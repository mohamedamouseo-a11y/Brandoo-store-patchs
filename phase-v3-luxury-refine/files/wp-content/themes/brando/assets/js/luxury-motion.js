(() => {
  'use strict';

  const ready = () => {
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduceMotion) {
      document.querySelectorAll('.brando-reveal').forEach((el) => el.classList.add('is-visible'));
      return;
    }

    const sections = [
      '.brando-categories__head',
      '.brando-best-sellers__head',
      '.brando-promo__card',
      '.brando-new-arrivals__head',
      '.brando-trust__inner',
      '.brando-newsletter__inner',
      '.brando-footer__grid'
    ];

    sections.forEach((selector) => {
      document.querySelectorAll(selector).forEach((el) => el.classList.add('brando-reveal'));
    });

    document.querySelectorAll('.brando-category-card, .brando-product-card, .brando-new-arrivals .woocommerce ul.products li.product').forEach((el, index) => {
      el.classList.add('brando-reveal');
      el.dataset.delay = String((index % 4) + 1);
    });

    const observer = new IntersectionObserver((entries, obs) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        obs.unobserve(entry.target);
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -7% 0px' });

    document.querySelectorAll('.brando-reveal').forEach((el) => observer.observe(el));

    document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
      anchor.addEventListener('click', (event) => {
        const href = anchor.getAttribute('href');
        if (!href || href === '#') return;
        const target = document.querySelector(href);
        if (!target) return;
        event.preventDefault();
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
    });
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', ready, { once: true });
  } else {
    ready();
  }
})();
