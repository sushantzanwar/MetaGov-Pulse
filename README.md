# Government Schemes Governance Intelligence Platform

An offline-first, dependency-free full-stack governance intelligence platform engineered for **Cross-Ministry Governance & Impact Intelligence** over **120 Curated Government of India Central Schemes**.

Built with **Python + Flask + SQLite (Normalized) + HTML5 + CSS + Vanilla JavaScript**, this platform uses deterministic rule-based algorithms, parameterized SQL queries, zero external AI APIs, zero machine learning models, and zero external CDNs. It operates 100% offline.

---

## 1. Project Overview

This platform transforms raw government scheme registries into actionable cross-ministerial intelligence:
- **Governance Intelligence Command Center:** Real-time KPI cards (Total Schemes: 120, Ministries: 19, Categories: 44, Scheme Types: 19), dynamic Canvas bar charts, and classification breakdowns.
- **Government Schemes Explorer:** Full exploration of all 120 schemes with real-time multi-field search, ministry filters, category filters, scheme type filters, column sorting, and 20-record database pagination.
- **Official Source Verification:** Every scheme provides verified attribution with a direct **"VIEW OFFICIAL SOURCE"** link to official portals (`https://www.india.gov.in/my-government/schemes`, `https://www.myscheme.gov.in`).
- **Cross-Ministry Intelligence:** Identifies multi-department sectoral intersections (e.g. Social Security, Education, Healthcare, Agriculture, Skill Development) with an interactive relationship hierarchy: `MINISTRY → CATEGORY → SCHEMES`.
- **Deterministic Scheme Comparison:** Side-by-side comparative analysis of 2 or 3 schemes across verified parameters without arbitrary scoring, fake ratings, or hallucinated facts.
- **100% Offline Architecture:** Uses native system font stacks and custom HTML5 Canvas chart engines. No npm, no Node.js, no React, no internet required.

---

## 2. Text Architecture Diagram

```
+-----------------------------------------------------------------------------------+
|                         GOVERNMENT INTELLIGENCE BROWSER UI                        |
|   HTML5 Semantic Shell  •  Vanilla CSS (Executive Navy)  •  Vanilla JS (Fetch)    |
|   [ Command Center ]  [ Scheme Explorer ]  [ Ministries ]  [ Categories ]         |
|   [ Cross-Ministry Tree ]  [ Scheme Comparison ]  [ Official Data Sources ]       |
+-----------------------------------------------------------------------------------+
                                         │
                        HTTP / REST APIs (JSON Payload)
                                         ▼
+-----------------------------------------------------------------------------------+
|                           FLASK BACKEND (routes/)                                 |
|   app.py (App Factory, Health Check, Favicon, JSON 400/404/500 Handlers)          |
|   ├── routes/dashboard.py  -->  GET /api/dashboard/stats, Page Routes             |
|   ├── routes/schemes.py    -->  GET /api/schemes, GET /api/schemes/<id>, /search  |
|   └── routes/analytics.py  -->  GET /api/ministries, /api/categories, /analytics   |
+-----------------------------------------------------------------------------------+
                     │                                         │
    Deterministic Analytics & Search               Executes Parameterized SQL
                     ▼                                         ▼
+-----------------------------------------+   +-------------------------------------+
|      GOVERNANCE LOGIC (services/)       |   |      DATABASE LAYER (database/)     |
|   services/analytics.py                 |   |   database/db.py (Connection Pool)  |
|   - get_dashboard_statistics()          |   |   database/schema.sql (DDL + Idx)   |
|   - search_schemes(q, filters, sort)    |   |   scripts/seed_database.py (Import) |
|   - compare_schemes(scheme_ids)         |   |                                     |
|   - get_cross_ministry_relationships()  |   |                                     |
+-----------------------------------------+   +-------------------------------------+
                                                               │
                                                               ▼
                                              +-------------------------------------+
                                              |       NORMALIZED SQLITE (db.db)     |
                                              |  [ministries]       [categories]    |
                                              |  [schemes]     [scheme_metadata]    |
                                              +-------------------------------------+
                                                               ▲
                                                               │ Initial Import
                                              +-------------------------------------+
                                              |  data/government_schemes_120.csv    |
                                              +-------------------------------------+
```

---

## 3. Technology Stack

| Component | Technology | Rationale & Competition Compliance |
| :--- | :--- | :--- |
| **Frontend UI** | HTML5 Semantic Elements | Instant browser parsing, zero build step. |
| **Styling** | Vanilla CSS (Executive Tokens) | Custom CSS properties, responsive flex/grid, zero framework bloat. |
| **Scripting** | Vanilla JavaScript (ES6+) | Native `fetch()`, event listeners, debounced search, modal controllers. |
| **Charts** | HTML5 Canvas (`charts.js`) | Offline horizontal/vertical bar charts and donut charts (0% CDN). |
| **Backend** | Python 3 + Flask 3.x | Lightweight, readable, standardized microframework. |
| **Database** | SQLite3 (`sqlite3` built-in) | Embedded relational database with foreign key constraints. |
| **Source Data** | `government_schemes_120.csv` | 120 verified Central Government of India schemes. |

