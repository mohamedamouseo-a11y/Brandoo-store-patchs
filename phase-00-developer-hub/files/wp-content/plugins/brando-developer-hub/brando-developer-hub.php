<?php
/**
 * Plugin Name: Brando Developer Hub
 * Description: Super-admin-only Developer Hub for Brando, modeled on the TCRM Developer Hub workflow.
 * Version: 0.1.3
 * Requires at least: 6.6
 * Requires PHP: 8.1
 * Author: Brando
 */

if (!defined('ABSPATH')) { exit; }

define('BDH_VERSION', '0.1.3');
define('BDH_FILE', __FILE__);
define('BDH_DIR', plugin_dir_path(__FILE__));
define('BDH_URL', plugin_dir_url(__FILE__));

require_once BDH_DIR . 'includes/class-bdh-access.php';
require_once BDH_DIR . 'includes/class-bdh-core.php';
require_once BDH_DIR . 'includes/class-bdh-repository-init.php';
require_once BDH_DIR . 'includes/class-bdh-rest.php';
require_once BDH_DIR . 'includes/class-bdh-admin.php';

register_activation_hook(__FILE__, static function (): void {
    BDH_Access::seed_owner();
    BDH_Core::ensure_defaults();
});

// Register hooks immediately when WordPress loads the active plugin.
// Do not defer this bootstrap to `plugins_loaded`: some managed-hosting /
// temporary MU-activation flows can load this file after that action has
// already fired, which would leave rest_api_init/admin hooks unregistered.
BDH_Access::init();
BDH_REST::init();
BDH_Admin::init();
