<?php
/**
 * Brando RED recovery tool for a missing/truncated wp-config.php.
 *
 * CLI only. No secrets are stored in this repository.
 * Required environment variables at runtime:
 *   BRANDO_DB_NAME
 *   BRANDO_DB_USER
 *   BRANDO_DB_PASSWORD
 *   BRANDO_DB_HOST
 * Optional:
 *   BRANDO_TABLE_PREFIX
 *   BRANDO_FORCE=1
 */

declare(strict_types=1);

if (PHP_SAPI !== 'cli') {
    fwrite(STDERR, "ERROR=CLI_ONLY\n");
    exit(2);
}

$root = realpath($argv[1] ?? getcwd());
if (!$root || !is_file($root . '/wp-load.php') || !is_file($root . '/wp-settings.php') || !is_dir($root . '/wp-content')) {
    fwrite(STDERR, "ERROR=INVALID_WORDPRESS_ROOT\n");
    exit(3);
}

$config = $root . '/wp-config.php';
$force = getenv('BRANDO_FORCE') === '1';

$looksValid = static function (string $path): bool {
    if (!is_file($path) || filesize($path) < 512) {
        return false;
    }
    $content = file_get_contents($path);
    if (!is_string($content)) {
        return false;
    }
    foreach (['DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST', '$table_prefix', 'ABSPATH', 'wp-settings.php'] as $needle) {
        if (!str_contains($content, $needle)) {
            return false;
        }
    }
    return true;
};

if ($looksValid($config) && !$force) {
    fwrite(STDOUT, "STATUS=SKIPPED_VALID_CONFIG_EXISTS\n");
    exit(0);
}

$env = static function (string $name): string {
    $value = getenv($name);
    return is_string($value) ? trim($value) : '';
};

$dbName = $env('BRANDO_DB_NAME');
$dbUser = $env('BRANDO_DB_USER');
$dbPass = getenv('BRANDO_DB_PASSWORD');
$dbPass = is_string($dbPass) ? $dbPass : '';
$dbHost = $env('BRANDO_DB_HOST');
$tablePrefix = $env('BRANDO_TABLE_PREFIX');

$missing = [];
foreach (['BRANDO_DB_NAME' => $dbName, 'BRANDO_DB_USER' => $dbUser, 'BRANDO_DB_HOST' => $dbHost] as $key => $value) {
    if ($value === '') {
        $missing[] = $key;
    }
}
if (getenv('BRANDO_DB_PASSWORD') === false) {
    $missing[] = 'BRANDO_DB_PASSWORD';
}

if ($missing) {
    fwrite(STDERR, 'ERROR=MISSING_RUNTIME_SECRETS:' . implode(',', $missing) . "\n");
    exit(4);
}

if (!extension_loaded('mysqli')) {
    fwrite(STDERR, "ERROR=MYSQLI_NOT_AVAILABLE\n");
    exit(5);
}

mysqli_report(MYSQLI_REPORT_OFF);
$mysqli = mysqli_init();
if (!$mysqli) {
    fwrite(STDERR, "ERROR=MYSQL_INIT_FAILED\n");
    exit(6);
}

if (!@$mysqli->real_connect($dbHost, $dbUser, $dbPass, $dbName)) {
    fwrite(STDERR, "ERROR=DB_CONNECTION_FAILED\n");
    exit(7);
}

$mysqli->set_charset('utf8mb4');

$validatePrefix = static function (mysqli $db, string $prefix): bool {
    if (!preg_match('/^[A-Za-z0-9_]+$/', $prefix)) {
        return false;
    }
    $table = $prefix . 'options';
    $escapedTable = '`' . str_replace('`', '``', $table) . '`';
    $sql = "SELECT option_value FROM {$escapedTable} WHERE option_name='siteurl' LIMIT 1";
    $result = @$db->query($sql);
    if (!$result) {
        return false;
    }
    $row = $result->fetch_assoc();
    return is_array($row) && isset($row['option_value']) && trim((string)$row['option_value']) !== '';
};

