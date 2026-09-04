<?php
if (!defined('ABSPATH')) { exit; }

final class BDH_Core {
    private const STATE_OPTION = 'bdh_state_v1';
    private const LOCK_TRANSIENT = 'bdh_git_operation_lock';
    private const MAX_PREVIEW_FILES = 500;

    public static function ensure_defaults(): array {
        $state = get_option(self::STATE_OPTION, []);
        if (!is_array($state)) { $state = []; }
        $defaults = [
            'mcp_enabled' => false,
            'github_token_encrypted' => null,
            'github_repo' => '',
            'github_branch' => 'main',
            'github_default_branch' => null,
            'github_verified_at' => null,
            'github_login' => null,
            'github_permission' => null,
            'github_push_mode' => 'review',
            'github_last_sync_at' => null,
            'github_last_sync_commit' => null,
            'github_last_sync_by' => null,
            'latest_context_generated_at' => null,
            'ai_access_token' => wp_generate_password(48, false, false),
            'webhook_secret' => wp_generate_password(64, false, false),
            'updated_at' => gmdate('c'),
        ];
        $merged = array_merge($defaults, $state);
        update_option(self::STATE_OPTION, $merged, false);
        return $merged;
    }

    public static function state(): array { return self::ensure_defaults(); }

    public static function save(array $patch): array {
        $state = array_merge(self::state(), $patch, ['updated_at' => gmdate('c')]);
        update_option(self::STATE_OPTION, $state, false);
        return $state;
    }

    private static function encryption_key(): string {
        $material = (defined('AUTH_KEY') ? AUTH_KEY : '') . '|' . (defined('SECURE_AUTH_SALT') ? SECURE_AUTH_SALT : '') . '|brando-developer-hub';
        return hash('sha256', $material, true);
    }

    public static function encrypt_secret(string $plain): array {
        if (!function_exists('openssl_encrypt')) { throw new RuntimeException('OpenSSL is required for encrypted Developer Hub secrets.'); }
        $iv = random_bytes(12); $tag = '';
        $ciphertext = openssl_encrypt($plain, 'aes-256-gcm', self::encryption_key(), OPENSSL_RAW_DATA, $iv, $tag);
        if ($ciphertext === false) { throw new RuntimeException('Failed to encrypt secret.'); }
        return ['version'=>1,'algorithm'=>'aes-256-gcm','iv'=>base64_encode($iv),'tag'=>base64_encode($tag),'ciphertext'=>base64_encode($ciphertext)];
    }

    public static function decrypt_secret(mixed $payload): string {
        if (!is_array($payload) || empty($payload['ciphertext'])) { return ''; }
        if (($payload['version'] ?? null) !== 1 || ($payload['algorithm'] ?? '') !== 'aes-256-gcm') { throw new RuntimeException('Unsupported encrypted token format.'); }
        $plain = openssl_decrypt(base64_decode((string)$payload['ciphertext'], true) ?: '', 'aes-256-gcm', self::encryption_key(), OPENSSL_RAW_DATA, base64_decode((string)$payload['iv'], true) ?: '', base64_decode((string)$payload['tag'], true) ?: '');
        if ($plain === false) { throw new RuntimeException('Failed to decrypt GitHub token.'); }
        return $plain;
    }

    public static function github_token(): string {
        $env = getenv('GITHUB_SYNC_TOKEN');
        if (is_string($env) && trim($env) !== '') { return trim($env); }
        return self::decrypt_secret(self::state()['github_token_encrypted'] ?? null);
    }

    public static function mask_secret(string $value): string {
        if ($value === '') { return ''; }
        if (strlen($value) <= 12) { return '[REDACTED]'; }
        return substr($value, 0, 6) . '••••' . substr($value, -4);
    }

    public static function repo_root(): string {
        $root = realpath(ABSPATH);
        return $root ?: rtrim(ABSPATH, '/\\');
    }

    public static function has_git(): bool { return is_dir(self::repo_root() . DIRECTORY_SEPARATOR . '.git'); }

