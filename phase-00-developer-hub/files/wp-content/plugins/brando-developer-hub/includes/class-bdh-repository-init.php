<?php
if (!defined('ABSPATH')) { exit; }

final class BDH_Repository_Init {
    private const PREVIEW_PREFIX = 'bdh_repo_init_preview_';
    private const LOCK_TRANSIENT = 'bdh_git_operation_lock';
    private const INITIAL_COMMIT_PREFIX = '[Brando Developer Hub] Initial WordPress baseline';
    private const MAX_PREVIEW_FILES = 300;
    private const MAX_SCAN_FILES = 20000;
    private const MAX_SCAN_BYTES = 536870912;

    private static function validate_repo(string $repo): string {
        $repo = trim($repo);
        if (!preg_match('/^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/', $repo)) {
            throw new RuntimeException('Invalid GitHub repository.');
        }
        return $repo;
    }

    private static function validate_branch(string $branch): string {
        $branch = trim($branch) ?: 'main';
        if (!preg_match('/^[A-Za-z0-9._\/-]+$/', $branch) || str_contains($branch, '..') || str_starts_with($branch, '/') || str_ends_with($branch, '/')) {
            throw new RuntimeException('Invalid branch.');
        }
        return $branch;
    }

    private static function root(): string { return BDH_Core::repo_root(); }
    private static function git_dir(): string { return self::root() . DIRECTORY_SEPARATOR . '.git'; }

    private static function is_wordpress_root(): bool {
        $root = self::root();
        return is_file($root . '/wp-load.php') && is_dir($root . '/wp-content');
    }

    private static function expected_remote(string $repo): string { return 'https://github.com/' . $repo . '.git'; }

    private static function normalize_remote_repo(string $url): string {
        $url = trim($url);
        if ($url === '') { return ''; }
        if (preg_match('#^git@github\.com:([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+?)(?:\.git)?$#', $url, $m)) { return strtolower($m[1]); }
        if (preg_match('#^ssh://git@github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+?)(?:\.git)?$#', $url, $m)) { return strtolower($m[1]); }
        $parts = wp_parse_url($url);
        if (!is_array($parts) || strtolower((string)($parts['host'] ?? '')) !== 'github.com' || isset($parts['user']) || isset($parts['pass'])) { return ''; }
        $path = trim((string)($parts['path'] ?? ''), '/');
        $path = preg_replace('/\.git$/i', '', $path) ?? $path;
        return preg_match('/^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/', $path) ? strtolower($path) : '';
    }

    private static function git_env(): array {
        $env = $_ENV;
        $env['GIT_TERMINAL_PROMPT'] = '0';
        $env['LC_ALL'] = 'C';
        $env['GIT_AUTHOR_NAME'] = 'Brando Developer Hub';
        $env['GIT_AUTHOR_EMAIL'] = 'developer-hub@brando.local';
        $env['GIT_COMMITTER_NAME'] = 'Brando Developer Hub';
        $env['GIT_COMMITTER_EMAIL'] = 'developer-hub@brando.local';
        $token = BDH_Core::github_token();
        if ($token !== '') {
            $env['GIT_CONFIG_COUNT'] = '1';
            $env['GIT_CONFIG_KEY_0'] = 'http.https://github.com/.extraheader';
            $env['GIT_CONFIG_VALUE_0'] = 'AUTHORIZATION: basic ' . base64_encode('x-access-token:' . $token);
        }
        return $env;
    }