---

## 4. Folder Structure

```
ELEVATION/
│
├── app.py                     # Flask application factory, error handling & blueprints
├── database.db                # Generated SQLite database (auto-created on first run; git-ignored)
├── requirements.txt           # Minimal dependencies (Flask>=3.0.0 only)
├── README.md                  # Comprehensive documentation and API contracts
│
├── data/
│   └── government_schemes_120.csv # Initial source of truth (120 curated GoI schemes)
│
├── scripts/
│   ├── __init__.py
│   └── seed_database.py       # Deterministic import & validation script
│
├── database/                  # [PERSON 4: DATABASE ENGINEER]
│   ├── __init__.py
│   ├── db.py                  # Thread-safe SQLite access layer & query helpers
│   └── schema.sql             # Normalized schema (ministries, categories, schemes, metadata)
│
├── services/                  # [PERSON 5: CORE LOGIC & ANALYTICS]
│   ├── __init__.py
│   ├── analytics.py           # Pure Python + SQL governance intelligence logic
│   └── logic.py               # Module forwarder for backwards compatibility
│
├── routes/                    # [PERSON 3: FLASK BACKEND ENGINEER]
│   ├── __init__.py
│   ├── dashboard.py           # Command Center stats API and HTML page routes
│   ├── schemes.py             # Scheme Explorer CRUD, search, pagination, comparison
│   └── analytics.py           # Ministries, categories, and cross-cutting analytics APIs
│
├── templates/                 # [PERSON 1: UI/UX DESIGNER & HTML]
│   ├── index.html             # Master Command Center shell (all 7 views + modals)
│   ├── dashboard.html         # Partial inheritance template
│   ├── records.html           # Partial inheritance template
│   ├── add_record.html        # Partial inheritance template
│   ├── detail.html            # Partial inheritance template
│   └── 404.html               # Clean government error page
│
├── static/                    # [PERSON 1 & 2: CSS & FRONTEND JAVASCRIPT]
│   ├── css/
│   │   └── style.css          # Executive navy design system, tokens, tables & badges
│   └── js/
│       ├── charts.js          # Offline HTML5 Canvas bar & donut chart engine
│       ├── main.js            # View router, Command Center loaders, relationship tree
│       └── schemes.js         # Scheme Explorer table controller, filters, pagination, compare
│
└── tests/                     # [PERSON 6: INTEGRATION LEAD]
    ├── __init__.py
    └── test_app.py            # Automated integration test suite (15 passing tests)
```

---

## 5. How to Install, Seed & Run

### 1. Install Dependencies
```bash
py -m pip install -r requirements.txt
```

### 2. Seed Database from CSV
```bash
py scripts/seed_database.py
```
**Import Summary Output:**
```
==================================================
GOVERNMENT SCHEMES DATASET IMPORT SUMMARY
==================================================
120 schemes imported
0 duplicate scheme IDs
0 duplicate scheme names
0 invalid required records
Ministries created: 19
Categories created: 44
==================================================
```

### 3. Start Application Server
```bash
py app.py
```
Open your browser at:
```
http://127.0.0.1:5000
```

### 4. Run Automated Test Suite
```bash
py -m unittest tests/test_app.py
```
*Output: `Ran 15 tests in 1.161s — OK`.*

---

## 6. REST API Documentation & Contracts

### 1. Schemes APIs

#### `GET /api/schemes`
Paginated, searchable, and filterable list of government schemes.
- **Query Parameters:**
  - `q`: Search keyword across scheme name, ID, ministry, category.
  - `ministry_id`: Filter by ministry ID.
  - `category_id`: Filter by category ID.
  - `scheme_type`: Filter by scheme type.
  - `sort_by`: `scheme_name` | `scheme_id` | `ministry` | `category` (default: `scheme_name`).
  - `sort_dir`: `asc` | `desc` (default: `asc`).
  - `page`: Page number (default: `1`).
  - `per_page`: Records per page (default: `20`).
- **Response `200 OK`:**
```json
{
  "success": true,
  "total": 120,
  "page": 1,
  "per_page": 20,
  "total_pages": 6,
  "schemes": [
    {
      "id": 1,
      "scheme_id": "SCH001",
      "scheme_name": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
      "ministry": "Ministry of Agriculture and Farmers Welfare",
      "ministry_id": 1,
      "category": "Agriculture",
      "category_id": 1,
      "scheme_type": "Central Sector Scheme",
      "government_level": "Central",
      "source_name": "National Portal of India / myScheme",
      "source_url": "https://www.india.gov.in/my-government/schemes",
      "last_verified": "2026-10-03"
    }
  ]
}
```

