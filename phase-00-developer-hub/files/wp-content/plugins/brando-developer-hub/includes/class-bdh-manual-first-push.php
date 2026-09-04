<?php
if (!defined('ABSPATH')) { exit; }

final class BDH_Manual_First_Push {
    private const LOCK_TRANSIENT = 'bdh_git_operation_lock';
    private const PUSH_PREVIEW_PREFIX = 'bdh_manual_first_push_';
    private const INITIAL_COMMIT_PREFIX = '[Brando Developer Hub] Initial WordPress baseline';

    private static function root(): string { return BDH_Core::repo_root(); }
    private static function git_dir(): string { return self::root() . DIRECTORY_SEPARATOR . '.git'; }

    private static function validate_repo(string $repo): string {
        $repo = trim($repo);
        if (!preg_match('/^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/', $repo)) { throw new RuntimeException('Invalid GitHub repository.'); }
        return $repo;
    }

    private static function validate_branch(string $branch): string {
        $branch = trim($branch) ?: 'main';
        if (!preg_match('/^[A-Za-z0-9._\/-]+$/', $branch) || str_contains($branch, '..') || str_starts_with($branch, '/') || str_ends_with($branch, '/')) {
            throw new RuntimeException('Invalid branch.');
        }
        return $branch;
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
        $allowed = ['init','status','branch','rev-parse','log','remote','add','commit','push'];
        $subcommand = (string)($args[0] ?? '');
        if (!in_array($subcommand, $allowed, true)) { throw new RuntimeException('Blocked Git command.'); }
        foreach ($args as $arg) {
            if (!is_string($arg) || str_contains($arg, "\0") || str_contains($arg, "\n") || str_contains($arg, "\r")) { throw new RuntimeException('Invalid Git argument.'); }
        }
        if (!function_exists('proc_open')) { throw new RuntimeException('proc_open is required for Developer Hub Git operations.'); }
        $cmd = array_merge(['git', '-C', self::root()], $args);
        $process = proc_open($cmd, [1=>['pipe','w'],2=>['pipe','w']], $pipes, self::root(), self::git_env(), ['bypass_shell'=>true]);
        if (!is_resource($process)) { throw new RuntimeException('Unable to start Git process.'); }
        stream_set_blocking($pipes[1], false); stream_set_blocking($pipes[2], false);
        $stdout=''; $stderr=''; $started=time(); $status=[];
        while (true) {
            $status=proc_get_status($process);
            $stdout.=stream_get_contents($pipes[1]); $stderr.=stream_get_contents($pipes[2]);
            if (!$status['running']) { break; }
            if ((time()-$started)>$timeout) {
                proc_terminate($process,15); usleep(200000); proc_terminate($process,9);
                fclose($pipes[1]); fclose($pipes[2]); proc_close($process);
                throw new RuntimeException('Git operation timed out.');
            }
            usleep(100000);
        }
        $stdout.=stream_get_contents($pipes[1]); $stderr.=stream_get_contents($pipes[2]);
        fclose($pipes[1]); fclose($pipes[2]);
        $code=proc_close($process);
        if ($code===-1 && isset($status['exitcode']) && $status['exitcode']>=0) { $code=(int)$status['exitcode']; }
        $stdout=trim(BDH_Core::redact($stdout)); $stderr=trim(BDH_Core::redact($stderr));
        if ($code!==0) { throw new RuntimeException($stderr !== '' ? $stderr : 'Git command failed.'); }
        return ['stdout'=>$stdout,'stderr'=>$stderr,'code'=>$code];
    }

    private static function has_commit(): bool {
        if (!is_dir(self::git_dir())) { return false; }
        try { self::run(['rev-parse','--verify','HEAD']); return true; } catch (Throwable) { return false; }
    }

    private static function current_branch(): string {
        if (!is_dir(self::git_dir())) { return ''; }
        try { return trim(self::run(['branch','--show-current'])['stdout']); } catch (Throwable) { return ''; }
    }

    private static function origin_url(): string {
        if (!is_dir(self::git_dir())) { return ''; }
        try { return trim(self::run(['remote','get-url','origin'])['stdout']); } catch (Throwable) { return ''; }
    }

    private static function ensure_origin(string $repo): void {
        $origin=self::origin_url();
        if ($origin==='') { self::run(['remote','add','origin',self::expected_remote($repo)]); return; }
        if (self::normalize_remote_repo($origin)!==strtolower($repo)) { throw new RuntimeException('Existing origin points to a different repository.'); }
    }

