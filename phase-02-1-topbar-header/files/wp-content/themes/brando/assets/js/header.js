(() => {
    const topbar = document.querySelector('[data-brando-topbar]');
    const topbarClose = document.querySelector('[data-brando-topbar-close]');
    const menuToggle = document.querySelector('[data-brando-menu-toggle]');
    const menu = document.querySelector('[data-brando-menu]');
    const searchToggle = document.querySelector('[data-brando-search-toggle]');
    const search = document.querySelector('[data-brando-search]');

    if (topbar && topbarClose) {
        try {
            if (sessionStorage.getItem('brandoTopbarClosed') === '1') {
                topbar.hidden = true;
            }
        } catch (e) {}

        topbarClose.addEventListener('click', () => {
            topbar.hidden = true;
            try { sessionStorage.setItem('brandoTopbarClosed', '1'); } catch (e) {}
        });
    }

    if (menuToggle && menu) {
        menuToggle.addEventListener('click', () => {
            const open = menu.classList.toggle('is-open');
            menuToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
        });
    }

    if (searchToggle && search) {
        searchToggle.addEventListener('click', () => {
            const opening = search.hasAttribute('hidden');
            if (opening) {
                search.removeAttribute('hidden');
                searchToggle.setAttribute('aria-expanded', 'true');
                const field = search.querySelector('input[type="search"]');
                if (field) { window.setTimeout(() => field.focus(), 30); }
            } else {
                search.setAttribute('hidden', '');
                searchToggle.setAttribute('aria-expanded', 'false');
            }
        });
    }

    document.addEventListener('keydown', (event) => {
        if (event.key !== 'Escape') return;

        if (search && !search.hasAttribute('hidden')) {
            search.setAttribute('hidden', '');
            if (searchToggle) searchToggle.setAttribute('aria-expanded', 'false');
        }

        if (menu && menu.classList.contains('is-open')) {
            menu.classList.remove('is-open');
            if (menuToggle) menuToggle.setAttribute('aria-expanded', 'false');
        }
    });
})();