    private static function git_env(): array {
        $env = $_ENV;
        $env['GIT_TERMINAL_PROMPT'] = '0';
        $env['LC_ALL'] = 'C';
        $token = self::github_token();
        if ($token !== '') {
            $env['GIT_CONFIG_COUNT'] = '1';
            $env['GIT_CONFIG_KEY_0'] = 'http.https://github.com/.extraheader';
            $env['GIT_CONFIG_VALUE_0'] = 'AUTHORIZATION: basic ' . base64_encode('x-access-token:' . $token);
        }
        return $env;
    }

    public static function git(array $args, int $timeout = 120): array {
        if (!self::has_git()) { throw new RuntimeException('WordPress root is not a Git repository.'); }
        $allowed = ['status','branch','rev-parse','log','rev-list','fetch','diff','add','commit','push','pull','checkout','remote','show-ref'];
        $subcommand = (string)($args[0] ?? '');
        if (!in_array($subcommand, $allowed, true)) { throw new RuntimeException('Blocked Git command.'); }
        foreach ($args as $arg) {
            if (!is_string($arg) || str_contains($arg, "\0") || str_contains($arg, "\n") || str_contains($arg, "\r")) { throw new RuntimeException('Invalid Git argument.'); }
        }
        if (!function_exists('proc_open')) { throw new RuntimeException('proc_open is required for Developer Hub Git operations.'); }
        $cmd = array_merge(['git','-C',self::repo_root()], $args);
        $process = proc_open($cmd, [1=>['pipe','w'],2=>['pipe','w']], $pipes, self::repo_root(), self::git_env(), ['bypass_shell'=>true]);
        if (!is_resource($process)) { throw new RuntimeException('Unable to start Git process.'); }
        stream_set_blocking($pipes[1], false); stream_set_blocking($pipes[2], false);
        $stdout=''; $stderr=''; $started=time(); $status=[];
        while (true) {
            $status = proc_get_status($process);
            $stdout .= stream_get_contents($pipes[1]); $stderr .= stream_get_contents($pipes[2]);
            if (!$status['running']) { break; }
            if ((time()-$started) > $timeout) {
                proc_terminate($process, 15); usleep(200000); proc_terminate($process, 9);
                fclose($pipes[1]); fclose($pipes[2]); proc_close($process);
                throw new RuntimeException('Git operation timed out.');
            }
            usleep(100000);
        }
        $stdout .= stream_get_contents($pipes[1]); $stderr .= stream_get_contents($pipes[2]);
        fclose($pipes[1]); fclose($pipes[2]); $code = proc_close($process);
        if ($code === -1 && isset($status['exitcode']) && $status['exitcode'] >= 0) { $code = (int)$status['exitcode']; }
        $clean = self::redact($stderr);
        if ($code !== 0) { throw new RuntimeException(trim($clean) ?: 'Git command failed.'); }
        return ['stdout'=>trim(self::redact($stdout)),'stderr'=>trim($clean),'code'=>$code];
    }

    public static function redact(string $text): string {
        $token=''; try { $token=self::github_token(); } catch (Throwable) {}
        if ($token !== '') { $text = str_replace($token, '[REDACTED]', $text); }
        $text = preg_replace('/gh[pousr]_[A-Za-z0-9_]{20,}/', '[REDACTED]', $text) ?? $text;
        return preg_replace('/github_pat_[A-Za-z0-9_]{20,}/', '[REDACTED]', $text) ?? $text;
    }

    public static function local_status(): array {
        if (!self::has_git()) { return ['repoPath'=>self::repo_root(),'gitAvailable'=>false,'branch'=>'','shortSha'=>'','lastCommit'=>'','isDirty'=>false,'unpushedCount'=>0]; }
        $branch=self::git(['rev-parse','--abbrev-ref','HEAD'])['stdout'];
        $sha=self::git(['rev-parse','--short','HEAD'])['stdout'];
        $last=self::git(['log','-1','--pretty=%h %s'])['stdout'];
        $porcelain=self::git(['status','--porcelain=v1'])['stdout'];
        $unpushed=0; try { $unpushed=(int)self::git(['rev-list','--count','@{u}..HEAD'])['stdout']; } catch (Throwable) {}
        return ['repoPath'=>self::repo_root(),'gitAvailable'=>true,'branch'=>$branch,'shortSha'=>$sha,'lastCommit'=>$last,'isDirty'=>$porcelain !== '','unpushedCount'=>$unpushed];
    }