    private static function managed_gitignore_block(): string {
        return "# BEGIN Brando Developer Hub managed ignores\nwp-config.php\n.env\n.env.*\n!.env.example\n/wp-content/uploads/\n/wp-content/cache/\n/wp-content/litespeed/\n/wp-content/upgrade/\n/wp-content/ai1wm-backups/\n/wp-content/backups/\n/wp-content/updraft/\n/wp-content/wflogs/\n/wp-content/et-cache/\n*.log\n.DS_Store\nThumbs.db\n/.idea/\n/.vscode/\n/node_modules/\n/vendor/\n# END Brando Developer Hub managed ignores\n";
    }

    private static function ensure_gitignore(): void {
        $path=self::root().'/.gitignore';
        $before=is_file($path)?(string)file_get_contents($path):'';
        if (str_contains($before,'# BEGIN Brando Developer Hub managed ignores')) { return; }
        $prefix=$before===''?'':rtrim($before,"\r\n")."\n\n";
        if (file_put_contents($path,$prefix.self::managed_gitignore_block(),LOCK_EX)===false) { throw new RuntimeException('Failed to write the safe WordPress .gitignore.'); }
    }

    private static function acquire_lock(string $type): void {
        if (get_transient(self::LOCK_TRANSIENT)) { throw new RuntimeException('Another GitHub operation is already running.'); }
        set_transient(self::LOCK_TRANSIENT,['user'=>get_current_user_id(),'at'=>time(),'type'=>$type],15*MINUTE_IN_SECONDS);
    }
    private static function release_lock(): void { delete_transient(self::LOCK_TRANSIENT); }

    private static function push_preview_key(): string { return self::PUSH_PREVIEW_PREFIX . get_current_user_id(); }

    public static function prepare_local(string $fingerprint, string $message=''): array {
        $state=BDH_Core::state();
        $repo=self::validate_repo((string)($state['github_repo'] ?? ''));
        $branch=self::validate_branch((string)($state['github_branch'] ?? 'main'));
        $review=BDH_Repository_Init::preview($repo,$branch);
        if (!hash_equals((string)($review['fingerprint'] ?? ''),$fingerprint)) { throw new RuntimeException('Initialization preview expired or changed. Review again before execution.'); }
        if (!empty($review['blocked'])) { throw new RuntimeException((string)($review['blockReason'] ?: 'This reviewed initialization is blocked.')); }

        self::acquire_lock('repository-prepare');
        try {
            if (!self::has_commit()) {
                if (is_dir(self::git_dir())) { throw new RuntimeException('An existing Git repository with no commits requires manual review.'); }
                self::run(['init','-b',$branch],120,true);
                self::ensure_origin($repo);
                self::ensure_gitignore();
                self::run(['add','--all']);
                if (trim(self::run(['status','--porcelain=v1'])['stdout'])==='') { throw new RuntimeException('No safe WordPress files are available for the initial baseline commit.'); }
                $safe=trim(wp_strip_all_tags($message));
                if ($safe==='') { $safe=self::INITIAL_COMMIT_PREFIX; }
                elseif (!str_starts_with($safe,self::INITIAL_COMMIT_PREFIX)) { $safe=self::INITIAL_COMMIT_PREFIX.' — '.$safe; }
                if (strlen($safe)>160) { $safe=substr($safe,0,160); }
                self::run(['commit','-m',$safe],300);
            }
            self::ensure_origin($repo);
            if (self::current_branch()!==$branch) { self::run(['branch','-M',$branch]); }
            if (trim(self::run(['status','--porcelain=v1'])['stdout'])!=='') { throw new RuntimeException('Local baseline is not clean after initialization.'); }
            $sha=trim(self::run(['rev-parse','--short','HEAD'])['stdout']);
            BDH_Core::save_selection($repo,$branch);
            BDH_Core::save(['github_default_branch'=>$branch,'github_local_baseline_commit'=>$sha,'github_local_prepared_at'=>gmdate('c')]);
            return ['ok'=>true,'logs'=>['Local Git baseline prepared. No GitHub push was executed.'],'commit'=>$sha,'branch'=>$branch,'repo'=>$repo,'remotePushed'=>false];
        } finally { self::release_lock(); }
    }

