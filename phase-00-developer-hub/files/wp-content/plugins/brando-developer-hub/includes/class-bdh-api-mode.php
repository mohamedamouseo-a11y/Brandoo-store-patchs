<?php
if (!defined('ABSPATH')) { exit; }

final class BDH_API_Mode {
    private const INIT_PREVIEW_PREFIX = 'bdh_api_init_';
    private const PUSH_PREVIEW_PREFIX = 'bdh_api_push_';
    private const LOCK_TRANSIENT = 'bdh_git_operation_lock';
    private const MAX_FILES = 1000;
    private const MAX_BYTES = 8388608;

    public static function active(): bool {
        return !function_exists('proc_open');
    }

    private static function root(): string { return BDH_Core::repo_root(); }
    private static function init_key(): string { return self::INIT_PREVIEW_PREFIX . get_current_user_id(); }
    private static function push_key(): string { return self::PUSH_PREVIEW_PREFIX . get_current_user_id(); }

    private static function validate_repo(string $repo): string {
        $repo = trim($repo);
        if (!preg_match('/^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/', $repo)) { throw new RuntimeException('Invalid GitHub repository.'); }
        return $repo;
    }

    private static function validate_branch(string $branch): string {
        $branch = trim($branch) ?: 'main';
        if (!preg_match('/^[A-Za-z0-9._\/-]+$/', $branch) || str_contains($branch, '..')) { throw new RuntimeException('Invalid branch.'); }
        return $branch;
    }

    private static function managed_path(string $relative): bool {
        $relative = ltrim(str_replace('\\', '/', $relative), '/');
        if ($relative === '' || str_contains($relative, '../')) { return false; }
        if (str_starts_with($relative, 'wp-content/plugins/brando-developer-hub/')) { return true; }
        if (preg_match('#^wp-content/themes/brando(?:-[A-Za-z0-9_.-]+)?/#', $relative)) { return true; }
        if (preg_match('#^wp-content/mu-plugins/brando-[A-Za-z0-9_.-]+\.php$#', $relative)) { return true; }
        return false;
    }

    private static function allowed_extension(string $path): bool {
        $ext = strtolower(pathinfo($path, PATHINFO_EXTENSION));
        return in_array($ext, ['php','js','css','json','md','txt','yml','yaml','xml','html','svg'], true);
    }