    private static function api_headers(string $token): array {
        return ['Authorization'=>'Bearer '.$token,'Accept'=>'application/vnd.github+json','X-GitHub-Api-Version'=>'2022-11-28','User-Agent'=>'Brando-Developer-Hub'];
    }

    public static function github_request(string $url): array {
        $token=self::github_token(); if ($token === '') { throw new RuntimeException('Verify the GitHub token first.'); }
        $response=wp_remote_get($url,['timeout'=>15,'headers'=>self::api_headers($token),'redirection'=>0]);
        if (is_wp_error($response)) { throw new RuntimeException($response->get_error_message()); }
        $code=(int)wp_remote_retrieve_response_code($response); $body=json_decode((string)wp_remote_retrieve_body($response),true);
        if ($code<200 || $code>=300) { throw new RuntimeException(self::redact(is_array($body)?(string)($body['message']??'GitHub API request failed.'):'GitHub API request failed.')); }
        return is_array($body)?$body:[];
    }

    public static function verify_github_token(string $token): array {
        if ($token === '') { throw new RuntimeException('GitHub token is required.'); }
        $response=wp_remote_get('https://api.github.com/user',['timeout'=>15,'headers'=>self::api_headers($token),'redirection'=>0]);
        if (is_wp_error($response)) { throw new RuntimeException($response->get_error_message()); }
        $code=(int)wp_remote_retrieve_response_code($response); $body=json_decode((string)wp_remote_retrieve_body($response),true);
        if ($code!==200 || !is_array($body) || empty($body['login'])) { throw new RuntimeException('GitHub token verification failed.'); }
        self::save(['github_token_encrypted'=>self::encrypt_secret($token),'github_verified_at'=>gmdate('c'),'github_login'=>sanitize_text_field((string)$body['login'])]);
        return ['login'=>(string)$body['login']];
    }

    public static function repositories(): array {
        $repos=self::github_request('https://api.github.com/user/repos?per_page=100&sort=updated&affiliation=owner,collaborator,organization_member');
        return array_values(array_map(static fn($r)=>['fullName'=>(string)($r['full_name']??''),'repoUrl'=>(string)($r['html_url']??''),'private'=>(bool)($r['private']??false),'defaultBranch'=>(string)($r['default_branch']??'main'),'updatedAt'=>(string)($r['updated_at']??''),'permission'=>(string)(($r['permissions']['admin']??false)?'admin':(($r['permissions']['push']??false)?'write':'read'))],$repos));
    }

    public static function branches(string $repo): array {
        if (!preg_match('/^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/',$repo)) { throw new RuntimeException('Invalid GitHub repository.'); }
        [$owner,$name]=explode('/',$repo,2);
        $items=self::github_request('https://api.github.com/repos/'.rawurlencode($owner).'/'.rawurlencode($name).'/branches?per_page=100');
        return array_values(array_filter(array_map(static fn($b)=>sanitize_text_field((string)($b['name']??'')),$items)));
    }

    public static function save_selection(string $repo,string $branch): array {
        if (!preg_match('/^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/',$repo)) { throw new RuntimeException('Invalid GitHub repository.'); }
        if (!preg_match('/^[A-Za-z0-9._\/-]+$/',$branch) || str_contains($branch,'..')) { throw new RuntimeException('Invalid branch.'); }
        return self::save(['github_repo'=>$repo,'github_branch'=>$branch]);
    }

