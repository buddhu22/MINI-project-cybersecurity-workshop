/* ========================================================
   Lab Activity Monitor — Enterprise JavaScript Controller
   Pure vanilla JS for UI rendering, dynamic filtering & charts.
   ======================================================== */

'use strict';

// Global Chart Instances
let errorRateChartInstance = null;
let durationChartInstance = null;

// Global Cache
let rawDataCache = null;

// DOM Helper functions
function $(id) { return document.getElementById(id); }
function show(id) { $(id).classList.remove('hidden'); }
function hide(id) { $(id).classList.add('hidden'); }
function setText(id, text) { $(id).textContent = text; }

// Status Tag Generator
function getStatusTag(status, type = 'status') {
  if (type === 'status') {
    return status === 'Success'
      ? `<span class="tag tag-success">Success</span>`
      : `<span class="tag tag-error">Error</span>`;
  }
  if (type === 'module-status') {
    return status === 'Flagged'
      ? `<span class="tag tag-flagged">Flagged</span>`
      : `<span class="tag tag-normal">Normal</span>`;
  }
  return status;
}

// Connection Status Badge
function setConnectionStatus(state, text) {
  const badge = $('status-badge');
  badge.className = `status-badge ${state}`;
  badge.textContent = text;
}

// Format Time Helper
function updateLastRefreshedTime() {
  const now = new Date();
  const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  setText('last-updated-time', `Updated ${timeStr}`);
}

// ---------------------------------------------------------
// Navigation Handling
// ---------------------------------------------------------
function initNavigation() {
  const navItems = document.querySelectorAll('.sidebar-nav .nav-item');
  navItems.forEach(item => {
    item.addEventListener('click', (e) => {
      e.preventDefault();
      navItems.forEach(n => n.classList.remove('active'));
      item.classList.add('active');

      const targetId = item.getAttribute('data-target');
      const targetElement = $(targetId);
      if (targetElement) {
        targetElement.scrollIntoView({ behavior: 'smooth' });
      }
    });
  });
}

// ---------------------------------------------------------
// Populate Select Dropdowns
// ---------------------------------------------------------
function populateDropdown(id, items, defaultVal = 'All') {
  const select = $(id);
  const currentVal = select.value || defaultVal;
  select.innerHTML = '';
  items.forEach(item => {
    const opt = document.createElement('option');
    opt.value = item;
    opt.textContent = item === 'All' ? (id === 'module-filter' ? 'All Modules' : id === 'status-filter' ? 'All Statuses' : 'All Events') : item;
    if (item === currentVal) opt.selected = true;
    select.appendChild(opt);
  });
}

// ---------------------------------------------------------
// Load Main Dashboard Data
// ---------------------------------------------------------
async function fetchDashboardData() {
  setConnectionStatus('loading', 'Loading…');

  try {
    const response = await fetch('/api/data');
    const data = await response.json();

    if (!response.ok) {
      $('error-banner').textContent = data.error || 'Failed to load activity logs data.';
      show('error-banner');
      setConnectionStatus('error', 'Error');
      return;
    }

    hide('error-banner');
    rawDataCache = data;

    // Duplicate Warning
    if (data.duplicate_warning > 0) {
      $('duplicate-warning').textContent = `Notice: ${data.duplicate_warning} duplicate activity log row(s) detected in dataset.`;
      show('duplicate-warning');
    } else {
      hide('duplicate-warning');
    }

    // 1. KPI Cards
    const m = data.metrics;
    setText('val-total-events', m.total_events);
    setText('val-total-errors', m.total_errors);
    setText('val-error-rate', `${m.error_rate}%`);
    setText('val-error-rate-sub', `${m.total_errors} errors / ${m.total_events} events`);
    setText('val-avg-duration', `${m.avg_duration} ms`);
    setText('val-flagged-modules', m.flagged_modules);

    // Highlight Flagged Module KPI card if > 0
    const cardFlagged = $('card-flagged-modules');
    if (m.flagged_modules > 0) {
      cardFlagged.querySelector('.metric-value').className = 'metric-value text-red';
    } else {
      cardFlagged.querySelector('.metric-value').className = 'metric-value';
    }

    // 2. Flagged Modules Cards
    renderFlaggedModules(data.module_stats);

    // 3. Module Analysis Table
    renderModuleAnalysisTable(data.module_stats);

    // 4. Dropdowns for Log Explorer
    populateDropdown('module-filter', data.modules);
    populateDropdown('status-filter', data.statuses);
    populateDropdown('event-filter', data.event_types);

    // 5. Initial Log Explorer Render (No Audit Log Created on Load)
    await filterLogs(false);

    // 6. Audit Log Records Load
    await fetchAuditLogs();

    // 7. Render Charts
    renderCharts(data.module_stats);

    setConnectionStatus('live', 'Connected');
    updateLastRefreshedTime();

  } catch (err) {
    console.error('Fetch error:', err);
    $('error-banner').textContent = 'Unable to connect to analytics backend server. Please verify application status.';
    show('error-banner');
    setConnectionStatus('error', 'Offline');
  }
}

