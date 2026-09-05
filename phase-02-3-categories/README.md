# Phase 02.3 — Categories

Implements only the approved homepage `تسوق حسب الفئة` section after Phase 02.2.

Included:
- six responsive category cards with images and action icon
- reads real WooCommerce `product_cat` terms and category thumbnails when available
- fills missing cards with safe demo kitchen categories until six cards are shown
- links real terms to their WooCommerce archives; demo cards link to Shop
- RTL responsive styling for desktop/tablet/mobile
- restores canonical `main.css` and `rtl.css` from Phase 02.1 because the latest private baseline had those base assets reduced to 14-byte stubs after the last sync
- preserves Phase 02.2 Hero unchanged
- hotfix: RTL forcing is frontend-only; wp-admin keeps its native WordPress/WooCommerce direction
- visual hotfix: category cards now use explicit flex/block sizing and extra section bottom space so card labels remain fully inside the white Categories section and the footer cannot cut them off

Theme version: `0.2.3.2`

Do not implement Best Sellers / Phase 02.4 in this phase.
