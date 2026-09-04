<?php
if (!defined('ABSPATH')) { exit; }

final class BDH_Admin {
    public static function init(): void {
        add_action('admin_menu', [self::class, 'menu']);
        add_action('admin_enqueue_scripts', [self::class, 'assets']);
        add_action('admin_post_bdh_download_source', [self::class, 'download_source']);
        add_action('admin_post_bdh_download_context', [self::class, 'download_context']);
    }

    public static function menu(): void {
        if (!BDH_Access::allowed()) { return; }
        add_menu_page(__('Developer Hub', 'brando-developer-hub'), __('Developer Hub', 'brando-developer-hub'), 'manage_options', 'brando-developer-hub', [self::class, 'render'], 'dashicons-editor-code', 3);
    }

    public static function assets(string $hook): void {
        if ($hook !== 'toplevel_page_brando-developer-hub' || !BDH_Access::allowed()) { return; }
        wp_enqueue_style('bdh-admin', BDH_URL . 'assets/admin.css', [], BDH_VERSION);
        wp_enqueue_script('bdh-admin', BDH_URL . 'assets/admin.js', [], BDH_VERSION, true);
        wp_localize_script('bdh-admin', 'BDH', [
            'rest' => esc_url_raw(rest_url('brando-developer-hub/v1')),
            'nonce' => wp_create_nonce('wp_rest'),
            'sourceUrl' => wp_nonce_url(admin_url('admin-post.php?action=bdh_download_source'), 'bdh_download_source'),
            'contextUrl' => wp_nonce_url(admin_url('admin-post.php?action=bdh_download_context'), 'bdh_download_context'),
            'rtl' => is_rtl(),
        ]);
    }