// ---------------------------------------------------------
// Render Flagged Modules Cards
// ---------------------------------------------------------
function renderFlaggedModules(moduleStats) {
  const container = $('flagged-modules-list');
  container.innerHTML = '';

  const flaggedList = moduleStats.filter(m => m.status === 'Flagged');

  if (flaggedList.length === 0) {
    container.innerHTML = `
      <div class="flagged-card normal">
        <div class="flagged-card-header">
          <span class="flagged-card-title">All Modules Normal</span>
          <span class="tag tag-normal">Normal</span>
        </div>
        <div class="flagged-details">No modules currently exceed the 5.0% error rate threshold.</div>
      </div>`;
    return;
  }

  flaggedList.forEach(m => {
    const card = document.createElement('div');
    card.className = 'flagged-card';
    card.innerHTML = `
      <div class="flagged-card-header">
        <span class="flagged-card-title">${m.module} Module</span>
        <span class="tag tag-flagged">Flagged</span>
      </div>
      <div class="flagged-rate">${m.error_rate}% Error Rate</div>
      <div class="flagged-details">
        ${m.total_errors} error(s) / ${m.total_events} events &bull; Avg Latency: ${m.average_duration_ms} ms
      </div>
    `;
    container.appendChild(card);
  });
}

// ---------------------------------------------------------
// Render Module Analysis Table
// ---------------------------------------------------------
function renderModuleAnalysisTable(moduleStats) {
  const tbody = $('module-body');
  tbody.innerHTML = '';

  moduleStats.forEach(item => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><strong>${item.module}</strong></td>
      <td class="td-mono">${item.total_events}</td>
      <td class="td-mono">${item.total_errors}</td>
      <td class="td-mono">${item.error_rate}%</td>
      <td class="td-mono">${item.average_duration_ms} ms</td>
      <td class="td-mono">${item.median_duration_ms} ms</td>
      <td>${getStatusTag(item.status, 'module-status')}</td>
    `;
    tbody.appendChild(tr);
  });
}

// ---------------------------------------------------------
// Log Explorer Filtering
// Audit record created ONLY when createAuditRecord === true
// ---------------------------------------------------------
async function filterLogs(createAuditRecord = false) {
  const moduleVal = $('module-filter').value || 'All';
  const statusVal = $('status-filter').value || 'All';
  const eventVal = $('event-filter').value || 'All';
  const searchVal = $('search-input').value.trim();

  const queryParams = new URLSearchParams({
    module: moduleVal,
    status: statusVal,
    event_type: eventVal,
    search: searchVal,
    log_audit: createAuditRecord ? 'true' : 'false'
  });

  try {
    const res = await fetch(`/api/filter?${queryParams.toString()}`);
    const result = await res.json();

    if (!res.ok) return;

    // Render Filtered Table Rows
    const tbody = $('filtered-body');
    tbody.innerHTML = '';

    if (result.filtered_records.length === 0) {
      tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: var(--text-muted); padding: 20px;">No activity records matched the selected filter criteria.</td></tr>`;
    } else {
      result.filtered_records.forEach(row => {
        const tr = document.createElement('tr');
        if (row.status === 'Error') tr.className = 'tr-error';
        tr.innerHTML = `
          <td class="td-mono">${row.timestamp}</td>
          <td><strong>${row.module}</strong></td>
          <td>${row.event_type}</td>
          <td>${getStatusTag(row.status, 'status')}</td>
          <td class="td-mono">${row.duration_ms} ms</td>
        `;
        tbody.appendChild(tr);
      });
    }

    setText('filtered-count-badge', `${result.records_count} records`);

    // If an audit record was newly created, refresh audit table
    if (createAuditRecord && result.audit_record) {
      await fetchAuditLogs();
    }

  } catch (err) {
    console.error('Filter request failed:', err);
  }
}