    private static function run(array $args, int $timeout = 120, bool $allow_without_git = false): array {
        if (!$allow_without_git && !is_dir(self::git_dir())) { throw new RuntimeException('WordPress root is not a Git repository.'); }
        $allowed = ['init','status','branch','rev-parse','log','remote','add','commit','push','diff'];
        $subcommand = (string)($args[0] ?? '');
        if (!in_array($subcommand, $allowed, true)) { throw new RuntimeException('Blocked Git command.'); }
        foreach ($args as $arg) {
            if (!is_string($arg) || str_contains($arg, "\0") || str_contains($arg, "\n") || str_contains($arg, "\r")) { throw new RuntimeException('Invalid Git argument.'); }
        }
        if (!function_exists('proc_open')) { throw new RuntimeException('proc_open is required for Developer Hub repository initialization.'); }
        $cmd = array_merge(['git', '-C', self::root()], $args);
        $process = proc_open($cmd, [1=>['pipe','w'], 2=>['pipe','w']], $pipes, self::root(), self::git_env(), ['bypass_shell'=>true]);
        if (!is_resource($process)) { throw new RuntimeException('Unable to start Git process.'); }
        stream_set_blocking($pipes[1], false);
        stream_set_blocking($pipes[2], false);
        $stdout = ''; $stderr = ''; $started = time(); $status = [];
        while (true) {
            $status = proc_get_status($process);
            $stdout .= stream_get_contents($pipes[1]);
            $stderr .= stream_get_contents($pipes[2]);
            if (!$status['running']) { break; }
            if ((time() - $started) > $timeout) {
                proc_terminate($process, 15); usleep(200000); proc_terminate($process, 9);
                fclose($pipes[1]); fclose($pipes[2]); proc_close($process);
                throw new RuntimeException('Git operation timed out.');
            }
            usleep(100000);
        }
        $stdout .= stream_get_contents($pipes[1]); $stderr .= stream_get_contents($pipes[2]);
        fclose($pipes[1]); fclose($pipes[2]);
        $code = proc_close($process);
        if ($code === -1 && isset($status['exitcode']) && $status['exitcode'] >= 0) { $code = (int)$status['exitcode']; }
        $stdout = trim(BDH_Core::redact($stdout));
        $stderr = trim(BDH_Core::redact($stderr));
        if ($code !== 0) { throw new RuntimeException($stderr !== '' ? $stderr : 'Git command failed.'); }
        return ['stdout'=>$stdout, 'stderr'=>$stderr, 'code'=>$code];
    }

    private static function has_commit(): bool {
        if (!is_dir(self::git_dir())) { return false; }
        try { self::run(['rev-parse', '--verify', 'HEAD']); return true; }
        catch (Throwable) { return false; }
    }

    private static function current_branch(): string {
        if (!is_dir(self::git_dir())) { return ''; }
        try { return trim(self::run(['branch', '--show-current'])['stdout']); }
        catch (Throwable) { return ''; }
    }

    private static function last_commit_subject(): string {
        if (!self::has_commit()) { return ''; }
        try { return trim(self::run(['log', '-1', '--pretty=%s'])['stdout']); }
        catch (Throwable) { return ''; }
    }

    private static function origin_url(): string {
        if (!is_dir(self::git_dir())) { return ''; }
        try { return trim(self::run(['remote', 'get-url', 'origin'])['stdout']); }
        catch (Throwable) { return ''; }
    }

    private static function is_excluded(string $relative): bool {
        $relative = ltrim(str_replace('\\', '/', $relative), '/');
        if ($relative === '' || $relative === '.git' || str_starts_with($relative, '.git/')) { return true; }
        if ($relative === 'wp-config.php' || $relative === '.env' || str_starts_with($relative, '.env.')) { return true; }
        if (preg_match('/(^|\/)(\.DS_Store|Thumbs\.db)$/i', $relative) || preg_match('/\.log$/i', $relative)) { return true; }
        $prefixes = ['wp-content/uploads/','wp-content/cache/','wp-content/litespeed/','wp-content/upgrade/','wp-content/ai1wm-backups/','wp-content/backups/','wp-content/updraft/','wp-content/wflogs/','wp-content/et-cache/','node_modules/','vendor/','.idea/','.vscode/'];
        foreach ($prefixes as $prefix) { if (str_starts_with($relative, $prefix)) { return true; } }
        return false;
    }

