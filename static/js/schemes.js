/**
 * ==============================================================================
 * GOVERNMENT SCHEMES EXPLORER & COMPARISON MODULE
 * Maintainer: Person 2 (Frontend JavaScript Engineer)
 * ==============================================================================
 * Manages scheme exploration, database-backed search, filters, pagination,
 * scheme detail modal with official source link, and side-by-side comparison.
 * ==============================================================================
 */

window.SchemesModule = (function () {
  const state = {
    q: '',
    ministry_id: 'all',
    category_id: 'all',
    scheme_type: 'all',
    sort_by: 'scheme_name',
    sort_dir: 'asc',
    page: 1,
    per_page: 20,
    total: 0,
    total_pages: 1,
    schemes: []
  };

  let searchDebounceTimer = null;

  // ----------------------------------------------------------------------------
  // INITIALIZE FILTERS
  // ----------------------------------------------------------------------------
  async function initFilters() {
    try {
      const [minRes, catRes, typeRes] = await Promise.all([
        api.get('/api/ministries'),
        api.get('/api/categories'),
        api.get('/api/analytics/scheme-type')
      ]);

      const minSelect = document.getElementById('filter-scheme-ministry');
      if (minSelect && minRes.data) {
        minSelect.innerHTML = '<option value="all">All Ministries (19)</option>' +
          minRes.data.map(m => `<option value="${m.id}">${escapeHtml(m.name)} (${m.scheme_count})</option>`).join('');
      }

      const catSelect = document.getElementById('filter-scheme-category');
      if (catSelect && catRes.data) {
        catSelect.innerHTML = '<option value="all">All Categories (44)</option>' +
          catRes.data.map(c => `<option value="${c.id}">${escapeHtml(c.name)} (${c.scheme_count})</option>`).join('');
      }

      const typeSelect = document.getElementById('filter-scheme-type');
      if (typeSelect && typeRes.data) {
        typeSelect.innerHTML = '<option value="all">All Scheme Types</option>' +
          typeRes.data.map(t => `<option value="${escapeHtml(t.scheme_type)}">${escapeHtml(t.scheme_type)} (${t.count})</option>`).join('');
      }

      // Also populate compare dropdowns
      populateCompareDropdowns();
    } catch (err) {
      console.error("Filter initialization error:", err);
    }
  }

  // ----------------------------------------------------------------------------
  // FETCH & RENDER SCHEMES
  // ----------------------------------------------------------------------------
  async function fetchAndRenderSchemes() {
    const tbody = document.getElementById('schemes-table-body');
    const paginationEl = document.getElementById('schemes-pagination');
    const countBadge = document.getElementById('schemes-total-count');

    if (tbody) {
      tbody.innerHTML = `<tr><td colspan="7" class="empty-state">Loading Government Schemes from SQLite database...</td></tr>`;
    }

    try {
      const params = {
        sort_by: state.sort_by,
        sort_dir: state.sort_dir,
        page: state.page,
        per_page: state.per_page
      };

      if (state.q) params.q = state.q;
      if (state.ministry_id && state.ministry_id !== 'all') params.ministry_id = state.ministry_id;
      if (state.category_id && state.category_id !== 'all') params.category_id = state.category_id;
      if (state.scheme_type && state.scheme_type !== 'all') params.scheme_type = state.scheme_type;

      const res = await api.get('/api/schemes', params);

      if (res && res.success) {
        state.schemes = res.schemes;
        state.total = res.total;
        state.total_pages = res.total_pages;
        state.page = res.page;

        renderTable(res.schemes);
        renderPagination(res);

        if (countBadge) {
          countBadge.textContent = `${res.total} Schemes Found`;
        }
      }
    } catch (err) {
      if (tbody) {
        tbody.innerHTML = `<tr><td colspan="7" class="empty-state" style="color: var(--gov-red);">Failed to load schemes: ${escapeHtml(err.message)}</td></tr>`;
      }
      showToast("Error loading schemes: " + err.message, "error");
    }
  }

  function renderTable(schemes) {
    const tbody = document.getElementById('schemes-table-body');
    if (!tbody) return;

    if (!schemes || schemes.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="7" style="text-align: center; padding: 40px;">
            <div style="font-size: 14px; font-weight: 700; color: var(--text-secondary); margin-bottom: 4px;">
              No Government Schemes Matched
            </div>
            <div style="font-size: 12px; color: var(--text-muted); margin-bottom: 12px;">
              Try adjusting your search keywords or clear active filters.
            </div>
            <button class="btn btn-secondary btn-sm" onclick="SchemesModule.resetFilters()">Clear Filters</button>
          </td>
        </tr>
      `;
      return;
    }

    tbody.innerHTML = schemes.map(s => {
      // Determine CSS class for scheme type tag
      let typeClass = 'type-programme';
      const st = (s.scheme_type || '').toLowerCase();
      if (st.includes('central sector')) typeClass = 'type-central-sector';
      else if (st.includes('centrally sponsored')) typeClass = 'type-centrally-sponsored';
      else if (st.includes('mission')) typeClass = 'type-mission';

      return `
        <tr>
          <td><span class="scheme-id-badge">${escapeHtml(s.scheme_id)}</span></td>
          <td>
            <div style="font-weight: 600; color: var(--gov-navy); cursor: pointer;" onclick="SchemesModule.openDetailModal('${s.scheme_id}')">
              ${escapeHtml(s.scheme_name)}
            </div>
          </td>
          <td style="color: var(--text-secondary); font-size: 12.5px;">${escapeHtml(s.ministry)}</td>
          <td><span class="category-pill">${escapeHtml(s.category)}</span></td>
          <td><span class="type-tag ${typeClass}">${escapeHtml(s.scheme_type)}</span></td>
          <td><span style="font-size: 12px; font-weight: 600; color: #475569;">${escapeHtml(s.government_level)}</span></td>
          <td>
            <div style="display: flex; gap: 6px;">
              <button class="btn btn-secondary btn-sm" onclick="SchemesModule.openDetailModal('${s.scheme_id}')">
                Details
              </button>
              ${s.source_url ? `
                <a href="${s.source_url}" target="_blank" rel="noopener noreferrer" class="btn btn-secondary btn-sm" title="Open verified official portal" style="color: var(--gov-green);">
                  Source ↗
                </a>
              ` : ''}
            </div>
          </td>
        </tr>
      `;
    }).join('');
  }

  function renderPagination(res) {
    const el = document.getElementById('schemes-pagination');
    if (!el) return;

    if (res.total === 0) {
      el.innerHTML = '';
      return;
    }

    const startIdx = (res.page - 1) * res.per_page + 1;
    const endIdx = Math.min(res.page * res.per_page, res.total);

    let pageButtons = '';
    for (let p = 1; p <= res.total_pages; p++) {
      pageButtons += `
        <button class="page-btn ${p === res.page ? 'active' : ''}" onclick="SchemesModule.goToPage(${p})">
          ${p}
        </button>
      `;
    }

    el.innerHTML = `
      <div style="font-size: 12px; color: var(--text-muted);">
        Showing <strong>${startIdx}–${endIdx}</strong> of <strong>${res.total}</strong> schemes (Page ${res.page} of ${res.total_pages})
      </div>
      <div class="pagination-controls">
        <button class="page-btn" ${res.page <= 1 ? 'disabled' : ''} onclick="SchemesModule.goToPage(${res.page - 1})">
          ← Previous
        </button>
        ${pageButtons}
        <button class="page-btn" ${res.page >= res.total_pages ? 'disabled' : ''} onclick="SchemesModule.goToPage(${res.page + 1})">
          Next →
        </button>
      </div>
    `;
  }

  // ----------------------------------------------------------------------------
  // FILTERS, SEARCH & SORT HANDLERS
  // ----------------------------------------------------------------------------
  function handleSearchInput(e) {
    clearTimeout(searchDebounceTimer);
    searchDebounceTimer = setTimeout(() => {
      state.q = e.target.value.trim();
      state.page = 1;
      fetchAndRenderSchemes();
    }, 250);
  }

  function handleFilterChange(key, val) {
    state[key] = val;
    state.page = 1;
    fetchAndRenderSchemes();
  }

  function handleSort(colKey) {
    if (state.sort_by === colKey) {
      state.sort_dir = state.sort_dir === 'asc' ? 'desc' : 'asc';
    } else {
      state.sort_by = colKey;
      state.sort_dir = 'asc';
    }

    document.querySelectorAll('.data-table th.sortable').forEach(th => {
      th.classList.remove('active');
      const arrow = th.querySelector('.sort-arrow');
      if (arrow) arrow.textContent = '↕';
    });

    const activeTh = document.querySelector(`.data-table th[data-sort="${colKey}"]`);
    if (activeTh) {
      activeTh.classList.add('active');
      const arrow = activeTh.querySelector('.sort-arrow');
      if (arrow) arrow.textContent = state.sort_dir === 'asc' ? '↑' : '↓';
    }

    fetchAndRenderSchemes();
  }

  function goToPage(p) {
    if (p < 1 || p > state.total_pages || p === state.page) return;
    state.page = p;
    fetchAndRenderSchemes();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function resetFilters() {
    state.q = '';
    state.ministry_id = 'all';
    state.category_id = 'all';
    state.scheme_type = 'all';
    state.sort_by = 'scheme_name';
    state.sort_dir = 'asc';
    state.page = 1;

    const qInput = document.getElementById('filter-scheme-search');
    const minSelect = document.getElementById('filter-scheme-ministry');
    const catSelect = document.getElementById('filter-scheme-category');
    const typeSelect = document.getElementById('filter-scheme-type');

    if (qInput) qInput.value = '';
    if (minSelect) minSelect.value = 'all';
    if (catSelect) catSelect.value = 'all';
    if (typeSelect) typeSelect.value = 'all';

    fetchAndRenderSchemes();
    showToast('Filters cleared.', 'info', 1500);
  }

  // ----------------------------------------------------------------------------
  // SCHEME DETAIL MODAL
  // ----------------------------------------------------------------------------
  async function openDetailModal(schemeId) {
    try {
      const res = await api.get(`/api/schemes/${schemeId}`);
      if (!res || !res.data) throw new Error("Scheme not found.");

      const s = res.data;
      const body = document.getElementById('modal-scheme-detail-content');

      if (body) {
        body.innerHTML = `
          <div class="scheme-detail-grid">
            <div>
              <div class="detail-prop-group">
                <div class="detail-prop-label">Scheme Name</div>
                <h2 style="font-size: 18px; font-weight: 800; color: var(--gov-navy); margin-bottom: 6px;">
                  ${escapeHtml(s.scheme_name)}
                </h2>
                <span class="scheme-id-badge">${escapeHtml(s.scheme_id)}</span>
              </div>

              <div class="detail-prop-group" style="margin-top: 14px;">
                <div class="detail-prop-label">Nodal Ministry</div>
                <div style="font-size: 14px; font-weight: 700; color: var(--text-primary);">
                  ${escapeHtml(s.ministry_name)}
                </div>
              </div>

              <div class="detail-prop-group">
                <div class="detail-prop-label">Category / Domain</div>
                <div style="font-size: 13.5px; color: var(--text-secondary);">
                  ${escapeHtml(s.category_name)}
                </div>
              </div>

              ${s.objective ? `
                <div class="detail-prop-group">
                  <div class="detail-prop-label">Objective</div>
                  <p style="font-size: 13px; color: var(--text-secondary); background: #f8fafc; padding: 10px; border-radius: var(--radius-sm); border: 1px solid var(--border-color);">
                    ${escapeHtml(s.objective)}
                  </p>
                </div>
              ` : ''}

              ${s.data_note ? `
                <div class="detail-prop-group" style="margin-top: 16px;">
                  <div class="detail-prop-label">Official Curation Note</div>
                  <p style="font-size: 11.5px; color: var(--text-muted); background: #fafbfc; padding: 8px 12px; border-radius: var(--radius-sm); border: 1px solid var(--border-subtle); line-height: 1.4;">
                    ${escapeHtml(s.data_note)}
                  </p>
                </div>
              ` : ''}
            </div>

            <div>
              <div style="background: #fafbfc; border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 16px;">
                <div class="detail-prop-group">
                  <div class="detail-prop-label">Scheme Classification</div>
                  <div style="margin-top: 4px;">
                    <span class="type-tag type-central-sector">${escapeHtml(s.scheme_type)}</span>
                  </div>
                </div>

                <div class="detail-prop-group">
                  <div class="detail-prop-label">Government Level</div>
                  <div style="font-size: 13px; font-weight: 600;">${escapeHtml(s.government_level)}</div>
                </div>

                <div class="detail-prop-group">
                  <div class="detail-prop-label">Official Data Source</div>
                  <div style="font-size: 12.5px; color: var(--text-primary);">${escapeHtml(s.source_name || 'National Portal of India')}</div>
                </div>

                <div class="detail-prop-group">
                  <div class="detail-prop-label">Last Verification Date</div>
                  <div style="font-size: 12px; font-family: var(--font-mono); color: var(--text-secondary);">${escapeHtml(s.last_verified || '—')}</div>
                </div>

                ${s.status ? `
                  <div class="detail-prop-group">
                    <div class="detail-prop-label">Status</div>
                    <div style="font-size: 12px; font-weight: 600; color: var(--gov-green);">${escapeHtml(s.status)}</div>
                  </div>
                ` : ''}

                <div style="margin-top: 20px; padding-top: 14px; border-top: 1px solid var(--border-color); display: flex; flex-direction: column; gap: 8px;">
                  ${s.source_url ? `
                    <a href="${s.source_url}" target="_blank" rel="noopener noreferrer" class="btn btn-official-source" style="text-align: center;">
                      VIEW OFFICIAL SOURCE ↗
                    </a>
                  ` : `
                    <button class="btn btn-secondary" disabled>Official URL Not Provided</button>
                  `}
                </div>
              </div>
            </div>
          </div>
        `;
      }
      openModal('modal-scheme-detail');
    } catch (err) {
      showToast("Error opening scheme details: " + err.message, "error");
    }
  }

  // ----------------------------------------------------------------------------
  // SCHEME COMPARISON LOGIC
  // ----------------------------------------------------------------------------
  async function populateCompareDropdowns() {
    try {
      const res = await api.get('/api/schemes', { per_page: 150 });
      if (!res || !res.schemes) return;

      const opts = '<option value="">-- Select a Scheme --</option>' +
        res.schemes.map(s => `<option value="${s.scheme_id}">${escapeHtml(s.scheme_id)}: ${escapeHtml(s.scheme_name)}</option>`).join('');

      const s1 = document.getElementById('compare-scheme-1');
      const s2 = document.getElementById('compare-scheme-2');
      const s3 = document.getElementById('compare-scheme-3');

      if (s1) s1.innerHTML = opts;
      if (s2) s2.innerHTML = opts;
      if (s3) s3.innerHTML = opts;

      // Default select SCH001 and SCH002 for immediate comparison
      if (s1) s1.value = 'SCH001';
      if (s2) s2.value = 'SCH002';
      executeComparison();
    } catch (err) {
      console.error(err);
    }
  }

  async function executeComparison() {
    const s1 = document.getElementById('compare-scheme-1')?.value;
    const s2 = document.getElementById('compare-scheme-2')?.value;
    const s3 = document.getElementById('compare-scheme-3')?.value;

    const selectedIds = [s1, s2, s3].filter(id => id && id.trim() !== '');

    const container = document.getElementById('comparison-results-container');
    if (!container) return;

    if (selectedIds.length < 2) {
      container.innerHTML = `
        <div style="text-align: center; padding: 30px; background: #fff; border: 1px solid var(--border-color); border-radius: var(--radius-md);">
          <p style="color: var(--text-secondary); font-size: 13.5px;">Please select at least 2 schemes above to generate side-by-side comparison.</p>
        </div>
      `;
      return;
    }

    container.innerHTML = `<div style="text-align: center; padding: 30px;">Loading comparison data...</div>`;

    try {
      const res = await api.post('/api/compare', { scheme_ids: selectedIds });
      if (!res || !res.data) throw new Error(res.error || "Comparison failed.");

      const data = res.data;
      const schemes = data.schemes;
      const attributes = data.attributes;

      let tableHtml = `
        <div class="comparison-table-wrapper">
          <table class="comparison-table">
            <thead>
              <tr>
                <th style="background: #0f172a; color: #fff;">Attribute</th>
                ${schemes.map(s => `
                  <th>
                    <div style="font-size: 14px; font-weight: 800; color: var(--gov-navy); margin-bottom: 4px;">
                      ${escapeHtml(s.scheme_name)}
                    </div>
                    <span class="scheme-id-badge">${escapeHtml(s.scheme_id)}</span>
                  </th>
                `).join('')}
              </tr>
            </thead>
            <tbody>
              ${attributes.map(attr => `
                <tr>
                  <td class="attr-label">${escapeHtml(attr.label)}</td>
                  ${schemes.map(s => {
                    let val = s[attr.key];
                    if (val === null || val === undefined || val === '') val = '—';
                    if (attr.key === 'scheme_type') {
                      return `<td><span class="type-tag type-central-sector">${escapeHtml(val)}</span></td>`;
                    }
                    if (attr.key === 'source_name' && s.source_url) {
                      return `<td><a href="${s.source_url}" target="_blank" rel="noopener noreferrer" style="color: var(--gov-green); font-weight: 600;">${escapeHtml(val)} ↗</a></td>`;
                    }
                    return `<td>${escapeHtml(val)}</td>`;
                  }).join('')}
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      `;

      container.innerHTML = tableHtml;
    } catch (err) {
      container.innerHTML = `<div style="color: var(--gov-red); padding: 20px;">Failed to compare: ${escapeHtml(err.message)}</div>`;
    }
  }

  // Public Interface
  return {
    state,
    initFilters,
    fetchAndRenderSchemes,
    handleSearchInput,
    handleFilterChange,
    handleSort,
    goToPage,
    resetFilters,
    openDetailModal,
    populateCompareDropdowns,
    executeComparison
  };
})();
