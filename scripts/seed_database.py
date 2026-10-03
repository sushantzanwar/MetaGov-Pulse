"""
==============================================================================
DATABASE SEED & MIGRATION SCRIPT: GOVERNMENT SCHEMES (120 Central Schemes)
Maintainer: Person 4 (Database Engineer) & Person 6 (Integration)
==============================================================================
Reads data/government_schemes_120.csv, validates records, normalizes
ministries and categories into relational tables, and inserts all 120 schemes.
Prevents duplicate IDs, duplicate scheme names, and invalid records.
==============================================================================
"""

import os
import sys
import csv
import sqlite3

# Determine project directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, 'data', 'government_schemes_120.csv')
DB_PATH = os.path.join(BASE_DIR, 'database.db')
SCHEMA_PATH = os.path.join(BASE_DIR, 'database', 'schema.sql')


def seed_database(csv_path=None, db_path=None, schema_path=None, verbose=True):
    target_csv = csv_path or CSV_PATH
    target_db = db_path or DB_PATH
    target_schema = schema_path or SCHEMA_PATH

    if not os.path.exists(target_csv):
        raise FileNotFoundError(f"Source dataset not found at: {target_csv}")

    # Connect to SQLite
    conn = sqlite3.connect(target_db)
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()

    try:
        # Step 1: Wipe old generic / demo tables completely
        cur.executescript("""
            DROP TABLE IF EXISTS activity_log;
            DROP TABLE IF EXISTS records;
            DROP TABLE IF EXISTS scheme_metadata;
            DROP TABLE IF EXISTS schemes;
            DROP TABLE IF EXISTS categories;
            DROP TABLE IF EXISTS ministries;
        """)

        # Execute fresh schema
        with open(target_schema, 'r', encoding='utf-8') as f:
            cur.executescript(f.read())
        conn.commit()

        # Step 2: Read and parse CSV
        with open(target_csv, 'r', encoding='utf-8') as f:
            reader = list(csv.DictReader(f))

        seen_scheme_ids = set()
        seen_scheme_names = set()
        duplicate_scheme_ids = 0
        duplicate_scheme_names = 0
        invalid_records = 0
        valid_rows = []

        # Step 3: Validate required fields and uniqueness
        for idx, row in enumerate(reader, start=1):
            s_id = (row.get('scheme_id') or '').strip()
            s_name = (row.get('scheme_name') or '').strip()
            ministry = (row.get('ministry') or '').strip()
            category = (row.get('category') or '').strip()
            scheme_type = (row.get('scheme_type') or '').strip()
            gov_level = (row.get('government_level') or 'Central').strip()

            # Check required fields
            if not s_id or not s_name or not ministry or not category or not scheme_type:
                invalid_records += 1
                if verbose:
                    print(f"[!] Row {idx} has missing required fields: ID={s_id}, Name={s_name}")
                continue

            # Check duplicate scheme ID
            if s_id in seen_scheme_ids:
                duplicate_scheme_ids += 1
                if verbose:
                    print(f"[!] Duplicate scheme_id detected: {s_id}")
                continue
            seen_scheme_ids.add(s_id)

            # Check duplicate scheme name
            if s_name.lower() in seen_scheme_names:
                duplicate_scheme_names += 1
                if verbose:
                    print(f"[!] Duplicate scheme_name detected: {s_name}")
                continue
            seen_scheme_names.add(s_name.lower())

            valid_rows.append(row)

        # Step 4: Extract and insert distinct Ministries
        distinct_ministries = sorted(list({r['ministry'].strip() for r in valid_rows if r['ministry'].strip()}))
        ministry_id_map = {}
        for m_name in distinct_ministries:
            cur.execute("INSERT INTO ministries (name) VALUES (?)", (m_name,))
            ministry_id_map[m_name] = cur.lastrowid

        # Step 5: Extract and insert distinct Categories
        distinct_categories = sorted(list({r['category'].strip() for r in valid_rows if r['category'].strip()}))
        category_id_map = {}
        for c_name in distinct_categories:
            cur.execute("INSERT INTO categories (name) VALUES (?)", (c_name,))
            category_id_map[c_name] = cur.lastrowid

        # Step 6: Insert Schemes
        schemes_imported = 0
        for r in valid_rows:
            s_id = r['scheme_id'].strip()
            s_name = r['scheme_name'].strip()
            m_id = ministry_id_map[r['ministry'].strip()]
            c_id = category_id_map[r['category'].strip()]
            s_type = r['scheme_type'].strip()
            gov_level = (r.get('government_level') or 'Central').strip()
            src_name = (r.get('source_name') or '').strip() or None
            src_url = (r.get('source_url') or '').strip() or None
            last_ver = (r.get('last_verified') or '').strip() or None
            note = (r.get('data_note') or '').strip() or None

            cur.execute("""
                INSERT INTO schemes (
                    scheme_id, scheme_name, ministry_id, category_id,
                    scheme_type, government_level, source_name, source_url,
                    last_verified, data_note
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (s_id, s_name, m_id, c_id, s_type, gov_level, src_name, src_url, last_ver, note))
            schemes_imported += 1

            # Insert initial metadata row (fields left NULL where not supplied)
            cur.execute("""
                INSERT INTO scheme_metadata (
                    scheme_id, department, description, objective,
                    beneficiary_type, implementation_level, geographic_scope,
                    launch_year, status, funding_pattern
                ) VALUES (?, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'Active', NULL)
            """, (s_id,))

        conn.commit()

        # Step 7: Print clean summary
        if verbose:
            print("\n" + "=" * 50)
            print("GOVERNMENT SCHEMES DATASET IMPORT SUMMARY")
            print("=" * 50)
            print(f"{schemes_imported} schemes imported")
            print(f"{duplicate_scheme_ids} duplicate scheme IDs")
            print(f"{duplicate_scheme_names} duplicate scheme names")
            print(f"{invalid_records} invalid required records")
            print(f"Ministries created: {len(distinct_ministries)}")
            print(f"Categories created: {len(distinct_categories)}")
            print("=" * 50 + "\n")

        return {
            "schemes_imported": schemes_imported,
            "duplicate_scheme_ids": duplicate_scheme_ids,
            "duplicate_scheme_names": duplicate_scheme_names,
            "invalid_records": invalid_records,
            "ministries_count": len(distinct_ministries),
            "categories_count": len(distinct_categories)
        }

    finally:
        conn.close()


if __name__ == '__main__':
    seed_database()
