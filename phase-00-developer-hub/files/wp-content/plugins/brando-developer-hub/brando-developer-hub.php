<?php
/**
 * Plugin Name: Brando Developer Hub
 * Description: Super-admin-only Developer Hub for Brando, modeled on the TCRM Developer Hub workflow.
 * Version: 0.1.0
 * Requires at least: 6.6
 * Requires PHP: 8.1
 * Author: Brando
 */

if (!defined('ABSPATH')) { exit; }

define('BDH_VERSION', '0.1.0');
define('BDH_FILE', __FILE__);
define('BDH_DIR', plugin_dir_path(__FILE__));
define('BDH_URL', plugin_dir_url(__FILE__));

require_once BDH_DIR . 'includes/class-bdh-access.php';
require_once BDH_DIR . 'includes/class-bdh-core.php';
require_once BDH_DIR . 'includes/class-bdh-rest.php';
require_once BDH_DIR . 'includes/class-bdh-admin.php';

register_activation_hook(__FILE__, static function (): void {
    BDH_Access::seed_owner();
    BDH_Core::ensure_defaults();
});

add_action('plugins_loaded', static function (): void {
    BDH_Access::init();
    BDH_REST::init();
    BDH_Admin::init();
});
