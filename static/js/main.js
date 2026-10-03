/**
 * ==============================================================================
 * GOVERNANCE INTELLIGENCE PLATFORM — MAIN CLIENT CONTROLLER
 * Maintainer: Person 2 (Frontend JavaScript Engineer)
 * ==============================================================================
 * Manages view switching, API communication, global toast notifications,
 * modals, command center metric charts, ministry & category explorers,
 * and cross-ministry relationship tree rendering.
 * ==============================================================================
 */

const AppState = {
  currentView: 'command-center',
  dashboardStats: null,
  ministries: [],
  categories: []
};

// ------------------------------------------------------------------------------
// API CLIENT (Standardized Fetch Wrapper)
// ------------------------------------------------------------------------------
const api = {
  async request(url, options = {}) {
    try {
      const defaultHeaders = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      };

      const response = await fetch(url, {
        ...options,
        headers: { ...defaultHeaders, ...options.headers }
      });

      const data = await response.json().catch(() => null);

      if (!response.ok) {
        const errorMsg = data && (data.error || data.message)
          ? `${data.error} ${data.details ? '(' + data.details + ')' : ''}`
          : `HTTP ${response.status}: ${response.statusText}`;
        throw new Error(errorMsg);
      }

      return data;
    } catch (err) {
      console.error(`API Error on [${options.method || 'GET'}] ${url}:`, err);
      throw err;
    }
  },

  get(url, params = {}) {
    const query = new URLSearchParams(params).toString();
    const finalUrl = query ? `${url}?${query}` : url;
    return this.request(finalUrl, { method: 'GET' });
  },

  post(url, body = {}) {
    return this.request(url, {
      method: 'POST',
      body: JSON.stringify(body)
    });
  }
};

