<?php
if (!defined('ABSPATH')) { exit; }

final class BDH_REST {
    private const NS = 'brando-developer-hub/v1';

    public static function init(): void {
        add_action('rest_api_init', [self::class, 'routes']);
    }

    private static function route(string $path, string $methods, callable $callback, ?callable $permission = null): void {
        register_rest_route(self::NS, $path, [
            'methods' => $methods,
            'callback' => $callback,
            'permission_callback' => $permission ?: [BDH_Access::class, 'rest_permission'],
        ]);
    }

    public static function routes(): void {
        self::route('/health', 'GET', [self::class, 'status']);
        self::route('/mcp', 'POST', [self::class, 'mcp']);
        self::route('/github-push-mode', 'POST', [self::class, 'push_mode']);
        self::route('/github-auth', 'POST', [self::class, 'github_auth']);
        self::route('/github-token', 'POST', [self::class, 'github_auth']);
        self::route('/github-connection', 'DELETE', [self::class, 'github_disconnect']);
        self::route('/github-repositories', 'GET', [self::class, 'repositories']);
        self::route('/github-branches', 'GET', [self::class, 'branches']);
        self::route('/github-selection', 'POST', [self::class, 'selection']);
        self::route('/github-sync-preview', 'POST', [self::class, 'sync_preview']);
        self::route('/github-sync-execute', 'POST', [self::class, 'sync_execute']);
        self::route('/generate-latest-context', 'POST', [self::class, 'generate_context']);
        self::route('/context', 'GET', [self::class, 'context'], [self::class, 'context_permission']);
    }

    private static function error(Throwable $e, int $status = 400): WP_Error {
        return new WP_Error('bdh_error', BDH_Core::redact($e->getMessage()), ['status' => $status]);
    }

    public static function status(): WP_REST_Response|WP_Error {
        try { return rest_ensure_response(BDH_Core::public_status()); }
        catch (Throwable $e) { return self::error($e, 500); }
    }

    public static function mcp(WP_REST_Request $request): WP_REST_Response {
        $enabled = rest_sanitize_boolean($request->get_param('enabled'));
        $state = BDH_Core::save(['mcp_enabled' => $enabled]);
        return rest_ensure_response(['ok' => true, 'mcpEnabled' => (bool) $state['mcp_enabled']]);
    }

    public static function push_mode(WP_REST_Request $request): WP_REST_Response|WP_Error {
        $mode = sanitize_key((string) $request->get_param('mode'));
        if (!in_array($mode, ['off','review','auto'], true)) {
            return new WP_Error('bdh_invalid_mode', 'Push mode must be off, review, or auto.', ['status'=>400]);
        }
        BDH_Core::save(['github_push_mode'=>$mode]);
        return rest_ensure_response(['ok'=>true,'githubPushMode'=>$mode]);
    }

    public static function github_auth(WP_REST_Request $request): WP_REST_Response|WP_Error {
        try {
            $token = trim((string) $request->get_param('token'));
            return rest_ensure_response(['ok'=>true] + BDH_Core::verify_github_token($token));
        } catch (Throwable $e) { return self::error($e); }
    }

    public static function github_disconnect(): WP_REST_Response {
        BDH_Core::save([
            'github_token_encrypted'=>null,
            'github_repo'=>'',
            'github_branch'=>'main',
            'github_default_branch'=>null,
            'github_verified_at'=>null,
            'github_login'=>null,
            'github_permission'=>null,
        ]);
        return rest_ensure_response(['ok'=>true]);
    }

    public static function repositories(): WP_REST_Response|WP_Error {
        try { return rest_ensure_response(['repositories'=>BDH_Core::repositories()]); }
        catch (Throwable $e) { return self::error($e); }
    }

    public static function branches(WP_REST_Request $request): WP_REST_Response|WP_Error {
        try {
            $repo = trim((string) $request->get_param('repo'));
            return rest_ensure_response(['branches'=>BDH_Core::branches($repo)]);
        } catch (Throwable $e) { return self::error($e); }
    }

    public static function selection(WP_REST_Request $request): WP_REST_Response|WP_Error {
        try {
            $repo = trim((string) $request->get_param('repo'));
            $branch = trim((string) $request->get_param('branch'));
            $state = BDH_Core::save_selection($repo, $branch);
            return rest_ensure_response(['ok'=>true,'githubRepo'=>$state['github_repo'],'githubBranch'=>$state['github_branch']]);
        } catch (Throwable $e) { return self::error($e); }
    }

    public static function sync_preview(WP_REST_Request $request): WP_REST_Response|WP_Error {
        try { return rest_ensure_response(BDH_Core::sync_preview((string) $request->get_param('action'))); }
        catch (Throwable $e) { return self::error($e, str_contains($e->getMessage(), 'already running') ? 409 : 400); }
    }

    public static function sync_execute(WP_REST_Request $request): WP_REST_Response|WP_Error {
        try {
            $mode = (string) (BDH_Core::state()['github_push_mode'] ?? 'review');
            if ($mode === 'off') { throw new RuntimeException('GitHub write operations are disabled by Push Control.'); }
            return rest_ensure_response(BDH_Core::sync_execute(
                sanitize_key((string) $request->get_param('action')),
                sanitize_text_field((string) $request->get_param('fingerprint')),
                sanitize_text_field((string) $request->get_param('message'))
            ));
        } catch (Throwable $e) { return self::error($e, str_contains($e->getMessage(), 'already running') ? 409 : 400); }
    }

    public static function generate_context(): WP_REST_Response|WP_Error {
        try { return rest_ensure_response(BDH_Core::generate_context()); }
        catch (Throwable $e) { return self::error($e, 500); }
    }

    public static function context_permission(WP_REST_Request $request): bool|WP_Error {
        if (is_user_logged_in() && BDH_Access::allowed()) { return true; }
        $header = trim((string) $request->get_header('authorization'));
        if (preg_match('/^Bearer\s+(.+)$/i', $header, $m)) {
            $state = BDH_Core::state();
            $expected = (string) ($state['ai_access_token'] ?? '');
            if ($expected !== '' && hash_equals($expected, trim($m[1]))) { return true; }
        }
        return new WP_Error('bdh_forbidden', 'Developer Hub AI access required', ['status'=>403]);
    }

    public static function context(): WP_REST_Response|WP_Error {
        $path = BDH_Core::context_path();
        if (!is_file($path)) { return new WP_Error('bdh_context_missing', 'Generate the project context first.', ['status'=>404]); }
        $content = file_get_contents($path);
        if ($content === false) { return new WP_Error('bdh_context_read', 'Failed to read project context.', ['status'=>500]); }
        $response = new WP_REST_Response($content, 200);
        $response->header('Content-Type', 'text/plain; charset=utf-8');
        $response->header('Cache-Control', 'no-store, private');
        return $response;
    }
}
