<?php
if (!defined('ABSPATH')) { exit; }

final class BDH_Access {
    private const OWNERS_OPTION = 'bdh_super_admin_user_ids';

    public static function init(): void {
        add_action('admin_init', [self::class, 'guard_direct_page']);
    }

    public static function seed_owner(): void {
        $user_id = get_current_user_id();
        if ($user_id <= 0 && !is_multisite()) {
            $admins = get_users(['role' => 'administrator', 'number' => 1, 'orderby' => 'ID', 'order' => 'ASC', 'fields' => 'ID']);
            $user_id = isset($admins[0]) ? (int) $admins[0] : 0;
        }
        if ($user_id <= 0) { return; }
        $owners = self::owners();
        if (!in_array($user_id, $owners, true)) {
            $owners[] = $user_id;
            update_option(self::OWNERS_OPTION, array_values(array_unique(array_map('intval', $owners))), false);
        }
    }

    public static function owners(): array {
        $value = get_option(self::OWNERS_OPTION, []);
        return is_array($value) ? array_values(array_filter(array_map('intval', $value))) : [];
    }

    public static function allowed(?int $user_id = null): bool {
        $user_id = $user_id ?: get_current_user_id();
        if ($user_id <= 0) { return false; }

        if (is_multisite()) {
            return is_super_admin($user_id);
        }

        $user = get_userdata($user_id);
        if (!$user || !user_can($user, 'manage_options')) { return false; }
        return in_array($user_id, self::owners(), true);
    }

    public static function require_access(): void {
        if (!self::allowed()) {
            wp_die(esc_html__('Developer Hub access required.', 'brando-developer-hub'), 403);
        }
    }

    public static function rest_permission(): bool|WP_Error {
        if (!is_user_logged_in()) {
            return new WP_Error('bdh_unauthorized', 'Unauthorized', ['status' => 401]);
        }
        if (!self::allowed()) {
            return new WP_Error('bdh_forbidden', 'Developer Hub access required', ['status' => 403]);
        }
        return true;
    }

    public static function guard_direct_page(): void {
        if (isset($_GET['page']) && sanitize_key(wp_unslash($_GET['page'])) === 'brando-developer-hub') {
            self::require_access();
        }
    }
}
