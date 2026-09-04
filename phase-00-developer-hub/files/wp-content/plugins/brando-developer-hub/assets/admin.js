(() => {
  'use strict';
  const $ = (id) => document.getElementById(id);
  const app = $('bdh-app');
  if (!app || !window.BDH) return;

  let status = null;
  let preview = null;
  let busy = false;

  const t = (ar, en) => BDH.rtl ? ar : en;
  const notice = (message, type = 'info') => {
    const el = $('bdh-notice');
    el.hidden = false;
    el.className = `bdh-notice bdh-${type}`;
    el.textContent = message;
  };
  const clearNotice = () => { $('bdh-notice').hidden = true; };
  const setBusy = (value) => {
    busy = value;
    app.classList.toggle('bdh-busy', value);
    app.querySelectorAll('button').forEach((button) => { button.disabled = value; });
  };

  async function api(path, options = {}) {
    const response = await fetch(`${BDH.rest}${path}`, {
      credentials: 'same-origin',
      ...options,
      headers: { 'Content-Type': 'application/json', 'X-WP-Nonce': BDH.nonce, ...(options.headers || {}) },
    });
    let payload = {};
    const text = await response.text();
    try { payload = text ? JSON.parse(text) : {}; } catch { payload = { message: text }; }
    if (!response.ok) throw new Error(payload.message || payload.error || `HTTP ${response.status}`);
    return payload;
  }

  const setText = (id, value) => { const el = $(id); if (el) el.textContent = value ?? '—'; };
  const fmtDate = (value) => value ? new Date(value).toLocaleString(BDH.rtl ? 'ar-EG' : 'en-US') : '—';

  async function loadStatus() {
    clearNotice();
    try {
      status = await api('/health', { method: 'GET' });
      setText('bdh-login', status.githubLogin ? `@${status.githubLogin}` : t('غير متصل', 'Disconnected'));
      $('bdh-running').hidden = !status.pushRunning;
      setText('bdh-path', status.repoPath); setText('bdh-local-branch', status.branch || '—'); setText('bdh-sha', status.shortSha || '—');
      setText('bdh-dirty', status.isDirty ? t('نعم', 'Yes') : t('لا', 'No')); setText('bdh-unpushed', String(status.unpushedCount ?? 0)); setText('bdh-last-sync', fmtDate(status.githubLastSyncAt));
      setText('bdh-last-commit', status.lastCommit || t('لا يوجد Git repository في WordPress root', 'WordPress root is not a Git repository'));
      setText('bdh-connection', `${status.githubConnectionStatus || 'disconnected'}${status.githubTokenSource ? ` • ${status.githubTokenSource}` : ''}`);
      $('bdh-push-mode').value = status.githubPushMode || 'review'; $('bdh-mcp').checked = !!status.mcpEnabled; $('bdh-ai-url').value = status.aiAccessUrl || '';
      setText('bdh-ai-token', status.aiAccessTokenMasked || '—');
      setText('bdh-context-date', status.latestContextGeneratedAt ? `${t('آخر توليد', 'Last generated')}: ${fmtDate(status.latestContextGeneratedAt)}` : t('لم يتم توليد السياق بعد', 'Context has not been generated yet'));
      const firstPushBox = $('bdh-first-push-box');
      if (firstPushBox) firstPushBox.hidden = !!status.gitAvailable;
      if (status.githubTokenSet) await loadRepositories(status.githubRepo, status.githubBranch);
    } catch (error) { notice(error.message, 'error'); }
  }

  async function loadRepositories(selectedRepo = '', selectedBranch = '') {
    try {
      const data = await api('/github-repositories', { method: 'GET' }); const select = $('bdh-repo'); select.replaceChildren();
      const placeholder = document.createElement('option'); placeholder.value = ''; placeholder.textContent = t('اختر المستودع', 'Choose repository'); select.appendChild(placeholder);
      (data.repositories || []).forEach((repo) => { const option = document.createElement('option'); option.value = repo.fullName; option.textContent = `${repo.fullName}${repo.private ? ' 🔒' : ''}`; option.dataset.defaultBranch = repo.defaultBranch || 'main'; option.dataset.permission = repo.permission || ''; if (repo.fullName === selectedRepo) option.selected = true; select.appendChild(option); });
      if (selectedRepo) await loadBranches(selectedRepo, selectedBranch);
    } catch (error) { notice(error.message, 'error'); }
  }

  async function loadBranches(repo, selected = '') {
    if (!repo) return;
    try {
      const data = await api(`/github-branches?repo=${encodeURIComponent(repo)}`, { method: 'GET' }); const select = $('bdh-branch'); select.replaceChildren();
      const branches = data.branches || [];
      branches.forEach((branch) => { const option = document.createElement('option'); option.value = branch; option.textContent = branch; if (branch === selected) option.selected = true; select.appendChild(option); });
      if (!branches.length) {
        const branch = selected || 'main';
        const option = document.createElement('option'); option.value = branch; option.textContent = `${branch} ${t('(مستودع فارغ)', '(empty repository)')}`; option.selected = true; select.appendChild(option);
      }
      if (!select.value && select.options.length) select.selectedIndex = 0;
    } catch (error) { notice(error.message, 'error'); }
  }

  function renderPreview(data) {
    preview = data; $('bdh-preview-empty').hidden = true; $('bdh-preview').hidden = false;
    setText('bdh-sync-state', data.syncState || '—'); setText('bdh-preview-action', data.action || '—'); setText('bdh-expected', data.expectedAction || '—'); setText('bdh-local-ahead', String(data.localAhead ?? 0)); setText('bdh-remote-ahead', String(data.remoteAhead ?? 0));
    const blocker = $('bdh-blocker'); blocker.hidden = !data.blocked; blocker.textContent = data.blockReason || t('العملية محظورة', 'Operation blocked');
    $('bdh-execute').disabled = !!data.blocked || data.expectedAction === 'noop' || (status?.githubPushMode === 'off');
    const tbody = $('bdh-files'); tbody.replaceChildren();
    (data.files || []).forEach((file) => { const tr = document.createElement('tr'); [file.direction, file.status, file.path].forEach((value) => { const td = document.createElement('td'); td.textContent = value || ''; tr.appendChild(td); }); tbody.appendChild(tr); });
    if (!(data.files || []).length) { const tr = document.createElement('tr'); const td = document.createElement('td'); td.colSpan = 3; td.textContent = t('لا توجد ملفات متغيرة', 'No changed files'); tr.appendChild(td); tbody.appendChild(tr); }
  }

  async function review(action) {
    if (busy) return; setBusy(true); clearNotice();
    try { const data = await api('/github-sync-preview', { method: 'POST', body: JSON.stringify({ action }) }); renderPreview(data); notice(data.blocked ? (data.blockReason || t('المراجعة محظورة', 'Review blocked')) : t('تمت المراجعة. راجع التفاصيل قبل التنفيذ.', 'Preview ready. Review details before execution.'), data.blocked ? 'warning' : 'success'); }
    catch (error) { notice(error.message, 'error'); }
    finally { setBusy(false); if (preview) renderPreview(preview); }
  }

  async function reviewFirstPush() {
    if (busy) return;
    const repo = $('bdh-repo').value;
    const branch = $('bdh-branch').value || 'main';
    if (!repo) return notice(t('اختر المستودع أولاً', 'Choose the repository first'), 'warning');
    setBusy(true); clearNotice();
    try {
      const data = await api('/repository-init-preview', { method: 'POST', body: JSON.stringify({ repo, branch }) });
      renderPreview(data);
      const sizeMb = ((data.sizeBytes || 0) / 1048576).toFixed(1);
      notice(data.blocked ? (data.blockReason || t('تهيئة Git محظورة', 'Git initialization blocked')) : `${t('مراجعة تهيئة Git جاهزة', 'Git initialization preview ready')} • ${data.fileCount || 0} files • ${sizeMb} MB`, data.blocked ? 'warning' : 'success');
    } catch (error) { notice(error.message, 'error'); }
    finally { setBusy(false); if (preview) renderPreview(preview); }
  }

  $('bdh-toggle-token').addEventListener('click', () => { $('bdh-token').type = $('bdh-token').type === 'password' ? 'text' : 'password'; });
  $('bdh-verify').addEventListener('click', async () => { const token = $('bdh-token').value.trim(); if (!token) return notice(t('أدخل GitHub Token', 'Enter GitHub token'), 'warning'); setBusy(true); try { const data = await api('/github-auth', { method: 'POST', body: JSON.stringify({ token }) }); $('bdh-token').value = ''; notice(`${t('تم التحقق', 'Verified')}: @${data.login}`, 'success'); await loadStatus(); } catch (e) { notice(e.message, 'error'); } finally { setBusy(false); } });
  $('bdh-disconnect').addEventListener('click', async () => { if (!confirm(t('فصل GitHub وحذف التوكن المشفر؟', 'Disconnect GitHub and remove the encrypted token?'))) return; setBusy(true); try { await api('/github-connection', { method: 'DELETE' }); preview = null; notice(t('تم فصل GitHub', 'GitHub disconnected'), 'success'); await loadStatus(); } catch (e) { notice(e.message, 'error'); } finally { setBusy(false); } });
  $('bdh-repo').addEventListener('change', async (event) => { const repo = event.target.value; if (repo) await loadBranches(repo, event.target.selectedOptions[0]?.dataset.defaultBranch || 'main'); });
  $('bdh-save-selection').addEventListener('click', async () => { const repo = $('bdh-repo').value, branch = $('bdh-branch').value || 'main'; if (!repo) return notice(t('اختر المستودع', 'Choose repository'), 'warning'); setBusy(true); try { await api('/github-selection', { method: 'POST', body: JSON.stringify({ repo, branch }) }); notice(t('تم حفظ المستودع والفرع', 'Repository and branch saved'), 'success'); await loadStatus(); } catch (e) { notice(e.message, 'error'); } finally { setBusy(false); } });
  $('bdh-push-mode').addEventListener('change', async (event) => { const mode = event.target.value; try { await api('/github-push-mode', { method: 'POST', body: JSON.stringify({ mode }) }); if (status) status.githubPushMode = mode; notice(`Push Control: ${mode}`, 'success'); } catch (e) { notice(e.message, 'error'); } });
  app.querySelectorAll('[data-preview]').forEach((button) => button.addEventListener('click', () => review(button.dataset.preview)));
  $('bdh-init-preview')?.addEventListener('click', reviewFirstPush);
  $('bdh-refresh').addEventListener('click', () => { if (preview?.action === 'initialize') reviewFirstPush(); else if (preview?.action) review(preview.action); });
  $('bdh-execute').addEventListener('click', async () => {
    if (!preview || preview.blocked) return;
    const isInit = preview.action === 'initialize';
    if (!confirm(isInit ? t('تهيئة Git محليًا وإنشاء baseline؟ لن يتم أي Push إلى GitHub.', 'Initialize Git locally and create the baseline? No GitHub push will be performed.') : t(`تنفيذ ${preview.action} بعد المراجعة؟`, `Execute reviewed ${preview.action}?`))) return;
    setBusy(true); clearNotice();
    try {
      const endpoint = isInit ? '/repository-init-execute' : '/github-sync-execute';
      const body = isInit
        ? { fingerprint: preview.fingerprint, message: $('bdh-commit-message').value.trim() }
        : { action: preview.action, fingerprint: preview.fingerprint, message: $('bdh-commit-message').value.trim() };
      const data = await api(endpoint, { method: 'POST', body: JSON.stringify(body) });
      const logs = $('bdh-logs'); logs.hidden = false; logs.textContent = (data.logs || []).join('\n\n') || t('تمت العملية بنجاح', 'Operation completed successfully');
      notice(`${isInit ? t('تمت تهيئة Git محليًا — اضغط Push يدويًا عندما تكون جاهزًا', 'Git prepared locally — click Push manually when ready') : t('تم التنفيذ', 'Executed')} • ${data.commit || ''}`, 'success');
      preview = null; await loadStatus();
    } catch (e) { notice(e.message, 'error'); }
    finally { setBusy(false); }
  });
  $('bdh-mcp').addEventListener('change', async (event) => { try { await api('/mcp', { method: 'POST', body: JSON.stringify({ enabled: event.target.checked }) }); notice(t('تم تحديث حالة MCP', 'MCP status updated'), 'success'); } catch (e) { event.target.checked = !event.target.checked; notice(e.message, 'error'); } });
  $('bdh-generate-context').addEventListener('click', async () => { setBusy(true); try { const data = await api('/generate-latest-context', { method: 'POST', body: '{}' }); notice(`${t('تم توليد السياق', 'Context generated')} • ${data.fileCount} files`, 'success'); await loadStatus(); } catch (e) { notice(e.message, 'error'); } finally { setBusy(false); } });
  $('bdh-copy-ai').addEventListener('click', async () => { try { await navigator.clipboard.writeText($('bdh-ai-url').value); notice(t('تم نسخ رابط API', 'API URL copied'), 'success'); } catch { notice(t('تعذر النسخ', 'Copy failed'), 'error'); } });

  loadStatus();
})();