#### `GET /api/schemes/<scheme_id>`
Fetches complete scheme metadata and official source verification URL.
- **Response `200 OK`:**
```json
{
  "success": true,
  "data": {
    "scheme_id": "SCH001",
    "scheme_name": "Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
    "ministry_name": "Ministry of Agriculture and Farmers Welfare",
    "category_name": "Agriculture",
    "scheme_type": "Central Sector Scheme",
    "government_level": "Central",
    "source_name": "National Portal of India / myScheme",
    "source_url": "https://www.india.gov.in/my-government/schemes",
    "last_verified": "2026-10-03"
  }
}
```

#### `POST /api/compare`
Side-by-side comparison of 2 or 3 schemes across verified attributes.
- **Request Body:** `{ "scheme_ids": ["SCH001", "SCH002"] }`
- **Response `200 OK`:**
```json
{
  "success": true,
  "data": {
    "count": 2,
    "schemes": [ ... ],
    "attributes": [
      { "key": "scheme_name", "label": "Scheme Name" },
      { "key": "ministry_name", "label": "Ministry" },
      { "key": "category_name", "label": "Category" },
      { "key": "scheme_type", "label": "Scheme Type" },
      { "key": "source_name", "label": "Official Source" }
    ]
  }
}
```

---

### 2. Analytics & Governance APIs

#### `GET /api/dashboard/stats`
Returns dynamic Command Center metrics computed from the database.
```json
{
  "success": true,
  "data": {
    "total_schemes": 120,
    "total_ministries": 19,
    "total_categories": 44,
    "total_scheme_types": 19,
    "top_ministries": [ ... ],
    "category_distribution": [ ... ],
    "scheme_type_distribution": [ ... ],
    "cross_ministry_collaborations_count": 5
  }
}
```

#### `GET /api/ministries`
List of all 19 ministries with scheme count and covered categories.

#### `GET /api/categories`
List of all 44 categories with scheme count and participating ministries.

#### `GET /api/analytics/cross-ministry`
Returns multi-department category overlaps and complete governance tree:
`MINISTRY → CATEGORY → SCHEMES`.

---

## 7. Database Schema (SQLite Normalized)

### 1. `ministries`
- `id INTEGER PRIMARY KEY AUTOINCREMENT`
- `name TEXT NOT NULL UNIQUE`

### 2. `categories`
- `id INTEGER PRIMARY KEY AUTOINCREMENT`
- `name TEXT NOT NULL UNIQUE`

### 3. `schemes`
- `id INTEGER PRIMARY KEY AUTOINCREMENT`
- `scheme_id TEXT NOT NULL UNIQUE` (e.g. `SCH001`)
- `scheme_name TEXT NOT NULL UNIQUE`
- `ministry_id INTEGER NOT NULL REFERENCES ministries(id)`
- `category_id INTEGER NOT NULL REFERENCES categories(id)`
- `scheme_type TEXT NOT NULL`
- `government_level TEXT NOT NULL DEFAULT 'Central'`
- `source_name TEXT`
- `source_url TEXT`
- `last_verified TEXT`
- `data_note TEXT`

### 4. `scheme_metadata`
- `scheme_id TEXT PRIMARY KEY REFERENCES schemes(scheme_id)`
- `department TEXT`
- `description TEXT`
- `objective TEXT`
- `beneficiary_type TEXT`
- `implementation_level TEXT`
- `geographic_scope TEXT`
- `launch_year INTEGER`
- `status TEXT`
- `funding_pattern TEXT`

---

## 8. Validation Checklist Results

All automated verification checks pass:
- [x] **120 schemes exist** (Verified via `SELECT COUNT(*) FROM schemes` = 120)
- [x] **0 duplicate scheme IDs** (SCH001 to SCH120 verified)
- [x] **0 duplicate scheme names** (Unique constraint enforced)
- [x] **19 Ministries correctly linked** (Foreign key relational mapping)
- [x] **44 Categories correctly linked** (Foreign key relational mapping)
- [x] **Database-backed Search works** (Tested on 'farmer', 'education', 'finance')
- [x] **Filters work** (Ministry, Category, Scheme Type)
- [x] **Sorting works** (Ascending and Descending by Scheme Name, ID, Ministry, Category)
- [x] **Pagination works** (20 records per page across 6 pages)
- [x] **Scheme details modal works** (Complete metadata display)
- [x] **Source links work** (Official portal links with `target="_blank"`)
- [x] **Dashboard statistics are dynamic** (All counts calculated from SQLite)
- [x] **Cross-Ministry Intelligence works** (Multi-ministry intersections & relationship tree)
- [x] **Scheme comparison works** (Factual comparison without fake ratings or winners)
- [x] **No fake demo records remain** (Old generic tables removed)
- [x] **Zero external internet dependencies** (Native system fonts, Canvas charts, no CDNs)
- [x] **Zero AI/ML dependencies** (Pure rule-based deterministic analytics)