// ------------------------------------------------------------------------------
// TOAST NOTIFICATION SYSTEM
// ------------------------------------------------------------------------------
function showToast(message, type = 'info', duration = 3200) {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;

  const icons = {
    success: '✓',
    error: '✕',
    info: 'ℹ'
  };

  toast.innerHTML = `
    <span style="font-weight: bold; font-size: 14px;">${icons[type] || '•'}</span>
    <span style="flex: 1;">${escapeHtml(message)}</span>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    toast.style.transition = 'all 0.2s ease';
    setTimeout(() => toast.remove(), 250);
  }, duration);
}

// ------------------------------------------------------------------------------
// MODAL CONTROLLER
// ------------------------------------------------------------------------------
function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
  }
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove('active');
    document.body.style.overflow = '';
  }
}

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    document.querySelectorAll('.modal-backdrop.active').forEach(m => {
      m.classList.remove('active');
    });
    document.body.style.overflow = '';
  }
});

// ------------------------------------------------------------------------------
// VIEW NAVIGATION (Command Center, Schemes, Ministries, Cross-Ministry, etc.)
// ------------------------------------------------------------------------------
const VIEW_METADATA = {
  'command-center': {
    title: 'Governance Intelligence Command Center',
    subtitle: 'National Overview • 120 Curated Government of India Schemes'
  },
  'schemes': {
    title: 'Government Schemes Explorer',
    subtitle: 'Search, Filter, Sort & Inspect 120 Central Sector and Sponsored Schemes'
  },
  'ministries': {
    title: 'Ministries Intelligence',
    subtitle: '19 Nodal Ministries & Their Scheme Portfolios'
  },
  'categories': {
    title: 'Sectors & Categories Intelligence',
    subtitle: '44 Governance Categories Across Central Departments'
  },
  'cross-ministry': {
    title: 'Cross-Ministry Governance Intelligence',
    subtitle: 'Inter-Ministerial Overlaps, Multi-Department Categories & Relationship Hierarchy'
  },
  'comparison': {
    title: 'Deterministic Scheme Comparison',
    subtitle: 'Side-by-Side Comparative Analysis (2–3 Schemes) Based on Verified Attributes'
  },
  'data-sources': {
    title: 'Data Sources & Verification',
    subtitle: 'Attribution to National Portal of India, myScheme & Open Government Data'
  }
};

function switchView(viewName) {
  AppState.currentView = viewName;

  // Update active sidebar nav
  document.querySelectorAll('.nav-item').forEach(el => {
    el.classList.toggle('active', el.dataset.view === viewName);
  });

  // Toggle active view section
  document.querySelectorAll('.view-section').forEach(sec => {
    sec.classList.toggle('active', sec.id === `view-${viewName}`);
  });

  // Update header title and subtitle
  const meta = VIEW_METADATA[viewName] || { title: 'Governance Intelligence', subtitle: 'National Platform' };
  const titleEl = document.getElementById('page-header-title');
  const subEl = document.getElementById('page-header-subtitle');
  if (titleEl) titleEl.textContent = meta.title;
  if (subEl) subEl.textContent = meta.subtitle;

  // Trigger view loaders
  if (viewName === 'command-center') {
    loadCommandCenterData();
  } else if (viewName === 'schemes') {
    if (window.SchemesModule) {
      window.SchemesModule.fetchAndRenderSchemes();
    }
  } else if (viewName === 'ministries') {
    loadMinistriesData();
  } else if (viewName === 'categories') {
    loadCategoriesData();
  } else if (viewName === 'cross-ministry') {
    loadCrossMinistryData();
  } else if (viewName === 'comparison') {
    if (window.SchemesModule) {
      window.SchemesModule.populateCompareDropdowns();
    }
  }

  window.location.hash = `#${viewName}`;
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ------------------------------------------------------------------------------
// COMMAND CENTER DATA LOADER
// ------------------------------------------------------------------------------
async function loadCommandCenterData() {
  try {
    const res = await api.get('/api/dashboard/stats');
    if (!res || !res.data) return;

    const stats = res.data;
    AppState.dashboardStats = stats;

    // 1. Dynamic 4 Stat Cards
    const totalEl = document.getElementById('stat-total-schemes');
    if (totalEl) totalEl.textContent = stats.total_schemes;

    const minEl = document.getElementById('stat-total-ministries');
    if (minEl) minEl.textContent = stats.total_ministries;

    const catEl = document.getElementById('stat-total-categories');
    if (catEl) catEl.textContent = stats.total_categories;

    const typeEl = document.getElementById('stat-total-types');
    if (typeEl) typeEl.textContent = stats.total_scheme_types;

    // 2. Render Charts
    // Chart 1: Top Ministries by Scheme Count (Horizontal Bar)
    const topMin = stats.top_ministries || [];
    const minLabels = topMin.map(m => m.ministry_name);
    const minValues = topMin.map(m => m.scheme_count);
    Charts.renderHorizontalBarChart('chart-top-ministries', minLabels, minValues);

    // Chart 2: Category Distribution (Vertical Bar)
    const topCat = (stats.top_categories || []).slice(0, 8);
    const catLabels = topCat.map(c => c.category_name);
    const catValues = topCat.map(c => c.scheme_count);
    Charts.renderBarChart('chart-top-categories', catLabels, catValues);

    // Chart 3: Scheme Type Distribution (Donut)
    const typeDist = stats.scheme_type_distribution || [];
    const typeLabels = typeDist.map(t => t.scheme_type);
    const typeValues = typeDist.map(t => t.scheme_count);
    Charts.renderDonutChart('chart-scheme-types', typeLabels, typeValues);

    // 3. Featured Schemes Preview Table
    loadDashboardPreviewSchemes();
  } catch (err) {
    showToast('Failed to load Command Center statistics: ' + err.message, 'error');
  }
}

async function loadDashboardPreviewSchemes() {
  const tbody = document.getElementById('dashboard-preview-table-body');
  if (!tbody) return;

  try {
    const res = await api.get('/api/schemes', { per_page: 8 });
    if (!res || !res.schemes) return;

    tbody.innerHTML = res.schemes.map(s => `
      <tr>
        <td><span class="scheme-id-badge">${escapeHtml(s.scheme_id)}</span></td>
        <td>
          <a href="javascript:void(0)" onclick="SchemesModule.openDetailModal('${s.scheme_id}')" style="font-weight: 600; color: var(--gov-navy);">
            ${escapeHtml(s.scheme_name)}
          </a>
        </td>
        <td style="color: var(--text-secondary); font-size: 12px;">${escapeHtml(s.ministry)}</td>
        <td><span class="category-pill">${escapeHtml(s.category)}</span></td>
        <td><span class="type-tag type-central-sector">${escapeHtml(s.scheme_type)}</span></td>
        <td>
          <button class="btn btn-secondary btn-sm" onclick="SchemesModule.openDetailModal('${s.scheme_id}')">
            View Details
          </button>
        </td>
      </tr>
    `).join('');
  } catch (err) {
    console.error(err);
  }
}

// ------------------------------------------------------------------------------
// MINISTRIES VIEW LOADER
// ------------------------------------------------------------------------------
async function loadMinistriesData() {
  const container = document.getElementById('ministries-grid-container');
  if (!container) return;

  container.innerHTML = '<div style="text-align: center; padding: 30px;">Loading Ministries from SQLite...</div>';

  try {
    const res = await api.get('/api/ministries');
    if (!res || !res.data) throw new Error("Could not fetch ministries");

    AppState.ministries = res.data;

    container.innerHTML = res.data.map(m => `
      <div class="card" style="margin-bottom: 0;">
        <div class="card-header" style="background: #fafbfc;">
          <h3 style="font-size: 13.5px; font-weight: 700; color: var(--gov-navy); line-height: 1.3;">
            ${escapeHtml(m.name)}
          </h3>
          <span class="scheme-id-badge" style="background: var(--gov-navy); color: #fff; border-color: var(--gov-navy);">
            ${m.scheme_count} Schemes
          </span>
        </div>
        <div class="card-body">
          <div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 12px;">
            Covers <strong>${m.category_count}</strong> distinct sectors/categories
          </div>
          <button class="btn btn-secondary btn-sm" style="width: 100%;" onclick="filterSchemesByMinistry(${m.id})">
            Explore All ${m.scheme_count} Schemes →
          </button>
        </div>
      </div>
    `).join('');
  } catch (err) {
    container.innerHTML = `<div style="color: var(--gov-red); padding: 20px;">Error: ${escapeHtml(err.message)}</div>`;
  }
}

function filterSchemesByMinistry(ministryId) {
  switchView('schemes');
  const minSelect = document.getElementById('filter-scheme-ministry');
  if (minSelect) {
    minSelect.value = ministryId;
    window.SchemesModule.handleFilterChange('ministry_id', ministryId);
  }
}

// ------------------------------------------------------------------------------
// CATEGORIES VIEW LOADER
// ------------------------------------------------------------------------------
async function loadCategoriesData() {
  const container = document.getElementById('categories-grid-container');
  if (!container) return;

  container.innerHTML = '<div style="text-align: center; padding: 30px;">Loading Categories from SQLite...</div>';

  try {
    const res = await api.get('/api/categories');
    if (!res || !res.data) throw new Error("Could not fetch categories");

    AppState.categories = res.data;

    container.innerHTML = res.data.map(c => `
      <div class="card" style="margin-bottom: 0;">
        <div class="card-header" style="background: #fafbfc;">
          <h3 style="font-size: 13.5px; font-weight: 700; color: var(--gov-navy);">
            ${escapeHtml(c.name)}
          </h3>
          <span class="category-pill" style="font-weight: 700;">
            ${c.scheme_count} Schemes
          </span>
        </div>
        <div class="card-body">
          <div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 12px;">
            Engages <strong>${c.ministry_count}</strong> Nodal Ministries
          </div>
          <button class="btn btn-secondary btn-sm" style="width: 100%;" onclick="filterSchemesByCategory(${c.id})">
            Explore Category Schemes →
          </button>
        </div>
      </div>
    `).join('');
  } catch (err) {
    container.innerHTML = `<div style="color: var(--gov-red); padding: 20px;">Error: ${escapeHtml(err.message)}</div>`;
  }
}

function filterSchemesByCategory(categoryId) {
  switchView('schemes');
  const catSelect = document.getElementById('filter-scheme-category');
  if (catSelect) {
    catSelect.value = categoryId;
    window.SchemesModule.handleFilterChange('category_id', categoryId);
  }
}

// ------------------------------------------------------------------------------
// CROSS-MINISTRY INTELLIGENCE VIEW LOADER (Relationship Graph & Tree)
// ------------------------------------------------------------------------------
async function loadCrossMinistryData() {
  const crossCatContainer = document.getElementById('cross-cutting-categories-container');
  const treeContainer = document.getElementById('cross-ministry-tree-container');

  if (crossCatContainer) crossCatContainer.innerHTML = '<div style="padding: 20px;">Loading Cross-Ministry Overlaps...</div>';
  if (treeContainer) treeContainer.innerHTML = '<div style="padding: 20px;">Loading Governance Hierarchy...</div>';

  try {
    const res = await api.get('/api/analytics/cross-ministry');
    if (!res || !res.data) throw new Error("Could not fetch cross-ministry intelligence");

    const data = res.data;

    // 1. Cross-Cutting Categories (Multi-Ministry Domains)
    if (crossCatContainer) {
      if (!data.cross_cutting_categories || data.cross_cutting_categories.length === 0) {
        crossCatContainer.innerHTML = '<p style="color: var(--text-muted);">No multi-ministry categories found.</p>';
      } else {
        crossCatContainer.innerHTML = data.cross_cutting_categories.map(cat => `
          <div class="relationship-card">
            <div class="relationship-header">
              <span class="relationship-title">${escapeHtml(cat.category_name)}</span>
              <span class="relationship-badge">${cat.ministry_count} Ministries Involved (${cat.total_schemes} Schemes)</span>
            </div>
            <div style="font-size: 11.5px; color: var(--text-muted); margin-bottom: 10px;">
              Cross-ministerial governance intersection:
            </div>
            ${cat.ministries.map(m => `
              <div class="ministry-branch-item">
                <div class="ministry-branch-name">
                  <span>${escapeHtml(m.ministry_name)}</span>
                  <span style="font-size: 11px; color: var(--gov-navy);">${m.scheme_count} schemes</span>
                </div>
                <div class="branch-scheme-list">
                  ${m.schemes.map(s => `
                    <div class="branch-scheme-link" onclick="SchemesModule.openDetailModal('${s.scheme_id}')">
                      • <strong>${escapeHtml(s.scheme_id)}:</strong> ${escapeHtml(s.scheme_name)}
                    </div>
                  `).join('')}
                </div>
              </div>
            `).join('')}
          </div>
        `).join('');
      }
    }

    // 2. Full Hierarchy Tree: Ministry -> Category -> Schemes
    if (treeContainer) {
      treeContainer.innerHTML = data.ministries_hierarchy.map(m => `
        <div class="card" style="margin-bottom: 16px;">
          <div class="card-header" style="background: #f8fafc;">
            <div style="font-size: 14px; font-weight: 800; color: var(--gov-navy);">
              ${escapeHtml(m.ministry_name)}
            </div>
            <span class="scheme-id-badge">${m.total_schemes} Schemes Across ${m.categories_count} Categories</span>
          </div>
          <div class="card-body" style="padding: 16px 20px;">
            <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 14px;">
              ${m.categories.map(c => `
                <div style="background: #fafbfc; border: 1px solid var(--border-subtle); border-radius: var(--radius-sm); padding: 12px;">
                  <div style="font-size: 12px; font-weight: 700; color: var(--text-primary); margin-bottom: 6px; display: flex; justify-content: space-between;">
                    <span>📂 ${escapeHtml(c.category_name)}</span>
                    <span style="color: var(--text-muted); font-size: 11px;">${c.scheme_count}</span>
                  </div>
                  <div style="display: flex; flex-direction: column; gap: 4px; padding-left: 8px;">
                    ${c.schemes.map(s => `
                      <a href="javascript:void(0)" onclick="SchemesModule.openDetailModal('${s.scheme_id}')" style="font-size: 11.5px; color: var(--gov-navy); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${escapeHtml(s.scheme_name)}">
                        • ${escapeHtml(s.scheme_name)}
                      </a>
                    `).join('')}
                  </div>
                </div>
              `).join('')}
            </div>
          </div>
        </div>
      `).join('');
    }
  } catch (err) {
    if (crossCatContainer) crossCatContainer.innerHTML = `<div style="color: var(--gov-red); padding: 20px;">Error: ${escapeHtml(err.message)}</div>`;
  }
}

// ------------------------------------------------------------------------------
// UTILITY HELPERS
// ------------------------------------------------------------------------------
function escapeHtml(str) {
  if (str === null || str === undefined) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// ------------------------------------------------------------------------------
// INITIALIZATION ON DOM READY
// ------------------------------------------------------------------------------
document.addEventListener('DOMContentLoaded', () => {
  const hash = window.location.hash.replace('#', '');
  const validViews = ['command-center', 'schemes', 'ministries', 'categories', 'cross-ministry', 'comparison', 'data-sources'];
  const initialView = validViews.includes(hash) ? hash : (window.__INITIAL_VIEW__ || 'command-center');

  switchView(initialView);

  // Initialize scheme explorer filters
  if (window.SchemesModule) {
    window.SchemesModule.initFilters();
  }

  // Topbar global search jump
  const topbarSearch = document.getElementById('topbar-global-search');
  if (topbarSearch) {
    topbarSearch.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        const query = topbarSearch.value.trim();
        switchView('schemes');
        const explorerInput = document.getElementById('filter-scheme-search');
        if (explorerInput) explorerInput.value = query;
        if (window.SchemesModule) {
          window.SchemesModule.state.q = query;
          window.SchemesModule.state.page = 1;
          window.SchemesModule.fetchAndRenderSchemes();
        }
      }
    });
  }

  // Mobile menu toggle
  const mobileToggle = document.getElementById('mobile-menu-toggle');
  const sidebar = document.querySelector('.sidebar');
  if (mobileToggle && sidebar) {
    mobileToggle.addEventListener('click', () => {
      sidebar.classList.toggle('mobile-open');
    });
  }
});
