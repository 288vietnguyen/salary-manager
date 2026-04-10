/* ── State ────────────────────────────────────────────────────────────────── */
let currentUser      = null;
let gmailConnected   = false;
let gmailScanResults = [];

/* ── i18n ─────────────────────────────────────────────────────────────────── */
const TRANSLATIONS = {
  en: {
    app_title:         'Salary Manager',
    setup_title:       'Welcome to Salary Manager',
    setup_subtitle:    "Let's set up your profile first.",
    edit_profile_title:'Edit Profile',
    record_income_title:'Record Monthly Income',
    history_title:     'Income History',
    tab_history:       'History',
    tab_analytics:     'Analytics',
    section_monthly:   'Monthly Change (%)',
    section_rolling:   '3-Month Rolling Average',
    section_annual:    'Annual Summary',
    label_name:        'Full Name',
    label_title:       'Job Title',
    label_base_salary: 'Base Salary',
    label_year:        'Year',
    label_month:       'Month',
    label_income:      'Income',
    label_note:        'Note (optional)',
    col_year:          'Year',
    col_month:         'Month',
    col_income:        'Income',
    col_note:          'Note',
    col_recorded_at:   'Recorded At',
    col_base_salary:   'Base Salary',
    col_vs_base:       'vs Base %',
    col_period:        'Period',
    col_base_3m:       'Base (3 months)',
    col_income_sum:    'Total Income (3m)',
    col_actual_diff:   'Actual Diff',
    col_total_income:  'Total Income',
    col_months:        'Months',
    col_base_x12:      'Base × 12',
    btn_save_profile:  'Save Profile',
    btn_edit_profile:  'Edit Profile',
    btn_cancel:        'Cancel',
    btn_save:          'Save',
    btn_add_update:    'Add / Update',
    col_total:         'Total',
    history_empty:     'No income recorded yet.',
    monthly_empty:     'Not enough data.',
    rolling_empty:     'Need at least 3 months of data.',
    annual_empty:      'No annual data yet.',
    ph_name:           'e.g. John Doe',
    ph_title:          'e.g. Software Engineer',
    ph_note:           'Bonus, overtime…',
    err_fill_fields:   'Please fill in all fields correctly.',
    err_fill_income:   'Please fill in year, month and income.',
    saved_income:      (month, year) => `Saved income for ${month} ${year}.`,
    months: ['', 'January','February','March','April','May','June',
             'July','August','September','October','November','December'],
    col_actions:              'Actions',
    btn_delete:               'Delete',
    confirm_delete:           'Delete this income record?',
    gmail_section_title:      'Gmail Import',
    gmail_status_connected:   'Connected',
    gmail_status_disconnected:'Not connected',
    gmail_btn_settings:       'Settings',
    gmail_label_email:        'Your Gmail Address',
    gmail_label_password:     'App Password',
    gmail_password_hint:      'Generate at: https://myaccount.google.com/apppasswords',
    gmail_label_sender:       'Sender Email / Domain',
    gmail_label_regex:        'Amount Regex (named group: amount)',
    gmail_btn_save_config:    'Save',
    gmail_btn_scan:           'Scan Emails',
    gmail_scan_title:         'Email Scan Results',
    gmail_col_date:           'Email Date',
    gmail_col_subject:        'Subject',
    gmail_col_amount:         'Amount',
    gmail_btn_import_selected:'Import Selected',
    gmail_scanning:           'Scanning your emails…',
    gmail_scan_empty:         'No matching emails found.',
    gmail_scan_no_amount:     'No amount found',
    gmail_import_success:     (n) => `Imported ${n} entr${n === 1 ? 'y' : 'ies'}.`,
    gmail_config_saved:       'Settings saved.',
    gmail_connecting:         'Opening Google login…',
  },
  vi: {
    app_title:         'Quản Lý Lương',
    setup_title:       'Chào mừng đến Quản Lý Lương',
    setup_subtitle:    'Hãy thiết lập hồ sơ của bạn trước.',
    edit_profile_title:'Chỉnh Sửa Hồ Sơ',
    record_income_title:'Nhập Thu Nhập Hàng Tháng',
    history_title:     'Lịch Sử Thu Nhập',
    tab_history:       'Lịch Sử',
    tab_analytics:     'Phân Tích',
    section_monthly:   'Thay Đổi Hàng Tháng (%)',
    section_rolling:   'Trung Bình Trượt 3 Tháng',
    section_annual:    'Tổng Kết Năm',
    label_name:        'Họ và Tên',
    label_title:       'Chức Vụ',
    label_base_salary: 'Lương Cơ Bản',
    label_year:        'Năm',
    label_month:       'Tháng',
    label_income:      'Thu Nhập',
    label_note:        'Ghi Chú (tùy chọn)',
    col_year:          'Năm',
    col_month:         'Tháng',
    col_income:        'Thu Nhập',
    col_note:          'Ghi Chú',
    col_recorded_at:   'Ngày Nhập',
    col_base_salary:   'Lương Cơ Bản',
    col_vs_base:       'So với Cơ Bản %',
    col_period:        'Giai Đoạn',
    col_base_3m:       'Cơ Bản (3 tháng)',
    col_income_sum:    'Tổng Thu Nhập (3t)',
    col_actual_diff:   'Chênh Lệch',
    col_total_income:  'Tổng Thu Nhập',
    col_months:        'Số Tháng',
    col_base_x12:      'Cơ Bản × 12',
    btn_save_profile:  'Lưu Hồ Sơ',
    btn_edit_profile:  'Chỉnh Sửa',
    btn_cancel:        'Hủy',
    btn_save:          'Lưu',
    btn_add_update:    'Thêm / Cập Nhật',
    col_total:         'Tổng',
    history_empty:     'Chưa có dữ liệu thu nhập.',
    monthly_empty:     'Chưa đủ dữ liệu.',
    rolling_empty:     'Cần ít nhất 3 tháng dữ liệu.',
    annual_empty:      'Chưa có dữ liệu năm.',
    ph_name:           'VD: Nguyễn Văn A',
    ph_title:          'VD: Kỹ Sư Phần Mềm',
    ph_note:           'Thưởng, tăng ca…',
    err_fill_fields:   'Vui lòng điền đầy đủ thông tin.',
    err_fill_income:   'Vui lòng điền năm, tháng và thu nhập.',
    saved_income:      (month, year) => `Đã lưu thu nhập tháng ${month} năm ${year}.`,
    months: ['', 'Tháng 1','Tháng 2','Tháng 3','Tháng 4','Tháng 5','Tháng 6',
             'Tháng 7','Tháng 8','Tháng 9','Tháng 10','Tháng 11','Tháng 12'],
    col_actions:              'Thao Tác',
    btn_delete:               'Xóa',
    confirm_delete:           'Xóa bản ghi thu nhập này?',
    gmail_section_title:      'Nhập Từ Gmail',
    gmail_status_connected:   'Đã kết nối',
    gmail_status_disconnected:'Chưa kết nối',
    gmail_btn_settings:       'Cài Đặt',
    gmail_label_email:        'Địa Chỉ Gmail Của Bạn',
    gmail_label_password:     'Mật Khẩu Ứng Dụng',
    gmail_password_hint:      'Tạo tại: https://myaccount.google.com/apppasswords',
    gmail_label_sender:       'Email / Tên miền người gửi',
    gmail_label_regex:        'Regex Số Tiền (nhóm tên: amount)',
    gmail_btn_save_config:    'Lưu',
    gmail_btn_scan:           'Quét Email',
    gmail_scan_title:         'Kết Quả Quét Email',
    gmail_col_date:           'Ngày Email',
    gmail_col_subject:        'Tiêu Đề',
    gmail_col_amount:         'Số Tiền',
    gmail_btn_import_selected:'Nhập Đã Chọn',
    gmail_scanning:           'Đang quét email của bạn…',
    gmail_scan_empty:         'Không tìm thấy email phù hợp.',
    gmail_scan_no_amount:     'Không tìm thấy số tiền',
    gmail_import_success:     (n) => `Đã nhập ${n} mục.`,
    gmail_config_saved:       'Đã lưu cài đặt.',
    gmail_connecting:         'Đang mở đăng nhập Google…',
  },
};