// ---------------------------------------------------------
// Fetch Audit Logs
// ---------------------------------------------------------
async function fetchAuditLogs() {
  try {
    const res = await fetch('/api/audit');
    const logs = await res.json();

    const tbody = $('audit-body');
    tbody.innerHTML = '';

    if (!logs || logs.length === 0) {
      tbody.innerHTML = `<tr><td colspan="4" style="text-align: center; color: var(--text-muted); padding: 20px;">No query audit records generated yet. Click "Apply Filters" to record an audit action.</td></tr>`;
      return;
    }

    // Display in reverse chronological order
    logs.slice().reverse().forEach(row => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td class="td-mono">${row.timestamp}</td>
        <td><span class="tag tag-normal">${row.module_filter}</span></td>
        <td><span class="tag tag-normal">${row.status_filter}</span></td>
        <td class="td-mono"><strong>${row.records_found}</strong></td>
      `;
      tbody.appendChild(tr);
    });

  } catch (err) {
    console.error('Audit fetch error:', err);
  }
}

// ---------------------------------------------------------
// Render Analytics Charts (Chart.js)
// ---------------------------------------------------------
function renderCharts(moduleStats) {
  const labels = moduleStats.map(m => m.module);
  const errorRates = moduleStats.map(m => m.error_rate);
  const avgDurations = moduleStats.map(m => m.average_duration_ms);

  // Chart 1: Module Error Rate (%)
  const ctx1 = $('error-rate-chart').getContext('2d');
  if (errorRateChartInstance) errorRateChartInstance.destroy();

  errorRateChartInstance = new Chart(ctx1, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Error Rate (%)',
        data: errorRates,
        backgroundColor: errorRates.map(r => r > 5 ? 'rgba(239, 68, 68, 0.85)' : 'rgba(16, 185, 129, 0.85)'),
        borderColor: errorRates.map(r => r > 5 ? 'rgba(239, 68, 68, 1)' : 'rgba(16, 185, 129, 1)'),
        borderWidth: 1,
        borderRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => `Error Rate: ${ctx.raw}%`
          }
        }
      },
      scales: {
        x: { grid: { color: '#1e293b' }, ticks: { color: '#64748b', font: { family: 'Inter', size: 11 } } },
        y: { grid: { color: '#1e293b' }, ticks: { color: '#64748b', font: { family: 'JetBrains Mono', size: 11 } }, beginAtZero: true }
      }
    }
  });

  // Chart 2: Module Average Duration (ms)
  const ctx2 = $('duration-chart').getContext('2d');
  if (durationChartInstance) durationChartInstance.destroy();

  durationChartInstance = new Chart(ctx2, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [{
        label: 'Avg Duration (ms)',
        data: avgDurations,
        backgroundColor: 'rgba(59, 130, 246, 0.85)',
        borderColor: 'rgba(59, 130, 246, 1)',
        borderWidth: 1,
        borderRadius: 4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => `Avg Latency: ${ctx.raw} ms`
          }
        }
      },
      scales: {
        x: { grid: { color: '#1e293b' }, ticks: { color: '#64748b', font: { family: 'Inter', size: 11 } } },
        y: { grid: { color: '#1e293b' }, ticks: { color: '#64748b', font: { family: 'JetBrains Mono', size: 11 } }, beginAtZero: true }
      }
    }
  });
}

// ---------------------------------------------------------
// Initialization & Event Listeners
// ---------------------------------------------------------
document.addEventListener('DOMContentLoaded', () => {
  initNavigation();

  // Refresh Button
  $('refresh-btn').addEventListener('click', () => {
    fetchDashboardData();
  });

  // Apply Filter Button -> Explicit Audit Creation!
  $('apply-filter-btn').addEventListener('click', () => {
    filterLogs(true);
  });

  // Reset Filters Button
  $('reset-filter-btn').addEventListener('click', () => {
    $('module-filter').value = 'All';
    $('status-filter').value = 'All';
    $('event-filter').value = 'All';
    $('search-input').value = '';
    filterLogs(false);
  });

  // Search input live filter on Enter key
  $('search-input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      filterLogs(true);
    }
  });

  // Initial Load
  fetchDashboardData();
});