    public static function preview_manual_push(string $action): ?array {
        if ($action!=='push' || !is_dir(self::git_dir()) || !self::has_commit()) { return null; }
        $state=BDH_Core::state();
        $repo=self::validate_repo((string)($state['github_repo'] ?? ''));
        $branch=self::validate_branch((string)($state['github_branch'] ?? self::current_branch() ?: 'main'));
        $branches=BDH_Core::branches($repo);
        if (in_array($branch,$branches,true)) { return null; }
        if ($branches) {
            return ['action'=>'push','repo'=>$repo,'branch'=>$branch,'syncState'=>'remote_branch_missing','expectedAction'=>'blocked','localAhead'=>0,'remoteAhead'=>0,'dirty'=>false,'files'=>[],'fileCount'=>0,'truncated'=>false,'reviewComplete'=>true,'blocked'=>true,'blockReason'=>'The remote repository is not empty, but the selected branch does not exist. Review the remote repository before creating a new branch.','fingerprint'=>''];
        }
        if (self::normalize_remote_repo(self::origin_url())!==strtolower($repo)) { throw new RuntimeException('Local origin does not match the selected GitHub repository.'); }
        if (self::current_branch()!==$branch) { throw new RuntimeException('Local branch does not match the selected GitHub branch.'); }
        $dirty_raw=self::run(['status','--porcelain=v1'])['stdout'];
        $dirty=$dirty_raw!=='';
        $sha=trim(self::run(['rev-parse','--short','HEAD'])['stdout']);
        $files=[];
        foreach (preg_split('/\R/',$dirty_raw) ?: [] as $line) {
            if ($line==='') continue;
            $files[]=['direction'=>'local','status'=>substr($line,0,2),'path'=>trim(substr($line,3))];
            if (count($files)>=500) break;
        }
        $expected=$dirty?'commit_and_first_push':'first_push';
        $fingerprint=hash_hmac('sha256',wp_json_encode([$repo,$branch,$sha,$dirty_raw,$expected]),wp_salt('auth'));
        set_transient(self::push_preview_key(),['fingerprint'=>$fingerprint,'repo'=>$repo,'branch'=>$branch,'sha'=>$sha,'dirtyRaw'=>$dirty_raw,'expected'=>$expected],10*MINUTE_IN_SECONDS);
        return ['action'=>'push','repo'=>$repo,'branch'=>$branch,'syncState'=>'first_remote_push','expectedAction'=>$expected,'localAhead'=>1,'remoteAhead'=>0,'dirty'=>$dirty,'files'=>$files,'fileCount'=>count($files),'truncated'=>count($files)>=500,'reviewComplete'=>true,'blocked'=>false,'blockReason'=>'','fingerprint'=>$fingerprint];
    }

    public static function execute_manual_push_if_matching(string $fingerprint,string $message=''): ?array {
        $preview=get_transient(self::push_preview_key());
        if (!is_array($preview) || !hash_equals((string)($preview['fingerprint'] ?? ''),$fingerprint)) { return null; }
        self::acquire_lock('manual-first-push');
        try {
            $repo=self::validate_repo((string)$preview['repo']);
            $branch=self::validate_branch((string)$preview['branch']);
            if (BDH_Core::branches($repo)) { throw new RuntimeException('Remote repository changed after preview. Review Push again.'); }
            if (self::normalize_remote_repo(self::origin_url())!==strtolower($repo) || self::current_branch()!==$branch) { throw new RuntimeException('Local repository selection changed after preview.'); }
            $sha=trim(self::run(['rev-parse','--short','HEAD'])['stdout']);
            $dirty_raw=self::run(['status','--porcelain=v1'])['stdout'];
            if (!hash_equals((string)$preview['sha'],$sha) || !hash_equals((string)$preview['dirtyRaw'],$dirty_raw)) { throw new RuntimeException('Local files changed after preview. Review Push again.'); }
            $logs=[];
            if ($dirty_raw!=='') {
                self::run(['add','--all']);
                $safe=trim(wp_strip_all_tags($message));
                if ($safe==='') { $safe='Brando Developer Hub first push '.gmdate('Y-m-d H:i:s').' UTC'; }
                if (strlen($safe)>160) { $safe=substr($safe,0,160); }
                $logs[]=self::run(['commit','-m',$safe],300)['stdout'];
            }
            $push=self::run(['push','-u','origin','HEAD:'.$branch],600);
            $logs[]=$push['stdout'] ?: $push['stderr'];
            delete_transient(self::push_preview_key());
            $sha=trim(self::run(['rev-parse','--short','HEAD'])['stdout']);
            BDH_Core::save(['github_default_branch'=>$branch,'github_last_sync_at'=>gmdate('c'),'github_last_sync_commit'=>$sha,'github_last_sync_by'=>wp_get_current_user()->user_login]);
            return ['ok'=>true,'logs'=>array_values(array_filter(array_map([BDH_Core::class,'redact'],$logs))),'commit'=>$sha,'branch'=>$branch,'repo'=>$repo,'remotePushed'=>true];
        } finally { self::release_lock(); }
    }
}
