"""
==============================================================================
SYSTEM INTEGRATION & REGRESSION TEST SUITE: GOVERNMENT SCHEMES INTELLIGENCE
Maintainer: Person 6 (Integration & System Assembly)
==============================================================================
Runs standalone in Python without internet or third-party test runners.
Run command: py -m unittest tests/test_app.py
==============================================================================
"""

import os
import gc
import tempfile
import unittest
import json
from app import create_app
from database.db import close_db, query_db
from scripts.seed_database import seed_database


class GovernancePlatformIntegrationTestCase(unittest.TestCase):
    def setUp(self):
        """Create a temporary isolated SQLite database and test client."""
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        os.close(self.db_fd)

        # Seed the temporary database with the verified 120 schemes
        seed_database(db_path=self.db_path, verbose=False)

        self.app = create_app({
            'TESTING': True,
            'DATABASE': self.db_path
        })
        self.client = self.app.test_client()

    def tearDown(self):
        """Clean up database connections and the temporary file on Windows."""
        with self.app.app_context():
            close_db()
        gc.collect()
        try:
            if os.path.exists(self.db_path):
                os.remove(self.db_path)
        except OSError:
            pass

    # --------------------------------------------------------------------------
    # 1. DATABASE INTEGRITY CHECKS
    # --------------------------------------------------------------------------
    def test_120_schemes_exist(self):
        """[CHECKLIST] Verify exactly 120 schemes exist in database."""
        row = query_db("SELECT COUNT(*) as count FROM schemes", one=True, db_path=self.db_path)
        self.assertEqual(row['count'], 120, "Must contain exactly 120 schemes from the dataset")

    def test_no_duplicate_scheme_ids(self):
        """[CHECKLIST] Verify zero duplicate scheme IDs."""
        dups = query_db("""
            SELECT scheme_id, COUNT(*) as count 
            FROM schemes 
            GROUP BY scheme_id 
            HAVING count > 1
        """, db_path=self.db_path)
        self.assertEqual(len(dups), 0, "No duplicate scheme IDs allowed")

    def test_no_duplicate_scheme_names(self):
        """[CHECKLIST] Verify zero duplicate scheme names."""
        dups = query_db("""
            SELECT LOWER(scheme_name) as name, COUNT(*) as count 
            FROM schemes 
            GROUP BY LOWER(scheme_name) 
            HAVING count > 1
        """, db_path=self.db_path)
        self.assertEqual(len(dups), 0, "No duplicate scheme names allowed")

    def test_ministries_and_categories_linked(self):
        """[CHECKLIST] Verify foreign keys correctly link to ministries and categories."""
        unlinked_m = query_db("""
            SELECT s.id FROM schemes s 
            LEFT JOIN ministries m ON s.ministry_id = m.id 
            WHERE m.id IS NULL
        """, db_path=self.db_path)
        self.assertEqual(len(unlinked_m), 0, "All schemes must link to a valid ministry")

        unlinked_c = query_db("""
            SELECT s.id FROM schemes s 
            LEFT JOIN categories c ON s.category_id = c.id 
            WHERE c.id IS NULL
        """, db_path=self.db_path)
        self.assertEqual(len(unlinked_c), 0, "All schemes must link to a valid category")

    def test_no_fake_demo_records_remain(self):
        """[CHECKLIST] Verify old generic records table or fake demo entities are removed."""
        old_table = query_db("SELECT name FROM sqlite_master WHERE type='table' AND name='records'", db_path=self.db_path)
        self.assertEqual(len(old_table), 0, "Old generic 'records' table must not exist")

    # --------------------------------------------------------------------------
    # 2. REST API & DASHBOARD ANALYTICS
    # --------------------------------------------------------------------------
    def test_dashboard_stats_api(self):
        """[CHECKLIST] Verify dashboard statistics are dynamic from database."""
        res = self.client.get('/api/dashboard/stats')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        stats = data['data']
        self.assertEqual(stats['total_schemes'], 120)
        self.assertEqual(stats['total_ministries'], 19)
        self.assertEqual(stats['total_categories'], 44)
        self.assertGreater(len(stats['top_ministries']), 0)
        self.assertGreater(len(stats['category_distribution']), 0)

    def test_schemes_list_and_pagination(self):
        """[CHECKLIST] Verify pagination works at 20 records per page."""
        res = self.client.get('/api/schemes?page=1&per_page=20')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(len(data['schemes']), 20)
        self.assertEqual(data['total'], 120)
        self.assertEqual(data['total_pages'], 6)

        # Page 6 should have remaining 20
        res_p6 = self.client.get('/api/schemes?page=6&per_page=20')
        self.assertEqual(len(res_p6.get_json()['schemes']), 20)

    def test_search_schemes(self):
        """[CHECKLIST] Verify database-backed search on keywords."""
        # Search 'farmer'
        res = self.client.get('/api/schemes?q=farmer')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertGreaterEqual(data['total'], 1)
        for s in data['schemes']:
            text = (s['scheme_name'] + ' ' + s['ministry'] + ' ' + s['category']).lower()
            self.assertTrue('farmer' in text or 'farm' in text or 'kisan' in text)

        # Direct search endpoint
        res2 = self.client.get('/api/search?q=education')
        self.assertEqual(res2.status_code, 200)
        data2 = res2.get_json()
        self.assertGreaterEqual(data2['total'], 1)

    def test_filters_and_sorting(self):
        """[CHECKLIST] Verify filters on ministry, category, and column sorting."""
        # Filter by Ministry of Finance
        min_row = query_db("SELECT id FROM ministries WHERE name = 'Ministry of Finance'", one=True, db_path=self.db_path)
        self.assertIsNotNone(min_row)
        res = self.client.get(f'/api/schemes?ministry_id={min_row["id"]}')
        data = res.get_json()
        self.assertTrue(data['success'])
        for s in data['schemes']:
            self.assertEqual(s['ministry'], 'Ministry of Finance')

        # Sort by scheme_name DESC
        res_sort = self.client.get('/api/schemes?sort_by=scheme_name&sort_dir=desc')
        names = [s['scheme_name'] for s in res_sort.get_json()['schemes']]
        self.assertEqual(names, sorted(names, reverse=True))

    def test_scheme_detail_and_source_link(self):
        """[CHECKLIST] Verify single scheme retrieval includes verified source URL."""
        res = self.client.get('/api/schemes/SCH001')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        s = data['data']
        self.assertEqual(s['scheme_id'], 'SCH001')
        self.assertIn('Pradhan Mantri Kisan Samman Nidhi', s['scheme_name'])
        self.assertTrue(s['source_url'].startswith('https://'))

    def test_ministry_and_category_analytics_endpoints(self):
        """[CHECKLIST] Verify /api/ministries, /api/categories, /api/analytics endpoints."""
        m_res = self.client.get('/api/ministries')
        self.assertEqual(m_res.status_code, 200)
        self.assertEqual(len(m_res.get_json()['data']), 19)

        c_res = self.client.get('/api/categories')
        self.assertEqual(c_res.status_code, 200)
        self.assertEqual(len(c_res.get_json()['data']), 44)

        t_res = self.client.get('/api/analytics/scheme-type')
        self.assertEqual(t_res.status_code, 200)
        self.assertGreater(len(t_res.get_json()['data']), 0)

    def test_cross_ministry_relationships(self):
        """[CHECKLIST] Verify cross-ministry relationship intersections."""
        res = self.client.get('/api/analytics/cross-ministry')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        self.assertIn('cross_cutting_categories', data['data'])
        self.assertIn('ministries_hierarchy', data['data'])
        self.assertGreater(len(data['data']['cross_cutting_categories']), 0)

    def test_scheme_comparison(self):
        """[CHECKLIST] Verify factual scheme comparison without winner/score."""
        payload = {"scheme_ids": ["SCH001", "SCH002"]}
        res = self.client.post('/api/compare', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        comp = data['data']
        self.assertEqual(comp['count'], 2)
        # Ensure no arbitrary score fields
        for attr in comp['attributes']:
            self.assertNotIn('score', attr['key'].lower())
            self.assertNotIn('winner', attr['key'].lower())

    def test_html_views_render(self):
        """[CHECKLIST] Verify all pages render without server errors."""
        routes = ['/', '/schemes', '/ministries', '/categories', '/cross-ministry', '/comparison', '/data-sources']
        for route in routes:
            r = self.client.get(route)
            self.assertEqual(r.status_code, 200, f"Route {route} must return 200")
            self.assertIn(b'Government', r.data)

    def test_health_check_offline(self):
        """[CHECKLIST] Verify offline health check status."""
        res = self.client.get('/api/health')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get('status'), 'healthy')
        self.assertEqual(data.get('mode'), '100% offline-ready')


if __name__ == '__main__':
    unittest.main()