let currentLang = localStorage.getItem('lang') || 'en';

const QUARTER_LABELS = {
  en: { 1: 'Jan → Mar', 2: 'Apr → Jun', 3: 'Jul → Sep', 4: 'Oct → Dec' },
  vi: { 1: 'Th1 → Th3', 2: 'Th4 → Th6', 3: 'Th7 → Th9', 4: 'Th10 → Th12' },
};

function t(key, ...args) {
  const val = TRANSLATIONS[currentLang][key];
  return typeof val === 'function' ? val(...args) : (val ?? key);
}

function applyLang() {
  // Text content
  document.querySelectorAll('[data-i18n]').forEach(el => {
    el.textContent = t(el.dataset.i18n);
  });
  // Placeholders
  document.querySelectorAll('[data-i18n-ph]').forEach(el => {
    el.placeholder = t(el.dataset.i18nPh);
  });
  // Month select options
  const sel = document.getElementById('income-month');
  if (sel) {
    const curr = sel.value;
    sel.innerHTML = TRANSLATIONS[currentLang].months
      .slice(1)
      .map((m, i) => `<option value="${i + 1}">${m}</option>`)
      .join('');
    sel.value = curr;
  }
  // Lang button shows the OTHER language (what clicking will switch to)
  const btn = document.getElementById('lang-toggle');
  if (btn) btn.textContent = currentLang === 'en' ? 'VI' : 'EN';
  document.documentElement.lang = currentLang;
  localStorage.setItem('lang', currentLang);
  renderGmailStatus();
}