    private static function scan_manifest(): array {
        $root = self::root();
        $files = []; $preview = []; $total_bytes = 0;
        $iterator = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($root, FilesystemIterator::SKIP_DOTS));
        foreach ($iterator as $entry) {
            if (!$entry->isFile() || $entry->isLink()) { continue; }
            $full = str_replace('\\', '/', $entry->getPathname());
            $relative = ltrim(str_replace(str_replace('\\', '/', $root), '', $full), '/');
            if (self::is_excluded($relative)) { continue; }
            $size = (int)$entry->getSize();
            $total_bytes += $size;
            if ($total_bytes > self::MAX_SCAN_BYTES) { throw new RuntimeException('Initial baseline exceeds the 512 MB safety limit after exclusions.'); }
            $digest = hash_file('sha256', $entry->getPathname());
            if (!is_string($digest)) { throw new RuntimeException('Failed to fingerprint a WordPress file.'); }
            $files[] = $relative . ':' . $size . ':' . $digest;
            if (count($files) > self::MAX_SCAN_FILES) { throw new RuntimeException('Initial baseline contains too many files for a safe reviewed first push.'); }
            if (count($preview) < self::MAX_PREVIEW_FILES) { $preview[] = ['direction'=>'local', 'status'=>'A', 'path'=>$relative]; }
        }
        sort($files, SORT_STRING);
        return ['hash'=>hash('sha256', implode("\n", $files)), 'fileCount'=>count($files), 'sizeBytes'=>$total_bytes, 'files'=>$preview, 'truncated'=>count($files) > self::MAX_PREVIEW_FILES];
    }

    private static function remote_snapshot(string $repo): array {
        [$owner, $name] = explode('/', $repo, 2);
        $info = BDH_Core::github_request('https://api.github.com/repos/' . rawurlencode($owner) . '/' . rawurlencode($name));
        $permissions = is_array($info['permissions'] ?? null) ? $info['permissions'] : [];
        if (empty($permissions['push']) && empty($permissions['admin']) && empty($permissions['maintain'])) {
            throw new RuntimeException('The verified GitHub token does not have write access to the selected repository.');
        }
        $branches = BDH_Core::branches($repo);
        return ['branches'=>$branches, 'defaultBranch'=>(string)($info['default_branch'] ?? 'main')];
    }

    private static function preview_key(): string { return self::PREVIEW_PREFIX . get_current_user_id(); }
    private static function fingerprint(array $data): string { return hash_hmac('sha256', wp_json_encode($data), wp_salt('auth')); }

    public static function preview(string $repo, string $branch = 'main'): array {
        if (!self::is_wordpress_root()) { throw new RuntimeException('Developer Hub is not running from a valid WordPress root.'); }
        if (BDH_Core::github_token() === '') { throw new RuntimeException('Verify the GitHub token first.'); }
        $repo = self::validate_repo($repo);
        $branch = self::validate_branch($branch);
        $remote = self::remote_snapshot($repo);
        $remote_branches = array_values(array_filter(array_map('strval', $remote['branches'] ?? [])));
        $blocked = false; $reason = '';
        if ($remote_branches) { $blocked = true; $reason = 'The selected GitHub repository is not empty. Use normal reviewed Push/Pull/Sync instead of First Push.'; }
        $git_exists = is_dir(self::git_dir());
        $has_commit = self::has_commit();
        $local_branch = self::current_branch();
        $last_subject = self::last_commit_subject();
        if ($git_exists && !$has_commit) { $blocked = true; $reason = 'An existing Git repository with no commits was found. Review the server Git metadata before initialization.'; }
        if ($has_commit && !str_starts_with($last_subject, self::INITIAL_COMMIT_PREFIX)) { $blocked = true; $reason = 'Existing local Git history was not created by Brando Developer Hub. First Push will not modify it.'; }
        if ($has_commit && $local_branch !== '' && $local_branch !== $branch) { $blocked = true; $reason = 'The existing Brando baseline is on a different local branch.'; }
        $origin = self::origin_url();
        if ($origin !== '' && self::normalize_remote_repo($origin) !== strtolower($repo)) { $blocked = true; $reason = 'Existing origin points to a different repository. First Push will not replace it.'; }
        if ($has_commit && trim(self::run(['status', '--porcelain=v1'])['stdout']) !== '') { $blocked = true; $reason = 'The existing Brando baseline has local changes. Review them before retrying First Push.'; }
        $manifest = self::scan_manifest();
        $expected = $has_commit ? 'push_existing_baseline' : 'initialize_commit_push';
        $fingerprint_data = ['repo'=>$repo,'branch'=>$branch,'manifest'=>$manifest['hash'],'gitExists'=>$git_exists,'hasCommit'=>$has_commit,'lastSubject'=>$last_subject,'origin'=>self::normalize_remote_repo($origin),'remoteBranches'=>$remote_branches,'expected'=>$expected];
        $fingerprint = self::fingerprint($fingerprint_data);
        set_transient(self::preview_key(), ['fingerprint'=>$fingerprint,'repo'=>$repo,'branch'=>$branch,'manifest'=>$manifest['hash'],'expected'=>$expected,'blocked'=>$blocked], 10 * MINUTE_IN_SECONDS);
        return ['action'=>'initialize','repo'=>$repo,'branch'=>$branch,'syncState'=>'first_push','expectedAction'=>$blocked ? 'blocked' : $expected,'localAhead'=>$has_commit ? 1 : 0,'remoteAhead'=>0,'dirty'=>false,'files'=>$manifest['files'],'fileCount'=>$manifest['fileCount'],'sizeBytes'=>$manifest['sizeBytes'],'truncated'=>$manifest['truncated'],'reviewComplete'=>true,'blocked'=>$blocked,'blockReason'=>$reason,'fingerprint'=>$fingerprint];
    }

    private static function managed_gitignore_block(): string {
        return "# BEGIN Brando Developer Hub managed ignores\nwp-config.php\n.env\n.env.*\n!.env.example\n/wp-content/uploads/\n/wp-content/cache/\n/wp-content/litespeed/\n/wp-content/upgrade/\n/wp-content/ai1wm-backups/\n/wp-content/backups/\n/wp-content/updraft/\n/wp-content/wflogs/\n/wp-content/et-cache/\n*.log\n.DS_Store\nThumbs.db\n/.idea/\n/.vscode/\n/node_modules/\n/vendor/\n# END Brando Developer Hub managed ignores\n";
    }

    private static function ensure_gitignore(): array {
        $path = self::root() . '/.gitignore';
        $exists = is_file($path);
        $before = $exists ? (string)file_get_contents($path) : '';
        if (str_contains($before, '# BEGIN Brando Developer Hub managed ignores')) { return ['path'=>$path, 'existed'=>$exists, 'before'=>$before, 'changed'=>false]; }
        $prefix = $before === '' ? '' : rtrim($before, "\r\n") . "\n\n";
        if (file_put_contents($path, $prefix . self::managed_gitignore_block(), LOCK_EX) === false) { throw new RuntimeException('Failed to write the safe WordPress .gitignore.'); }
        return ['path'=>$path, 'existed'=>$exists, 'before'=>$before, 'changed'=>true];
    }

    private static function restore_gitignore(array $backup): void {
        if (empty($backup['changed'])) { return; }
        $path = (string)($backup['path'] ?? '');
        if ($path === '') { return; }
        if (!empty($backup['existed'])) { @file_put_contents($path, (string)($backup['before'] ?? ''), LOCK_EX); }
        else { @unlink($path); }
    }

    private static function acquire_lock(): void {
        if (get_transient(self::LOCK_TRANSIENT)) { throw new RuntimeException('Another GitHub operation is already running.'); }
        set_transient(self::LOCK_TRANSIENT, ['user'=>get_current_user_id(), 'at'=>time(), 'type'=>'repository-init'], 15 * MINUTE_IN_SECONDS);
    }
    private static function release_lock(): void { delete_transient(self::LOCK_TRANSIENT); }

    private static function remove_new_git_dir(): void {
        $dir = self::git_dir();
        if (!is_dir($dir)) { return; }
        $real_root = realpath(self::root()); $real_git = realpath($dir);
        if (!$real_root || !$real_git || dirname($real_git) !== $real_root || basename($real_git) !== '.git') { return; }
        $iterator = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($real_git, FilesystemIterator::SKIP_DOTS), RecursiveIteratorIterator::CHILD_FIRST);
        foreach ($iterator as $entry) {
            if ($entry->isLink() || $entry->isFile()) { @unlink($entry->getPathname()); }
            elseif ($entry->isDir()) { @rmdir($entry->getPathname()); }
        }
        @rmdir($real_git);
    }

    private static function ensure_origin(string $repo): void {
        $origin = self::origin_url();
        if ($origin === '') { self::run(['remote', 'add', 'origin', self::expected_remote($repo)]); return; }
        if (self::normalize_remote_repo($origin) !== strtolower($repo)) { throw new RuntimeException('Existing origin points to a different repository.'); }
    }

    public static function execute(string $fingerprint, string $message = ''): array {
        $preview = get_transient(self::preview_key());
        if (!is_array($preview) || !hash_equals((string)($preview['fingerprint'] ?? ''), $fingerprint)) { throw new RuntimeException('First Push preview expired or changed. Review again before execution.'); }
        if (!empty($preview['blocked'])) { throw new RuntimeException('This reviewed First Push operation is blocked.'); }
        $repo = self::validate_repo((string)($preview['repo'] ?? ''));
        $branch = self::validate_branch((string)($preview['branch'] ?? 'main'));
        if (BDH_Core::github_token() === '') { throw new RuntimeException('Verify the GitHub token first.'); }
        self::acquire_lock();
        $created_git = false; $commit_created = false; $gitignore_backup = ['changed'=>false];
        try {
            $remote = self::remote_snapshot($repo);
            if (!empty($remote['branches'])) { throw new RuntimeException('Remote repository changed after preview and is no longer empty. Review again.'); }
            $manifest = self::scan_manifest();
            if (!hash_equals((string)($preview['manifest'] ?? ''), (string)$manifest['hash'])) { throw new RuntimeException('WordPress files changed after preview. Review First Push again.'); }
            $has_commit = self::has_commit();
            if ($has_commit) {
                $subject = self::last_commit_subject();
                if (!str_starts_with($subject, self::INITIAL_COMMIT_PREFIX)) { throw new RuntimeException('Existing local Git history is not a Brando Developer Hub baseline.'); }
                if (trim(self::run(['status', '--porcelain=v1'])['stdout']) !== '') { throw new RuntimeException('Local files changed after the baseline commit. Review before First Push.'); }
            } else {
                if (is_dir(self::git_dir())) { throw new RuntimeException('An existing Git repository with no commits requires manual review.'); }
                self::run(['init', '-b', $branch], 120, true);
                $created_git = true;
                self::ensure_origin($repo);
                $gitignore_backup = self::ensure_gitignore();
                self::run(['add', '--all']);
                if (trim(self::run(['status', '--porcelain=v1'])['stdout']) === '') { throw new RuntimeException('No safe WordPress files are available for the initial baseline commit.'); }
                $safe = trim(wp_strip_all_tags($message));
                if ($safe === '') { $safe = self::INITIAL_COMMIT_PREFIX; }
                elseif (!str_starts_with($safe, self::INITIAL_COMMIT_PREFIX)) { $safe = self::INITIAL_COMMIT_PREFIX . ' — ' . $safe; }
                if (strlen($safe) > 160) { $safe = substr($safe, 0, 160); }
                self::run(['commit', '-m', $safe], 300);
                $commit_created = true;
            }
            self::ensure_origin($repo);
            if (self::current_branch() !== $branch) { self::run(['branch', '-M', $branch]); }
            $push = self::run(['push', '-u', 'origin', 'HEAD:' . $branch], 600);
            delete_transient(self::preview_key());
            BDH_Core::save_selection($repo, $branch);
            $local = BDH_Core::local_status();
            BDH_Core::save(['github_default_branch'=>$branch,'github_last_sync_at'=>gmdate('c'),'github_last_sync_commit'=>$local['shortSha'] ?? null,'github_last_sync_by'=>wp_get_current_user()->user_login]);
            return ['ok'=>true,'logs'=>array_values(array_filter([$commit_created ? 'Initial WordPress baseline committed locally.' : 'Existing Brando baseline reused.',$push['stdout'] ?: $push['stderr']])),'commit'=>(string)($local['shortSha'] ?? ''),'branch'=>$branch,'repo'=>$repo];
        } catch (Throwable $e) {
            if ($created_git && !$commit_created) { self::restore_gitignore($gitignore_backup); self::remove_new_git_dir(); }
            throw $e;
        } finally { self::release_lock(); }
    }
}