    private static function manifest(): array {
        $root = self::root();
        $map = []; $preview = []; $total = 0;
        $it = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($root, FilesystemIterator::SKIP_DOTS));
        foreach ($it as $entry) {
            if (!$entry->isFile() || $entry->isLink()) { continue; }
            $full = str_replace('\\', '/', $entry->getPathname());
            $relative = ltrim(str_replace(str_replace('\\', '/', $root), '', $full), '/');
            if (!self::managed_path($relative) || !self::allowed_extension($relative)) { continue; }
            $size = (int)$entry->getSize();
            if ($size > 1048576) { throw new RuntimeException('Managed file exceeds 1 MB API-mode safety limit: ' . $relative); }
            $fileContent = file_get_contents($entry->getPathname());
            if (!is_string($fileContent)) { throw new RuntimeException('Failed to read managed file: ' . $relative); }
            $total += strlen($fileContent);
            if ($total > self::MAX_BYTES) { throw new RuntimeException('API-mode baseline exceeds the 8 MB safety limit.'); }
            $map[$relative] = ['sha256'=>hash('sha256', $fileContent), 'content'=>$fileContent, 'size'=>strlen($fileContent)];
            if (count($map) > self::MAX_FILES) { throw new RuntimeException('API-mode baseline contains too many managed files.'); }
        }
        ksort($map, SORT_STRING);
        foreach ($map as $path=>$meta) {
            $preview[] = ['direction'=>'local','status'=>'A','path'=>$path];
            if (count($preview) >= 500) { break; }
        }
        $fingerprintParts = [];
        foreach ($map as $path=>$meta) { $fingerprintParts[] = $path . ':' . $meta['size'] . ':' . $meta['sha256']; }
        return [
            'map'=>$map,
            'hash'=>hash('sha256', implode("\n", $fingerprintParts)),
            'fileCount'=>count($map),
            'sizeBytes'=>$total,
            'files'=>$preview,
            'truncated'=>count($map) > 500,
        ];
    }

    private static function request(string $method, string $repo, string $path, ?array $body = null): array {
        $token = BDH_Core::github_token();
        if ($token === '') { throw new RuntimeException('Verify the GitHub token first.'); }
        $url = 'https://api.github.com/repos/' . $repo . $path;
        $args = [
            'method'=>$method,
            'timeout'=>45,
            'redirection'=>0,
            'headers'=>[
                'Authorization'=>'Bearer ' . $token,
                'Accept'=>'application/vnd.github+json',
                'X-GitHub-Api-Version'=>'2022-11-28',
                'User-Agent'=>'Brando-Developer-Hub',
                'Content-Type'=>'application/json',
            ],
        ];
        if ($body !== null) { $args['body'] = wp_json_encode($body); }
        $response = wp_remote_request($url, $args);
        if (is_wp_error($response)) { throw new RuntimeException($response->get_error_message()); }
        $code = (int)wp_remote_retrieve_response_code($response);
        $raw = (string)wp_remote_retrieve_body($response);
        $data = $raw !== '' ? json_decode($raw, true) : [];
        if ($code < 200 || $code >= 300) {
            $message = is_array($data) ? (string)($data['message'] ?? 'GitHub API request failed.') : 'GitHub API request failed.';
            throw new RuntimeException(BDH_Core::redact($message));
        }
        return is_array($data) ? $data : [];
    }

    private static function contents_path(string $relative): string {
        $relative = ltrim(str_replace('\\', '/', $relative), '/');
        return '/contents/' . implode('/', array_map('rawurlencode', explode('/', $relative)));
    }

    private static function stored_map(array $map): array {
        $stored = [];
        foreach ($map as $path=>$meta) {
            $stored[$path] = ['sha256'=>(string)$meta['sha256'], 'size'=>(int)$meta['size']];
        }
        return $stored;
    }

    private static function save_remote_state(string $branch, string $sha, array $map, string $manifestHash): void {
        BDH_Core::save([
            'github_api_mode'=>true,
            'github_default_branch'=>$branch,
            'github_last_sync_at'=>gmdate('c'),
            'github_last_sync_commit'=>$sha,
            'github_last_sync_by'=>wp_get_current_user()->user_login,
            'github_api_last_map'=>self::stored_map($map),
            'github_api_last_manifest'=>$manifestHash,
        ]);
    }

    private static function remote_head(string $repo, string $branch): string {
        $branches = BDH_Core::branches($repo);
        if (!in_array($branch, $branches, true)) { return ''; }
        $ref = self::request('GET', $repo, '/git/ref/heads/' . rawurlencode($branch));
        return (string)($ref['object']['sha'] ?? '');
    }

    private static function acquire(string $type): void {
        if (get_transient(self::LOCK_TRANSIENT)) { throw new RuntimeException('Another GitHub operation is already running.'); }
        set_transient(self::LOCK_TRANSIENT, ['user'=>get_current_user_id(),'at'=>time(),'type'=>$type], 15 * MINUTE_IN_SECONDS);
    }

    private static function release(): void { delete_transient(self::LOCK_TRANSIENT); }

    public static function init_preview(string $repo, string $branch): array {
        $repo = self::validate_repo($repo);
        $branch = self::validate_branch($branch);
        $info = BDH_Core::github_request('https://api.github.com/repos/' . $repo);
        $permissions = is_array($info['permissions'] ?? null) ? $info['permissions'] : [];
        if (empty($permissions['push']) && empty($permissions['admin']) && empty($permissions['maintain'])) {
            throw new RuntimeException('GitHub token does not have write access to the selected repository.');
        }
        $branches = BDH_Core::branches($repo);
        $blocked = !empty($branches);
        $manifest = self::manifest();
        if ($manifest['fileCount'] === 0) { $blocked = true; $reason = 'No Brando-managed source files were found.'; }
        else { $reason = $blocked ? 'The selected GitHub repository is not empty. Use reviewed Push instead.' : ''; }
        $fingerprint = hash_hmac('sha256', wp_json_encode([$repo,$branch,$manifest['hash'],$branches]), wp_salt('auth'));
        set_transient(self::init_key(), [
            'fingerprint'=>$fingerprint,
            'repo'=>$repo,
            'branch'=>$branch,
            'manifestHash'=>$manifest['hash'],
            'blocked'=>$blocked,
        ], 10 * MINUTE_IN_SECONDS);
        return [
            'action'=>'initialize',
            'repo'=>$repo,
            'branch'=>$branch,
            'syncState'=>'github_api_mode',
            'expectedAction'=>$blocked ? 'blocked' : 'prepare_api_baseline',
            'localAhead'=>0,
            'remoteAhead'=>0,
            'dirty'=>false,
            'files'=>$manifest['files'],
            'fileCount'=>$manifest['fileCount'],
            'sizeBytes'=>$manifest['sizeBytes'],
            'truncated'=>$manifest['truncated'],
            'reviewComplete'=>true,
            'blocked'=>$blocked,
            'blockReason'=>$reason,
            'fingerprint'=>$fingerprint,
        ];
    }

    public static function init_execute(string $fingerprint): array {
        $preview = get_transient(self::init_key());
        if (!is_array($preview) || !hash_equals((string)($preview['fingerprint'] ?? ''), $fingerprint)) {
            throw new RuntimeException('Initialization preview expired or changed. Review again.');
        }
        if (!empty($preview['blocked'])) { throw new RuntimeException('This reviewed initialization is blocked.'); }
        $manifest = self::manifest();
        if (!hash_equals((string)$preview['manifestHash'], $manifest['hash'])) {
            throw new RuntimeException('Managed files changed after preview. Review again.');
        }
        self::acquire('api-prepare');
        try {
            BDH_Core::save_selection((string)$preview['repo'], (string)$preview['branch']);
            BDH_Core::save([
                'github_api_mode'=>true,
                'github_api_prepared_at'=>gmdate('c'),
                'github_api_prepared_manifest'=>$manifest['hash'],
            ]);
            delete_transient(self::init_key());
            return [
                'ok'=>true,
                'logs'=>['GitHub API baseline prepared. No remote push was executed.'],
                'commit'=>'API',
                'branch'=>(string)$preview['branch'],
                'repo'=>(string)$preview['repo'],
                'remotePushed'=>false,
            ];
        } finally {
            self::release();
        }
    }

    private static function changed_files(array $before, array $after): array {
        $out = [];
        foreach ($after as $path=>$meta) {
            if (!isset($before[$path])) { $out[] = ['direction'=>'local','status'=>'A','path'=>$path]; }
            elseif (($before[$path]['sha256'] ?? '') !== $meta['sha256']) { $out[] = ['direction'=>'local','status'=>'M','path'=>$path]; }
        }
        foreach ($before as $path=>$meta) {
            if (!isset($after[$path])) { $out[] = ['direction'=>'local','status'=>'D','path'=>$path]; }
        }
        return $out;
    }

    public static function sync_preview(string $action): array {
        $action = sanitize_key($action);
        if ($action !== 'push') {
            return [
                'action'=>$action,
                'repo'=>(string)(BDH_Core::state()['github_repo'] ?? ''),
                'branch'=>(string)(BDH_Core::state()['github_branch'] ?? 'main'),
                'syncState'=>'github_api_mode',
                'expectedAction'=>'blocked',
                'localAhead'=>0,
                'remoteAhead'=>0,
                'dirty'=>false,
                'files'=>[],
                'fileCount'=>0,
                'truncated'=>false,
                'reviewComplete'=>true,
                'blocked'=>true,
                'blockReason'=>'Hostinger API mode currently supports reviewed Push only.',
                'fingerprint'=>'',
            ];
        }

        $state = BDH_Core::state();
        $repo = self::validate_repo((string)($state['github_repo'] ?? ''));
        $branch = self::validate_branch((string)($state['github_branch'] ?? 'main'));
        if (empty($state['github_api_prepared_at']) && empty($state['github_last_sync_commit'])) {
            throw new RuntimeException('Review First Push and prepare the API baseline first.');
        }

        $manifest = self::manifest();
        $remoteHead = self::remote_head($repo, $branch);
        $lastRemote = (string)($state['github_last_sync_commit'] ?? '');

        if ($remoteHead !== '' && $lastRemote === '') {
            return [
                'action'=>'push','repo'=>$repo,'branch'=>$branch,'syncState'=>'remote_changes',
                'expectedAction'=>'blocked','localAhead'=>0,'remoteAhead'=>1,'dirty'=>false,
                'files'=>[],'fileCount'=>0,'truncated'=>false,'reviewComplete'=>true,'blocked'=>true,
                'blockReason'=>'Remote branch already exists but has no trusted Developer Hub baseline.','fingerprint'=>'',
            ];
        }

        if ($remoteHead !== '' && $lastRemote !== '' && !hash_equals($lastRemote, $remoteHead)) {
            return [
                'action'=>'push','repo'=>$repo,'branch'=>$branch,'syncState'=>'remote_changes',
                'expectedAction'=>'blocked','localAhead'=>0,'remoteAhead'=>1,'dirty'=>false,
                'files'=>[],'fileCount'=>0,'truncated'=>false,'reviewComplete'=>true,'blocked'=>true,
                'blockReason'=>'Remote changed since the last Developer Hub push. Review remote changes before pushing.','fingerprint'=>'',
            ];
        }

        $before = is_array($state['github_api_last_map'] ?? null) ? $state['github_api_last_map'] : [];
        $files = self::changed_files($before, $manifest['map']);
        $initial = $remoteHead === '';
        $expected = $initial ? 'api_first_push' : ($files ? 'api_push' : 'noop');
        $fingerprint = hash_hmac('sha256', wp_json_encode([$repo,$branch,$remoteHead,$manifest['hash'],$expected]), wp_salt('auth'));

        set_transient(self::push_key(), [
            'fingerprint'=>$fingerprint,
            'repo'=>$repo,
            'branch'=>$branch,
            'remoteHead'=>$remoteHead,
            'manifestHash'=>$manifest['hash'],
            'expected'=>$expected,
        ], 10 * MINUTE_IN_SECONDS);

        return [
            'action'=>'push',
            'repo'=>$repo,
            'branch'=>$branch,
            'syncState'=>$initial ? 'first_remote_push' : 'local_changes',
            'expectedAction'=>$expected,
            'localAhead'=>$files ? 1 : 0,
            'remoteAhead'=>0,
            'dirty'=>!empty($files),
            'files'=>array_slice($files, 0, 500),
            'fileCount'=>count($files),
            'truncated'=>count($files) > 500,
            'reviewComplete'=>true,
            'blocked'=>false,
            'blockReason'=>'',
            'fingerprint'=>$fingerprint,
        ];
    }

    private static function bootstrap_empty_repo(string $repo, string $branch, array $manifest, string $message): array {
        $info = BDH_Core::github_request('https://api.github.com/repos/' . $repo);
        $defaultBranch = self::validate_branch((string)($info['default_branch'] ?? 'main'));
        if ($branch !== $defaultBranch) {
            throw new RuntimeException('For an empty repository, First Push must use the default branch: ' . $defaultBranch);
        }
        if (empty($manifest['map'])) { throw new RuntimeException('No managed files are available for First Push.'); }

        $preferred = 'wp-content/plugins/brando-developer-hub/brando-developer-hub.php';
        $bootstrapPath = isset($manifest['map'][$preferred]) ? $preferred : (string)array_key_first($manifest['map']);
        $bootstrapMeta = $manifest['map'][$bootstrapPath];

        $bootstrap = self::request('PUT', $repo, self::contents_path($bootstrapPath), [
            'message'=>'[Brando Developer Hub] Repository bootstrap',
            'content'=>base64_encode((string)$bootstrapMeta['content']),
        ]);
        $bootstrapSha = (string)($bootstrap['commit']['sha'] ?? '');
        if ($bootstrapSha === '') { throw new RuntimeException('GitHub did not return the bootstrap commit SHA.'); }

        $partialMap = [$bootstrapPath=>$bootstrapMeta];
        self::save_remote_state($branch, $bootstrapSha, $partialMap, 'bootstrap:' . $manifest['hash']);

        if (count($manifest['map']) === 1) {
            self::save_remote_state($branch, $bootstrapSha, $manifest['map'], $manifest['hash']);
            return [
                'ok'=>true,
                'logs'=>['GitHub repository bootstrapped through Contents API.'],
                'commit'=>substr($bootstrapSha, 0, 12),
                'branch'=>$branch,
                'repo'=>$repo,
                'remotePushed'=>true,
            ];
        }

        $bootstrapCommit = self::request('GET', $repo, '/git/commits/' . rawurlencode($bootstrapSha));
        $baseTree = (string)($bootstrapCommit['tree']['sha'] ?? '');
        if ($baseTree === '') { throw new RuntimeException('GitHub did not return the bootstrap tree SHA.'); }

        $tree = [];
        foreach ($manifest['map'] as $path=>$meta) {
            if ($path === $bootstrapPath) { continue; }
            $tree[] = ['path'=>$path,'mode'=>'100644','type'=>'blob','content'=>$meta['content']];
        }

        $treeResult = self::request('POST', $repo, '/git/trees', ['base_tree'=>$baseTree,'tree'=>$tree]);
        $safe = trim(wp_strip_all_tags($message));
        if ($safe === '') { $safe = '[Brando Developer Hub] Initial WordPress baseline'; }
        if (strlen($safe) > 160) { $safe = substr($safe, 0, 160); }

        $newCommit = self::request('POST', $repo, '/git/commits', [
            'message'=>$safe,
            'tree'=>(string)($treeResult['sha'] ?? ''),
            'parents'=>[$bootstrapSha],
        ]);
        $sha = (string)($newCommit['sha'] ?? '');
        if ($sha === '') { throw new RuntimeException('GitHub did not return the baseline commit SHA.'); }

        self::request('PATCH', $repo, '/git/refs/heads/' . rawurlencode($branch), ['sha'=>$sha,'force'=>false]);
        self::save_remote_state($branch, $sha, $manifest['map'], $manifest['hash']);

        return [
            'ok'=>true,
            'logs'=>['GitHub repository bootstrapped through Contents API.','GitHub API baseline push completed.'],
            'commit'=>substr($sha, 0, 12),
            'branch'=>$branch,
            'repo'=>$repo,
            'remotePushed'=>true,
        ];
    }

    public static function sync_execute(string $action, string $fingerprint, string $message=''): array {
        if ($action !== 'push') { throw new RuntimeException('Hostinger API mode currently supports Push only.'); }

        $preview = get_transient(self::push_key());
        if (!is_array($preview) || !hash_equals((string)($preview['fingerprint'] ?? ''), $fingerprint)) {
            throw new RuntimeException('Push preview expired or changed. Review again.');
        }

        $repo = self::validate_repo((string)$preview['repo']);
        $branch = self::validate_branch((string)$preview['branch']);
        $manifest = self::manifest();

        if (!hash_equals((string)$preview['manifestHash'], $manifest['hash'])) {
            throw new RuntimeException('Managed files changed after preview. Review Push again.');
        }

        $remoteHead = self::remote_head($repo, $branch);
        if (!hash_equals((string)$preview['remoteHead'], $remoteHead)) {
            throw new RuntimeException('Remote changed after preview. Review Push again.');
        }

        if (($preview['expected'] ?? '') === 'noop') {
            return ['ok'=>true,'logs'=>['Already synchronized.'],'commit'=>$remoteHead,'branch'=>$branch,'repo'=>$repo,'remotePushed'=>false];
        }

        self::acquire('api-push');
        try {
            if ($remoteHead === '') {
                $result = self::bootstrap_empty_repo($repo, $branch, $manifest, $message);
                delete_transient(self::push_key());
                return $result;
            }

            $state = BDH_Core::state();
            $before = is_array($state['github_api_last_map'] ?? null) ? $state['github_api_last_map'] : [];
            $commit = self::request('GET', $repo, '/git/commits/' . rawurlencode($remoteHead));
            $baseTree = (string)($commit['tree']['sha'] ?? '');
            if ($baseTree === '') { throw new RuntimeException('GitHub did not return the current tree SHA.'); }

            $tree = [];
            foreach ($manifest['map'] as $path=>$meta) {
                if (!isset($before[$path]) || ($before[$path]['sha256'] ?? '') !== $meta['sha256']) {
                    $tree[] = ['path'=>$path,'mode'=>'100644','type'=>'blob','content'=>$meta['content']];
                }
            }
            foreach ($before as $path=>$meta) {
                if (!isset($manifest['map'][$path])) { $tree[] = ['path'=>$path,'mode'=>'100644','type'=>'blob','sha'=>null]; }
            }

            if (!$tree) {
                return ['ok'=>true,'logs'=>['Already synchronized.'],'commit'=>$remoteHead,'branch'=>$branch,'repo'=>$repo,'remotePushed'=>false];
            }

            $treeResult = self::request('POST', $repo, '/git/trees', ['base_tree'=>$baseTree,'tree'=>$tree]);

            $safe = trim(wp_strip_all_tags($message));
            if ($safe === '') { $safe = 'Brando Developer Hub sync ' . gmdate('Y-m-d H:i:s') . ' UTC'; }
            if (strlen($safe) > 160) { $safe = substr($safe, 0, 160); }

            $newCommit = self::request('POST', $repo, '/git/commits', [
                'message'=>$safe,
                'tree'=>(string)($treeResult['sha'] ?? ''),
                'parents'=>[$remoteHead],
            ]);
            $sha = (string)($newCommit['sha'] ?? '');
            if ($sha === '') { throw new RuntimeException('GitHub did not return a commit SHA.'); }

            self::request('PATCH', $repo, '/git/refs/heads/' . rawurlencode($branch), ['sha'=>$sha,'force'=>false]);
            self::save_remote_state($branch, $sha, $manifest['map'], $manifest['hash']);
            delete_transient(self::push_key());

            return [
                'ok'=>true,
                'logs'=>['GitHub API push completed.'],
                'commit'=>substr($sha, 0, 12),
                'branch'=>$branch,
                'repo'=>$repo,
                'remotePushed'=>true,
            ];
        } finally {
            self::release();
        }
    }
}