    private static function acquire_lock(): void {
        if (get_transient(self::LOCK_TRANSIENT)) { throw new RuntimeException('Another GitHub operation is already running.'); }
        set_transient(self::LOCK_TRANSIENT,['user'=>get_current_user_id(),'at'=>time()],15*MINUTE_IN_SECONDS);
    }
    private static function release_lock(): void { delete_transient(self::LOCK_TRANSIENT); }

    public static function sync_preview(string $action): array {
        $action=sanitize_key($action);
        if (!in_array($action,['push','pull','sync'],true)) { throw new RuntimeException('Action must be push, pull, or sync.'); }
        self::acquire_lock();
        try {
            $state=self::state(); $branch=(string)($state['github_branch'] ?: self::local_status()['branch']);
            if ($branch==='') { throw new RuntimeException('Select a GitHub branch first.'); }
            self::git(['fetch','origin',$branch],120);
            $dirty_raw=self::git(['status','--porcelain=v1'])['stdout'];
            $counts=preg_split('/\s+/',trim(self::git(['rev-list','--left-right','--count','HEAD...origin/'.$branch])['stdout']));
            $local_ahead=(int)($counts[0]??0); $remote_ahead=(int)($counts[1]??0); $dirty=$dirty_raw!=='';
            $sync_state='synced';
            if ($dirty && $remote_ahead>0) { $sync_state='both_changes'; }
            elseif ($dirty || $local_ahead>0) { $sync_state='local_changes'; }
            elseif ($remote_ahead>0) { $sync_state='remote_changes'; }
            $expected='noop'; $blocked=false; $reason='';
            if ($action==='push') {
                if ($remote_ahead>0) { $blocked=true; $expected='blocked'; $reason='Remote changes exist. Pull/review before pushing.'; }
                elseif ($dirty) { $expected='commit_and_push'; } elseif ($local_ahead>0) { $expected='push'; }
            } elseif ($action==='pull') {
                if ($dirty || $local_ahead>0) { $blocked=true; $expected='blocked'; $reason='Local changes exist. Review/sync before pulling.'; }
                elseif ($remote_ahead>0) { $expected='fast_forward'; }
            } else {
                if ($remote_ahead>0 && ($dirty || $local_ahead>0)) { $blocked=true; $expected='blocked'; $reason='Local and remote changes both exist. Automatic merge is blocked in Brando V1; resolve/review first.'; }
                elseif ($remote_ahead>0) { $expected='fast_forward'; } elseif ($dirty) { $expected='commit_and_push'; } elseif ($local_ahead>0) { $expected='push'; }
            }
            $files=[];
            foreach (preg_split('/\R/',$dirty_raw) ?: [] as $line) { if ($line==='') continue; $files[]=['direction'=>'local','status'=>substr($line,0,2),'path'=>trim(substr($line,3))]; if (count($files)>=self::MAX_PREVIEW_FILES) break; }
            if ($remote_ahead>0 && count($files)<self::MAX_PREVIEW_FILES) {
                $remote=self::git(['diff','--name-status','HEAD..origin/'.$branch])['stdout'];
                foreach (preg_split('/\R/',$remote) ?: [] as $line) { if ($line==='') continue; $parts=preg_split('/\s+/',$line,2); $files[]=['direction'=>'remote','status'=>(string)($parts[0]??''),'path'=>(string)($parts[1]??'')]; if (count($files)>=self::MAX_PREVIEW_FILES) break; }
            }
            $fingerprint=hash_hmac('sha256',wp_json_encode([$action,$branch,$local_ahead,$remote_ahead,$dirty_raw,self::local_status()['shortSha']]),wp_salt('auth'));
            set_transient('bdh_preview_'.get_current_user_id(),['fingerprint'=>$fingerprint,'action'=>$action,'branch'=>$branch,'expected'=>$expected,'blocked'=>$blocked],10*MINUTE_IN_SECONDS);
            return ['action'=>$action,'repo'=>(string)$state['github_repo'],'branch'=>$branch,'syncState'=>$sync_state,'expectedAction'=>$expected,'localAhead'=>$local_ahead,'remoteAhead'=>$remote_ahead,'dirty'=>$dirty,'files'=>$files,'fileCount'=>count($files),'truncated'=>count($files)>=self::MAX_PREVIEW_FILES,'reviewComplete'=>true,'blocked'=>$blocked,'blockReason'=>$reason,'fingerprint'=>$fingerprint];
        } finally { self::release_lock(); }
    }

