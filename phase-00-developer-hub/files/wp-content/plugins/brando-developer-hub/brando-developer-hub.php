<?php
/**
 * Plugin Name: Brando Developer Hub
 * Description: Super-admin-only Developer Hub for Brando, modeled on the TCRM Developer Hub workflow.
 * Version: 0.1.7
 * Requires at least: 6.6
 * Requires PHP: 8.1
 * Author: Brando
 */

if (!defined('ABSPATH')) { exit; }

define('BDH_VERSION', '0.1.7');
define('BDH_BUILD_ID', '20260905-v017-empty-repo-bootstrap');
define('BDH_FILE', __FILE__);
define('BDH_DIR', plugin_dir_path(__FILE__));
define('BDH_URL', plugin_dir_url(__FILE__));

$bdh_fail_soft = static function (string $message): void {
    $safe = 'Brando Developer Hub disabled safely: ' . $message;
    error_log($safe);
    add_action('admin_notices', static function () use ($safe): void {
        if (!current_user_can('manage_options')) { return; }
        echo '<div class="notice notice-error"><p>' . esc_html($safe) . '</p></div>';
    });
};

$bdh_required_files = [
    'includes/class-bdh-access.php',
    'includes/class-bdh-core.php',
    'includes/class-bdh-repository-init.php',
    'includes/class-bdh-manual-first-push.php',
    'includes/class-bdh-api-mode.php',
    'includes/class-bdh-rest.php',
    'includes/class-bdh-admin.php',
];

foreach ($bdh_required_files as $bdh_relative_file) {
    if (!is_file(BDH_DIR . $bdh_relative_file)) {
        $bdh_fail_soft('missing required file: ' . $bdh_relative_file . '. Re-deploy all v0.1.7 plugin files byte-for-byte.');
        return;
    }
}

require_once BDH_DIR . 'includes/class-bdh-access.php';
require_once BDH_DIR . 'includes/class-bdh-core.php';
require_once BDH_DIR . 'includes/class-bdh-repository-init.php';
require_once BDH_DIR . 'includes/class-bdh-manual-first-push.php';
require_once BDH_DIR . 'includes/class-bdh-api-mode.php';
require_once BDH_DIR . 'includes/class-bdh-rest.php';
require_once BDH_DIR . 'includes/class-bdh-admin.php';

$bdh_required_classes = [
    'BDH_Access',
    'BDH_Core',
    'BDH_Repository_Init',
    'BDH_Manual_First_Push',
    'BDH_API_Mode',
    'BDH_REST',
    'BDH_Admin',
];

foreach ($bdh_required_classes as $bdh_class) {
    if (!class_exists($bdh_class, false)) {
        $bdh_fail_soft('canonical class ' . $bdh_class . ' is missing. Re-deploy every v0.1.7 file from the public patch repo.');
        return;
    }
}

register_activation_hook(__FILE__, static function (): void {
    BDH_Access::seed_owner();
    BDH_Core::ensure_defaults();
});

BDH_Access::init();
BDH_REST::init();
BDH_Admin::init();