function toggleLang() {
  currentLang = currentLang === 'en' ? 'vi' : 'en';
  applyLang();
  // Re-render dynamic content
  if (currentUser) { loadHistory(); loadAnalytics(); }
}

/* ── Theme ────────────────────────────────────────────────────────────────── */
function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  const btn = document.getElementById('theme-toggle');
  if (btn) btn.textContent = theme === 'light' ? '🌙' : '☀️';
  localStorage.setItem('theme', theme);
}

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme') || 'dark';
  applyTheme(current === 'dark' ? 'light' : 'dark');
}

// Load saved theme immediately (before paint)
(function () {
  document.documentElement.setAttribute('data-theme', localStorage.getItem('theme') || 'dark');
})();

/* ── Boot ─────────────────────────────────────────────────────────────────── */
async function boot() {
  applyTheme(localStorage.getItem('theme') || 'dark');
  applyLang();

  const now = new Date();
  document.getElementById('income-year').value  = now.getFullYear();
  document.getElementById('income-month').value = now.getMonth() + 1;

  const users = await api('/api/users');
  if (!users.length) {
    show('setup-overlay');
  } else {
    currentUser = users[0];
    showApp();
  }
  checkGmailCallbackParams();
  await checkGmailStatus();
}

function showApp() {
  hide('setup-overlay');
  show('app');
  document.getElementById('header-user').textContent =
    `${currentUser.name} · ${currentUser.title}`;
  loadHistory();
  loadAnalytics();
}

/* ── Setup ────────────────────────────────────────────────────────────────── */
async function submitSetup() {
  const name   = document.getElementById('setup-name').value.trim();
  const title  = document.getElementById('setup-title').value.trim();
  const salary = parseFloat(document.getElementById('setup-salary').value);

  if (!name || !title || isNaN(salary) || salary < 0) {
    showError('setup-error', t('err_fill_fields'));
    return;
  }

  const user = await api('/api/users', 'POST', { name, title, base_salary: salary });
  if (user.id) {
    currentUser = user;
    showApp();
  }
}

/* ── Edit Profile ─────────────────────────────────────────────────────────── */
function openEditProfile() {
  document.getElementById('edit-name').value   = currentUser.name;
  document.getElementById('edit-title').value  = currentUser.title;
  document.getElementById('edit-salary').value = currentUser.base_salary;
  show('edit-overlay');
}

function closeEditProfile() { hide('edit-overlay'); }

async function saveEditProfile() {
  const name   = document.getElementById('edit-name').value.trim();
  const title  = document.getElementById('edit-title').value.trim();
  const salary = parseFloat(document.getElementById('edit-salary').value);

  if (!name || !title || isNaN(salary) || salary < 0) {
    showError('edit-error', t('err_fill_fields'));
    return;
  }

  await api(`/api/users/${currentUser.id}`, 'PUT', { name, title, base_salary: salary });
  currentUser = { ...currentUser, name, title, base_salary: salary };
  document.getElementById('header-user').textContent = `${name} · ${title}`;
  hide('edit-overlay');
  loadAnalytics();
}

