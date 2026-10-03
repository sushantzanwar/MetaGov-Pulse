-- ==============================================================================
-- DATABASE SCHEMA: Normalized Government Schemes Intelligence
-- Maintainer: Person 4 (Database Engineer)
-- Description: Core normalized tables, foreign keys, and indexes for 
--              120 Government of India Schemes.
-- ==============================================================================

-- 1. Ministries Table
CREATE TABLE IF NOT EXISTS ministries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE INDEX IF NOT EXISTS idx_ministries_name ON ministries(name);

-- 2. Categories Table
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE INDEX IF NOT EXISTS idx_categories_name ON categories(name);

-- 3. Government Schemes Table (Source of Truth)
CREATE TABLE IF NOT EXISTS schemes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scheme_id TEXT NOT NULL UNIQUE,
    scheme_name TEXT NOT NULL UNIQUE,
    ministry_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    scheme_type TEXT NOT NULL,
    government_level TEXT NOT NULL DEFAULT 'Central',
    source_name TEXT,
    source_url TEXT,
    last_verified TEXT,
    data_note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(ministry_id) REFERENCES ministries(id) ON DELETE CASCADE,
    FOREIGN KEY(category_id) REFERENCES categories(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_schemes_scheme_id ON schemes(scheme_id);
CREATE INDEX IF NOT EXISTS idx_schemes_scheme_name ON schemes(scheme_name);
CREATE INDEX IF NOT EXISTS idx_schemes_ministry_id ON schemes(ministry_id);
CREATE INDEX IF NOT EXISTS idx_schemes_category_id ON schemes(category_id);
CREATE INDEX IF NOT EXISTS idx_schemes_scheme_type ON schemes(scheme_type);
CREATE INDEX IF NOT EXISTS idx_schemes_government_level ON schemes(government_level);

-- 4. Scheme Metadata Table (Optional additional verified attributes)
CREATE TABLE IF NOT EXISTS scheme_metadata (
    scheme_id TEXT PRIMARY KEY,
    department TEXT,
    description TEXT,
    objective TEXT,
    beneficiary_type TEXT,
    implementation_level TEXT,
    geographic_scope TEXT,
    launch_year INTEGER,
    status TEXT,
    funding_pattern TEXT,
    FOREIGN KEY(scheme_id) REFERENCES schemes(scheme_id) ON DELETE CASCADE
);