    public static function sync_execute(string $action,string $fingerprint,string $message): array {
        $preview=get_transient('bdh_preview_'.get_current_user_id());
        if (!is_array($preview) || !hash_equals((string)($preview['fingerprint']??''),$fingerprint) || ($preview['action']??'')!==$action) { throw new RuntimeException('Preview expired or changed. Review again before execution.'); }
        if (!empty($preview['blocked'])) { throw new RuntimeException('This reviewed operation is blocked.'); }
        self::acquire_lock();
        try {
            $branch=(string)$preview['branch']; $expected=(string)$preview['expected']; $logs=[];
            if ($expected==='noop') { return ['ok'=>true,'logs'=>['Already synchronized.'],'commit'=>self::local_status()['shortSha']]; }
            if ($expected==='fast_forward') { $logs[]=self::git(['pull','--ff-only','origin',$branch],180)['stdout']; }
            elseif ($expected==='commit_and_push') {
                self::git(['add','--all']); $safe=trim(wp_strip_all_tags($message));
                if ($safe==='') $safe='Brando Developer Hub sync '.gmdate('Y-m-d H:i:s').' UTC';
                if (strlen($safe)>160) $safe=substr($safe,0,160);
                $logs[]=self::git(['commit','-m',$safe],180)['stdout']; $logs[]=self::git(['push','origin','HEAD:'.$branch],300)['stdout'];
            } elseif ($expected==='push') { $logs[]=self::git(['push','origin','HEAD:'.$branch],300)['stdout']; }
            else { throw new RuntimeException('Unsupported reviewed action.'); }
            delete_transient('bdh_preview_'.get_current_user_id());
            $local=self::local_status(); self::save(['github_last_sync_at'=>gmdate('c'),'github_last_sync_commit'=>$local['shortSha'],'github_last_sync_by'=>wp_get_current_user()->user_login]);
            return ['ok'=>true,'logs'=>array_values(array_filter(array_map([self::class,'redact'],$logs))),'commit'=>$local['shortSha']];
        } finally { self::release_lock(); }
    }

    public static function generate_context(): array {
        $uploads=wp_upload_dir(); if (!empty($uploads['error'])) throw new RuntimeException((string)$uploads['error']);
        $dir=trailingslashit($uploads['basedir']).'brando-developer-hub'; wp_mkdir_p($dir); $path=$dir.'/brando-context-latest.txt'; $root=self::repo_root();
        $excluded=['/.git/','/wp-content/uploads/','/wp-content/cache/','/node_modules/','/vendor/']; $extensions=['php','js','css','json','md','txt','yml','yaml','xml','html'];
        $out="BRANDO PROJECT CONTEXT\nGenerated: ".gmdate('c')."\nRoot: {$root}\n\n"; $count=0; $bytes=0; $max=8*1024*1024;
        $it=new RecursiveIteratorIterator(new RecursiveDirectoryIterator($root,FilesystemIterator::SKIP_DOTS));
        foreach ($it as $file) {
            if (!$file->isFile() || $file->isLink()) continue; $full=$file->getPathname(); $normalized=str_replace('\\','/',$full); $skip=false;
            foreach ($excluded as $needle) { if (str_contains($normalized,$needle)) { $skip=true; break; } }
            if ($skip || !in_array(strtolower($file->getExtension()),$extensions,true) || $file->getSize()>512*1024) continue;
            $relative=ltrim(str_replace(str_replace('\\','/',$root),'',$normalized),'/');
            if (preg_match('/(^|\/)(\.env|wp-config\.php|.*secret.*|.*credential.*)$/i',$relative)) continue;
            $content=@file_get_contents($full); if (!is_string($content)) continue; $content=self::redact($content); $section="\n===== {$relative} =====\n{$content}\n";
            if (($bytes+strlen($section))>$max) break; $out.=$section; $bytes+=strlen($section); $count++;
        }
        if (file_put_contents($path,$out,LOCK_EX)===false) throw new RuntimeException('Failed to write AI context file.');
        @chmod($path,0600); self::save(['latest_context_generated_at'=>gmdate('c')]);
        return ['ok'=>true,'fileCount'=>$count,'sizeBytes'=>$bytes,'generatedAt'=>gmdate('c')];
    }