if ($tablePrefix !== '') {
    if (!$validatePrefix($mysqli, $tablePrefix)) {
        fwrite(STDERR, "ERROR=INVALID_TABLE_PREFIX\n");
        exit(8);
    }
} else {
    $candidates = [];
    $result = $mysqli->query('SHOW TABLES');
    if ($result) {
        while ($row = $result->fetch_row()) {
            $table = (string)($row[0] ?? '');
            if (preg_match('/^(.+)options$/', $table, $m)) {
                $prefix = (string)$m[1];
                if ($validatePrefix($mysqli, $prefix)) {
                    $candidates[$prefix] = true;
                }
            }
        }
    }
    $prefixes = array_keys($candidates);
    if (count($prefixes) !== 1) {
        fwrite(STDERR, 'ERROR=TABLE_PREFIX_AMBIGUOUS:' . count($prefixes) . "\n");
        exit(9);
    }
    $tablePrefix = $prefixes[0];
}

$mysqli->close();

$secret = static function (): string {
    return rtrim(strtr(base64_encode(random_bytes(48)), '+/', '-_'), '=');
};

$keys = [
    'AUTH_KEY', 'SECURE_AUTH_KEY', 'LOGGED_IN_KEY', 'NONCE_KEY',
    'AUTH_SALT', 'SECURE_AUTH_SALT', 'LOGGED_IN_SALT', 'NONCE_SALT',
];

$php = "<?php\n";
$php .= "/** Emergency-recovered wp-config.php. Generated locally on the server. */\n";
$php .= "define('DB_NAME', " . var_export($dbName, true) . ");\n";
$php .= "define('DB_USER', " . var_export($dbUser, true) . ");\n";
$php .= "define('DB_PASSWORD', " . var_export($dbPass, true) . ");\n";
$php .= "define('DB_HOST', " . var_export($dbHost, true) . ");\n";
$php .= "define('DB_CHARSET', 'utf8mb4');\n";
$php .= "define('DB_COLLATE', '');\n\n";
foreach ($keys as $key) {
    $php .= "define('{$key}', " . var_export($secret(), true) . ");\n";
}
$php .= "\n\$table_prefix = " . var_export($tablePrefix, true) . ";\n";
$php .= "define('WP_DEBUG', false);\n\n";
$php .= "if (!defined('ABSPATH')) {\n";
$php .= "    define('ABSPATH', __DIR__ . '/');\n";
$php .= "}\n";
$php .= "require_once ABSPATH . 'wp-settings.php';\n";

if (is_file($config)) {
    $backup = $config . '.pre-red-recovery-' . gmdate('Ymd-His');
    if (!@copy($config, $backup)) {
        fwrite(STDERR, "ERROR=FAILED_TO_BACKUP_EXISTING_CONFIG\n");
        exit(10);
    }
}

$tmp = $config . '.redtmp-' . bin2hex(random_bytes(6));
if (file_put_contents($tmp, $php, LOCK_EX) === false) {
    fwrite(STDERR, "ERROR=FAILED_TO_WRITE_TEMP_CONFIG\n");
    exit(11);
}
@chmod($tmp, 0644);

$lintCommand = escapeshellarg(PHP_BINARY) . ' -l ' . escapeshellarg($tmp) . ' 2>&1';
$lintOutput = [];
$lintCode = 1;
@exec($lintCommand, $lintOutput, $lintCode);
if ($lintCode !== 0) {
    @unlink($tmp);
    fwrite(STDERR, "ERROR=GENERATED_CONFIG_LINT_FAILED\n");
    exit(12);
}

if (!@rename($tmp, $config)) {
    @unlink($tmp);
    fwrite(STDERR, "ERROR=ATOMIC_RENAME_FAILED\n");
    exit(13);
}
@chmod($config, 0644);

clearstatcache(true, $config);
if (!$looksValid($config)) {
    fwrite(STDERR, "ERROR=POST_WRITE_VALIDATION_FAILED\n");
    exit(14);
}

fwrite(STDOUT, "STATUS=RECOVERED\n");
fwrite(STDOUT, "DB_CONNECTION=PASS\n");
fwrite(STDOUT, "TABLE_PREFIX_VALIDATED=YES\n");
fwrite(STDOUT, 'WP_CONFIG_SIZE=' . filesize($config) . "\n");
fwrite(STDOUT, "SECRETS_PRINTED=NO\n");