/* ── Income Input ─────────────────────────────────────────────────────────── */
async function submitIncome() {
  const year   = parseInt(document.getElementById('income-year').value);
  const month  = parseInt(document.getElementById('income-month').value);
  const income = parseFloat(document.getElementById('income-amount').value);
  const note   = document.getElementById('income-note').value.trim();
  const msg    = document.getElementById('income-msg');

  if (isNaN(year) || isNaN(month) || isNaN(income) || income < 0) {
    showMsg(msg, t('err_fill_income'), false);
    return;
  }

  await api('/api/income', 'POST', { user_id: currentUser.id, year, month, income, note });
  showMsg(msg, t('saved_income', TRANSLATIONS[currentLang].months[month], year), true);

  document.getElementById('income-amount').value = '';
  document.getElementById('income-note').value   = '';

  loadHistory();
  loadAnalytics();
}

/* ── History Tab ─────────────────────────────────────────────────────────── */
async function loadHistory() {
  const rows  = await api(`/api/income/${currentUser.id}`);
  const tbody = document.getElementById('history-body');
  tbody.innerHTML = '';

  if (!rows.length) {
    hide('history-table-wrap');
    show('history-empty');
    return;
  }

  hide('history-empty');
  show('history-table-wrap');

  rows.forEach(r => {
    const tr = document.createElement('tr');
    tr.id = `income-row-${r.id}`;
    tr.innerHTML = `
      <td>${r.year}</td>
      <td>${TRANSLATIONS[currentLang].months[r.month]}</td>
      <td>${fmt(r.income)}</td>
      <td>${r.note || '—'}</td>
      <td class="dim">${fmtDate(r.created_at)}</td>
      <td><button class="btn-delete" onclick="deleteIncome(${r.id})" title="${t('btn_delete')}"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg></button></td>
    `;
    tbody.appendChild(tr);
  });
}