    public static function context_path(): string { $uploads=wp_upload_dir(); return trailingslashit($uploads['basedir']).'brando-developer-hub/brando-context-latest.txt'; }

    public static function build_source_zip(): array {
        if (!class_exists('ZipArchive')) throw new RuntimeException('PHP ZipArchive extension is required.');
        $uploads=wp_upload_dir(); if (!empty($uploads['error'])) throw new RuntimeException((string)$uploads['error']);
        $dir=trailingslashit($uploads['basedir']).'brando-developer-hub/exports'; wp_mkdir_p($dir); $file=$dir.'/brando-source-'.gmdate('Ymd-His').'.zip';
        $zip=new ZipArchive(); if ($zip->open($file,ZipArchive::CREATE|ZipArchive::OVERWRITE)!==true) throw new RuntimeException('Could not create source ZIP.');
        $root=self::repo_root(); $count=0; $it=new RecursiveIteratorIterator(new RecursiveDirectoryIterator($root,FilesystemIterator::SKIP_DOTS));
        foreach ($it as $entry) {
            if (!$entry->isFile() || $entry->isLink()) continue; $full=str_replace('\\','/',$entry->getPathname());
            if (str_contains($full,'/.git/') || str_contains($full,'/wp-content/uploads/') || str_contains($full,'/wp-content/cache/')) continue;
            $rel=ltrim(str_replace(str_replace('\\','/',$root),'',$full),'/'); if (preg_match('/(^|\/)(\.env|wp-config\.php|.*secret.*|.*credential.*)$/i',$rel)) continue;
            $zip->addFile($entry->getPathname(),$rel); $count++;
        }
        $zip->close(); @chmod($file,0600); return ['path'=>$file,'fileName'=>basename($file),'fileCount'=>$count,'sizeBytes'=>(int)filesize($file)];
    }

    public static function public_status(): array {
        $state=self::state(); $local=self::local_status(); $token=''; try { $token=self::github_token(); } catch (Throwable) {}
        return array_merge($local,['pushRunning'=>(bool)get_transient(self::LOCK_TRANSIENT),'mcpEnabled'=>(bool)$state['mcp_enabled'],'githubTokenSet'=>$token!=='','githubTokenSource'=>(getenv('GITHUB_SYNC_TOKEN')?'environment':($token!==''?'encrypted-storage':null)),'githubRepo'=>(string)$state['github_repo'],'githubBranch'=>(string)$state['github_branch'],'githubDefaultBranch'=>$state['github_default_branch'],'githubLastSyncAt'=>$state['github_last_sync_at'],'githubLastSyncCommit'=>$state['github_last_sync_commit'],'githubLastSyncBy'=>$state['github_last_sync_by'],'githubVerifiedAt'=>$state['github_verified_at'],'githubLogin'=>$state['github_login'],'githubPermission'=>$state['github_permission'],'githubPushMode'=>$state['github_push_mode'],'githubConnectionStatus'=>$token===''?'disconnected':(($state['github_repo']&&$state['github_branch'])?'verified':'incomplete'),'webhookSecret'=>self::mask_secret((string)$state['webhook_secret']),'aiAccessUrl'=>rest_url('brando-developer-hub/v1/context'),'aiAccessTokenMasked'=>self::mask_secret((string)$state['ai_access_token']),'latestContextGeneratedAt'=>$state['latest_context_generated_at']]);
    }
}