    public static function render(): void {
        BDH_Access::require_access();
        ?>
        <div class="wrap bdh-wrap" id="bdh-app" dir="<?php echo is_rtl() ? 'rtl' : 'ltr'; ?>">
            <div class="bdh-hero">
                <div class="bdh-icon dashicons dashicons-editor-code"></div>
                <div class="bdh-hero-copy"><h1><?php echo esc_html(is_rtl() ? 'لوحة المطورين' : 'Developer Hub'); ?></h1><p><?php echo esc_html(is_rtl() ? 'ربط GitHub ورفع وجلب ومزامنة مشروع براندو بأمان.' : 'Connect GitHub and securely push, pull, or synchronize the Brando project.'); ?></p></div>
                <div class="bdh-badges"><span class="bdh-badge" id="bdh-login">—</span><span class="bdh-badge bdh-warning" id="bdh-running" hidden><?php echo esc_html(is_rtl() ? 'عملية GitHub جارية' : 'GitHub operation running'); ?></span></div>
            </div>
            <div id="bdh-notice" class="bdh-notice" hidden></div>

            <section class="bdh-card bdh-download-card"><div><h2>⬇ <?php echo esc_html(is_rtl() ? 'تحميل الكود المصدري' : 'Download Source Code'); ?></h2><p><?php echo esc_html(is_rtl() ? 'نسخة ZIP آمنة تستبعد الأسرار وملفات الرفع والكاش.' : 'Safe ZIP export excluding secrets, uploads and cache.'); ?></p></div><a class="button button-secondary" href="<?php echo esc_url(wp_nonce_url(admin_url('admin-post.php?action=bdh_download_source'), 'bdh_download_source')); ?>"><?php echo esc_html(is_rtl() ? 'تحميل ZIP' : 'Download ZIP'); ?></a></section>

            <div class="bdh-grid bdh-grid-2">
                <section class="bdh-card">
                    <h2>🔑 <?php echo esc_html(is_rtl() ? 'الاتصال والمستودع' : 'Connection & Repository'); ?></h2><p><?php echo esc_html(is_rtl() ? 'تحقق من الحساب ثم اختر المستودع والفرع الخاصين بهذا المشروع.' : "Verify the account, then choose this project's repository and branch."); ?></p>
                    <label>GitHub Personal Access Token</label><div class="bdh-row"><input id="bdh-token" type="password" autocomplete="new-password" placeholder="github_pat_…"><button class="button" id="bdh-toggle-token" type="button">👁</button><button class="button button-primary" id="bdh-verify" type="button"><?php echo esc_html(is_rtl() ? 'تحقق' : 'Verify'); ?></button></div><div class="bdh-connection" id="bdh-connection">—</div>
                    <label><?php echo esc_html(is_rtl() ? 'المستودع' : 'Repository'); ?></label><select id="bdh-repo"><option value=""><?php echo esc_html(is_rtl() ? 'اختر المستودع' : 'Choose repository'); ?></option></select>
                    <label><?php echo esc_html(is_rtl() ? 'الفرع' : 'Branch'); ?></label><select id="bdh-branch"><option value="main">main</option></select>
                    <div class="bdh-actions"><button class="button button-primary" id="bdh-save-selection" type="button"><?php echo esc_html(is_rtl() ? 'حفظ الاختيار' : 'Save Selection'); ?></button><button class="button bdh-danger" id="bdh-disconnect" type="button"><?php echo esc_html(is_rtl() ? 'فصل GitHub' : 'Disconnect GitHub'); ?></button></div>
                </section>

                <section class="bdh-card">
                    <h2>↔ <?php echo esc_html(is_rtl() ? 'حالة المزامنة' : 'Synchronization Status'); ?></h2><p><?php echo esc_html(is_rtl() ? 'راجع الفروقات قبل تنفيذ أي تغيير في المشروع أو GitHub.' : 'Review differences before changing the project or GitHub.'); ?></p>
                    <div class="bdh-status-grid"><div><span><?php echo esc_html(is_rtl() ? 'المسار' : 'Path'); ?></span><strong id="bdh-path">—</strong></div><div><span><?php echo esc_html(is_rtl() ? 'الفرع الحالي' : 'Current branch'); ?></span><strong id="bdh-local-branch">—</strong></div><div><span>SHA</span><strong id="bdh-sha">—</strong></div><div><span><?php echo esc_html(is_rtl() ? 'تغييرات محلية' : 'Dirty'); ?></span><strong id="bdh-dirty">—</strong></div><div><span><?php echo esc_html(is_rtl() ? 'غير مرفوع' : 'Unpushed'); ?></span><strong id="bdh-unpushed">—</strong></div><div><span><?php echo esc_html(is_rtl() ? 'آخر مزامنة' : 'Last sync'); ?></span><strong id="bdh-last-sync">—</strong></div></div>
                    <div class="bdh-commit" id="bdh-last-commit">—</div><label>Push Control</label><select id="bdh-push-mode"><option value="off">Off</option><option value="review">Review</option><option value="auto">Auto</option></select>
                    <div class="bdh-action-buttons"><button class="button" data-preview="pull">↓ Pull</button><button class="button" data-preview="push">↑ Push</button><button class="button button-primary" data-preview="sync">↔ Sync</button></div>
                    <div class="bdh-info" id="bdh-first-push-box" hidden>
                        <strong><?php echo esc_html(is_rtl() ? 'أول ربط للمستودع' : 'First Repository Push'); ?></strong>
                        <p><?php echo esc_html(is_rtl() ? 'لو المستودع البعيد فاضي، راجع تهيئة Git وملف .gitignore والـbaseline قبل أول Push من نفس سيرفر WordPress.' : 'For an empty remote repository, review Git initialization, the safe .gitignore, and the WordPress baseline before the first push from this server.'); ?></p>
                        <div class="bdh-actions"><button class="button button-primary" id="bdh-init-preview" type="button"><?php echo esc_html(is_rtl() ? 'مراجعة أول Push' : 'Review First Push'); ?></button></div>
                    </div>
                </section>
            </div>

            <section class="bdh-card" id="bdh-review-card">
                <div class="bdh-card-head"><div><h2>🐙 <?php echo esc_html(is_rtl() ? 'مراجعة وتنفيذ' : 'Review & Execute'); ?></h2><p><?php echo esc_html(is_rtl() ? 'اختر عملية مراجعة من الأعلى. لا يتم تنفيذ أي كتابة قبل Preview.' : 'Choose a review action above. No write runs before a Preview.'); ?></p></div><span class="bdh-badge" id="bdh-sync-state">—</span></div>
                <div id="bdh-preview-empty" class="bdh-empty"><?php echo esc_html(is_rtl() ? 'لا توجد مراجعة بعد.' : 'No preview yet.'); ?></div>
                <div id="bdh-preview" hidden><div class="bdh-status-grid bdh-preview-stats"><div><span>Action</span><strong id="bdh-preview-action">—</strong></div><div><span>Expected</span><strong id="bdh-expected">—</strong></div><div><span>Local ahead</span><strong id="bdh-local-ahead">0</strong></div><div><span>Remote ahead</span><strong id="bdh-remote-ahead">0</strong></div></div><div class="bdh-blocker" id="bdh-blocker" hidden></div><div class="bdh-files"><table><thead><tr><th><?php echo esc_html(is_rtl() ? 'الاتجاه' : 'Direction'); ?></th><th><?php echo esc_html(is_rtl() ? 'الحالة' : 'Status'); ?></th><th><?php echo esc_html(is_rtl() ? 'الملف' : 'File'); ?></th></tr></thead><tbody id="bdh-files"></tbody></table></div><label><?php echo esc_html(is_rtl() ? 'رسالة Commit' : 'Commit message'); ?></label><input id="bdh-commit-message" type="text" maxlength="160" placeholder="Brando Developer Hub sync"><div class="bdh-actions"><button class="button button-primary" id="bdh-execute" type="button"><?php echo esc_html(is_rtl() ? 'تنفيذ المراجعة' : 'Execute Reviewed Action'); ?></button><button class="button" id="bdh-refresh" type="button"><?php echo esc_html(is_rtl() ? 'إعادة المراجعة' : 'Review Again'); ?></button></div><pre id="bdh-logs" class="bdh-logs" hidden></pre></div>
            </section>

            <div class="bdh-grid bdh-grid-2">
                <section class="bdh-card"><h2>🤖 <?php echo esc_html(is_rtl() ? 'ربط الذكاء الاصطناعي' : 'AI Integration'); ?></h2><p><?php echo esc_html(is_rtl() ? 'إعداد سياق الذكاء الاصطناعي ليتمكن من قراءة كود المشروع.' : 'Set up AI context so AI tools can read your project code.'); ?></p><div class="bdh-switch-row"><div><strong><?php echo esc_html(is_rtl() ? 'خادم MCP' : 'MCP Server'); ?></strong><small>Model Context Protocol</small></div><label class="bdh-switch"><input id="bdh-mcp" type="checkbox"><span></span></label></div><label><?php echo esc_html(is_rtl() ? 'توليد سياق AI' : 'Generate AI Context'); ?></label><p class="description"><?php echo esc_html(is_rtl() ? 'يجمع ملفات المشروع النصية الآمنة في ملف واحد لأدوات AI.' : 'Packs safe text project files into one AI-readable file.'); ?></p><div class="bdh-actions"><button class="button" id="bdh-generate-context" type="button"><?php echo esc_html(is_rtl() ? 'توليد الآن' : 'Generate Now'); ?></button><a class="button" href="<?php echo esc_url(wp_nonce_url(admin_url('admin-post.php?action=bdh_download_context'), 'bdh_download_context')); ?>"><?php echo esc_html(is_rtl() ? 'تحميل السياق' : 'Download Context'); ?></a></div><p class="description" id="bdh-context-date">—</p><label><?php echo esc_html(is_rtl() ? 'رابط API الآمن' : 'Secure AI API URL'); ?></label><div class="bdh-row"><input id="bdh-ai-url" type="text" readonly><button class="button" id="bdh-copy-ai" type="button">⧉</button></div><p class="description"><span>Token:</span> <code id="bdh-ai-token">—</code></p></section>
                <section class="bdh-card"><h2>🛡 <?php echo esc_html(is_rtl() ? 'الاستخدام مع أدوات AI' : 'Using AI Tools'); ?></h2><div class="bdh-info"><strong>ChatGPT / Claude / Cursor</strong><ol><li><?php echo esc_html(is_rtl() ? 'ولّد ملف سياق المشروع.' : 'Generate the project context file.'); ?></li><li><?php echo esc_html(is_rtl() ? 'انسخ رابط API أو حمّل الملف.' : 'Copy the API URL or download the file.'); ?></li><li><?php echo esc_html(is_rtl() ? 'استخدمه فقط مع أداة موثوقة.' : 'Use it only with a trusted tool.'); ?></li></ol></div><div class="bdh-safe">✓ <?php echo esc_html(is_rtl() ? 'لا تشارك روابط أو مفاتيح الوصول مع أي جهة غير موثوقة.' : 'Do not share access URLs or tokens with untrusted parties.'); ?></div><div class="bdh-safe">✓ <?php echo esc_html(is_rtl() ? 'GitHub Token مشفر AES-256-GCM ولا يظهر في السجلات.' : 'GitHub token is AES-256-GCM encrypted and redacted from logs.'); ?></div></section>
            </div>
        </div>
        <?php
    }

    public static function download_source(): void {
        BDH_Access::require_access(); check_admin_referer('bdh_download_source');
        try { $archive=BDH_Core::build_source_zip(); nocache_headers(); header('Content-Type: application/zip'); header('Content-Disposition: attachment; filename="'.sanitize_file_name($archive['fileName']).'"'); header('Content-Length: '.(string)filesize($archive['path'])); readfile($archive['path']); @unlink($archive['path']); exit; }
        catch (Throwable $e) { wp_die(esc_html(BDH_Core::redact($e->getMessage())), 500); }
    }

    public static function download_context(): void {
        BDH_Access::require_access(); check_admin_referer('bdh_download_context'); $path=BDH_Core::context_path();
        if (!is_file($path)) { wp_die(esc_html__('Generate the project context first.', 'brando-developer-hub'), 404); }
        nocache_headers(); header('Content-Type: text/plain; charset=utf-8'); header('Content-Disposition: attachment; filename="brando-context-latest.txt"'); readfile($path); exit;
    }
}