/* ── Analytics Tab ────────────────────────────────────────────────────────── */
async function loadAnalytics() {
  const stats = await api(`/api/stats/${currentUser.id}`);

  // Monthly
  const mBody = document.getElementById('monthly-body');
  mBody.innerHTML = '';
  if (!stats.monthly.length) {
    show('monthly-empty');
  } else {
    hide('monthly-empty');
    stats.monthly.forEach(r => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${r.year}</td>
        <td>${TRANSLATIONS[currentLang].months[r.month]}</td>
        <td>${fmt(r.income)}</td>
        <td>${fmt(r.base_salary)}</td>
        <td>${pctBadge(r.diff_pct)}</td>
      `;
      mBody.appendChild(tr);
    });

    // Total row
    const totalIncome = stats.monthly.reduce((s, r) => s + r.income, 0);
    const totalBase   = stats.monthly.reduce((s, r) => s + r.base_salary, 0);
    const validPcts   = stats.monthly.filter(r => r.diff_pct !== null).map(r => r.diff_pct);
    const avgPct      = validPcts.length ? Math.round(validPcts.reduce((a, b) => a + b, 0) / validPcts.length * 100) / 100 : null;
    const mFoot = document.getElementById('monthly-foot');
    mFoot.innerHTML = `<tr class="total-row">
      <td colspan="2"><strong>${t('col_total')}</strong></td>
      <td><strong>${fmt(totalIncome)}</strong></td>
      <td><strong>${fmt(totalBase)}</strong></td>
      <td>${pctBadge(avgPct)}</td>
    </tr>`;
  }

  // Rolling 3m (fixed quarters)
  const rBody = document.getElementById('rolling-body');
  rBody.innerHTML = '';
  if (!stats.rolling3.length) {
    show('rolling-empty');
  } else {
    hide('rolling-empty');
    stats.rolling3.forEach(r => {
      const label = `${r.year} ${QUARTER_LABELS[currentLang][r.quarter]}`;
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${label}</td>
        <td>${fmt(r.base_3m)}</td>
        <td>${fmt(r.income_sum)}</td>
        <td>${pctBadge(r.diff_pct)}</td>
        <td>${diffBadge(r.actual_diff)}</td>
      `;
      rBody.appendChild(tr);
    });

    // Total row
    const rTotalBase   = stats.rolling3.reduce((s, r) => s + r.base_3m, 0);
    const rTotalIncome = stats.rolling3.reduce((s, r) => s + r.income_sum, 0);
    const rValidPcts   = stats.rolling3.filter(r => r.diff_pct !== null).map(r => r.diff_pct);
    const rAvgPct      = rValidPcts.length ? Math.round(rValidPcts.reduce((a, b) => a + b, 0) / rValidPcts.length * 100) / 100 : null;
    const rTotalDiff   = Math.round((rTotalIncome - rTotalBase) * 100) / 100;
    const rFoot = document.getElementById('rolling-foot');
    rFoot.innerHTML = `<tr class="total-row">
      <td><strong>${t('col_total')}</strong></td>
      <td><strong>${fmt(rTotalBase)}</strong></td>
      <td><strong>${fmt(rTotalIncome)}</strong></td>
      <td>${pctBadge(rAvgPct)}</td>
      <td>${diffBadge(rTotalDiff)}</td>
    </tr>`;
  }

  // Annual
  const aBody = document.getElementById('annual-body');
  aBody.innerHTML = '';
  if (!stats.annual.length) {
    show('annual-empty');
  } else {
    hide('annual-empty');
    stats.annual.forEach(r => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${r.year}</td>
        <td>${fmt(r.annual_base)}</td>
        <td>${fmt(r.total)}</td>
        <td>${pctBadge(r.diff_pct)}</td>
        <td>${diffBadge(r.actual_diff)}</td>
      `;
      aBody.appendChild(tr);
    });
  }
}


/* ── Helpers ──────────────────────────────────────────────────────────────── */
async function api(path, method = 'GET', body = null) {
  const opts = { method, headers: { 'Content-Type': 'application/json' } };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(path, opts);
  if (!res.ok) {
    let msg = `API error ${res.status}`;
    try { const j = await res.json(); if (j.detail) msg = j.detail; } catch {}
    throw new Error(msg);
  }
  return res.json();
}

function show(id) { document.getElementById(id)?.classList.remove('hidden'); }
function hide(id) { document.getElementById(id)?.classList.add('hidden'); }

function showError(id, msg) {
  const el = document.getElementById(id);
  el.textContent = msg;
  el.classList.remove('hidden');
  setTimeout(() => el.classList.add('hidden'), 4000);
}

function showMsg(el, text, ok) {
  el.textContent = text;
  el.className   = `msg ${ok ? 'ok' : 'err'}`;
  el.classList.remove('hidden');
  setTimeout(() => el.classList.add('hidden'), 3500);
}

function fmt(n) {
  if (n === null || n === undefined) return '—';
  const parts = n.toFixed(2).split('.');
  parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, '.');
  return parts.join(',');
}

function fmtDate(s) {
  if (!s) return '';
  return new Date(s + 'Z').toLocaleDateString(currentLang === 'vi' ? 'vi-VN' : 'en-US',
    { year: 'numeric', month: 'short', day: 'numeric' });
}

function pctBadge(v) {
  if (v === null || v === undefined) return '<span class="badge flat">—</span>';
  const cls  = v > 0 ? 'up' : v < 0 ? 'down' : 'flat';
  const sign = v > 0 ? '+' : '';
  return `<span class="badge ${cls}">${sign}${v}%</span>`;
}

function diffBadge(v) {
  if (v === null || v === undefined) return '<span class="badge flat">—</span>';
  const cls  = v > 0 ? 'up' : v < 0 ? 'down' : 'flat';
  const sign = v > 0 ? '+' : '';
  return `<span class="badge ${cls}">${sign}${fmt(v)}</span>`;
}

/* ── Delete Income ────────────────────────────────────────────────────────── */
async function deleteIncome(id) {
  if (!confirm(t('confirm_delete'))) return;
  await api(`/api/income/${id}`, 'DELETE');
  const row = document.getElementById(`income-row-${id}`);
  if (row) row.remove();
  loadAnalytics();
}

/* ── Gmail ────────────────────────────────────────────────────────────────── */
async function checkGmailStatus() {
  try {
    const data = await api('/api/gmail/status');
    gmailConnected = data.connected;
    renderGmailStatus();
  } catch (e) { /* non-fatal */ }
}

function renderGmailStatus() {
  const badge = document.getElementById('gmail-status-badge');
  if (!badge) return;
  if (gmailConnected) {
    badge.textContent = t('gmail_status_connected');
    badge.className   = 'badge up';
  } else {
    badge.textContent = t('gmail_status_disconnected');
    badge.className   = 'badge flat';
  }
}

function checkGmailCallbackParams() { /* no-op */ }

async function openGmailSettings() {
  const config = await api('/api/gmail/config');
  document.getElementById('gmail-email').value    = config.email         || '';
  document.getElementById('gmail-password').value = '';  // never pre-fill password
  document.getElementById('gmail-sender').value   = config.sender_filter || '';
  document.getElementById('gmail-regex').value    = config.amount_regex  || '';
  const hint = document.getElementById('gmail-password');
  if (config.has_password) hint.placeholder = '••••••••••••••••';
  show('gmail-settings-overlay');
}

function closeGmailSettings() { hide('gmail-settings-overlay'); }

async function saveGmailConfig() {
  const gmail_email  = document.getElementById('gmail-email').value.trim();
  const app_password = document.getElementById('gmail-password').value.trim();
  const sender       = document.getElementById('gmail-sender').value.trim();
  const regex        = document.getElementById('gmail-regex').value.trim();
  await api('/api/gmail/config', 'POST', {
    email: gmail_email, app_password, sender_filter: sender, amount_regex: regex,
  });
  const msg = document.getElementById('gmail-config-msg');
  showMsg(msg, t('gmail_config_saved'), true);
  await checkGmailStatus();
  setTimeout(() => closeGmailSettings(), 1200);
}

async function gmailScan() {
  const msg = document.getElementById('gmail-msg');
  show('scan-loader');
  try {
    const results = await api('/api/gmail/scan', 'POST', {
      user_id: currentUser.id, year: null, month: null,
    });
    gmailScanResults = results;
    renderGmailPreview(results);
    show('gmail-scan-overlay');
  } catch (e) {
    showMsg(msg, e.message, false);
  } finally {
    hide('scan-loader');
  }
}

function renderGmailPreview(entries) {
  const tbody = document.getElementById('gmail-preview-body');
  tbody.innerHTML = '';

  if (!entries.length) {
    show('gmail-scan-empty');
    return;
  }
  hide('gmail-scan-empty');

  entries.forEach((e, i) => {
    const amountDisplay = e.amount !== null
      ? fmt(e.amount)
      : `<span class="badge flat">${t('gmail_scan_no_amount')}</span>`;
    const tr = document.createElement('tr');
    if (e.unresolved) tr.className = 'gmail-unresolved';
    tr.innerHTML = `
      <td><input type="checkbox" class="gmail-entry-check" data-idx="${i}"
                 ${e.amount !== null ? '' : 'disabled'} /></td>
      <td>${e.year}</td>
      <td>${TRANSLATIONS[currentLang].months[e.month]}</td>
      <td>${amountDisplay}</td>
      <td class="dim" title="${e.subject}">${e.subject.slice(0, 40)}${e.subject.length > 40 ? '…' : ''}</td>
      <td class="dim">${e.date}</td>
    `;
    tbody.appendChild(tr);
  });
}

function gmailToggleAll(masterCb) {
  document.querySelectorAll('.gmail-entry-check:not([disabled])')
    .forEach(cb => { cb.checked = masterCb.checked; });
}

function closeGmailScan() {
  hide('gmail-scan-overlay');
  const selectAll = document.getElementById('gmail-select-all');
  if (selectAll) selectAll.checked = false;
}

async function gmailImportSelected() {
  const checked = [...document.querySelectorAll('.gmail-entry-check:checked')];
  if (!checked.length) return;

  const toImport = checked.map(cb => gmailScanResults[parseInt(cb.dataset.idx)]);
  let imported = 0;

  for (const entry of toImport) {
    await api('/api/income', 'POST', {
      user_id: currentUser.id,
      year:    entry.year,
      month:   entry.month,
      income:  entry.amount,
      note:    `Gmail: ${entry.subject.slice(0, 80)}`,
    });
    imported++;
  }

  const msg = document.getElementById('gmail-import-msg');
  showMsg(msg, t('gmail_import_success', imported), true);
  setTimeout(() => {
    closeGmailScan();
    loadHistory();
    loadAnalytics();
  }, 1500);
}

/* ── Start ────────────────────────────────────────────────────────────────── */
boot();
