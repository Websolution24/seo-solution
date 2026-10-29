"""Offline contract tests. All properties and data below are fictional."""
from __future__ import annotations

from pathlib import Path
import tempfile
import tomllib
import unittest

from gsc_client import GSCClient, GSCError, SCOPE, build_query
from setup_connector import config_block, register_config


class FakeHTTP:
    def __init__(self, responses=None):
        self.calls = []
        self.responses = list(responses or [])

    def __call__(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        return self.responses.pop(0) if self.responses else {}


class ClientTests(unittest.TestCase):
    def test_readonly_scope(self):
        self.assertEqual(SCOPE, 'https://www.googleapis.com/auth/webmasters.readonly')

    def test_property_selection_limits_sites(self):
        http = FakeHTTP([{'siteEntry': [{'siteUrl': 'sc-domain:example.com', 'permissionLevel': 'siteOwner'},
                                       {'siteUrl': 'sc-domain:other.example', 'permissionLevel': 'siteOwner'}]}])
        result = GSCClient(http, 'sc-domain:example.com').list_sites()
        self.assertEqual([x['site_url'] for x in result['sites']], ['sc-domain:example.com'])

    def test_stats_request_and_measured_values(self):
        rows = [{'keys': ['test fictif'], 'clicks': 3, 'impressions': 20, 'ctr': 0.15, 'position': 7.5}]
        http = FakeHTTP([{'rows': rows, 'responseAggregationType': 'byProperty'}])
        result = GSCClient(http).search_analytics('sc-domain:example.com', '2026-09-01', '2026-09-30', ['query'])
        self.assertIn('sc-domain%3Aexample.com/searchAnalytics/query', http.calls[0][1])
        self.assertEqual(http.calls[0][2]['json']['dataState'], 'final')
        self.assertEqual(result['rows'], rows)
        self.assertEqual(result['period']['timezone'], 'America/Los_Angeles')

    def test_url_property_is_one_encoded_path_segment(self):
        http = FakeHTTP()
        GSCClient(http).list_sitemaps('https://example.com/shop/')
        self.assertIn('https%3A%2F%2Fexample.com%2Fshop%2F/sitemaps', http.calls[0][1])

    def test_invalid_period_prevents_api_call(self):
        http = FakeHTTP()
        for start, end in [('2026-09-31', '2026-10-01'), ('20260901', '2026-10-01'), ('2026-10-02', '2026-10-01')]:
            with self.assertRaises(GSCError):
                GSCClient(http).search_analytics('sc-domain:example.com', start, end)
        self.assertEqual(http.calls, [])

    def test_invalid_dimensions_and_limits(self):
        for dims in [['page', 'page'], ['not_a_dimension'], 'query']:
            with self.assertRaises(GSCError):
                build_query('2026-09-01', '2026-09-30', dims)
        for limit in [0, 25001, True]:
            with self.assertRaises(GSCError):
                build_query('2026-09-01', '2026-09-30', row_limit=limit)

    def test_filters_preserved_as_and_group(self):
        filters = [{'dimension': 'country', 'operator': 'equals', 'expression': 'fra'},
                   {'dimension': 'page', 'operator': 'contains', 'expression': '/test/'}]
        query = build_query('2026-09-01', '2026-09-30', ['query', 'page'], filters)
        self.assertEqual(query['dimensionFilterGroups'], [{'groupType': 'and', 'filters': filters}])

    def test_unknown_filter_fields_rejected(self):
        with self.assertRaises(GSCError):
            build_query('2026-09-01', '2026-09-30', filters=[{'dimension': 'page', 'expression': '/', 'endpoint': 'external'}])

    def test_pagination_is_explicit_and_bounded(self):
        http = FakeHTTP([{'rows': [{'keys': ['one']}, {'keys': ['two']}]}])
        result = GSCClient(http).search_analytics('sc-domain:example.com', '2026-09-01', '2026-09-30', ['page'], row_limit=2, start_row=4)
        self.assertEqual(result['next_start_row'], 6)
        self.assertEqual(len(http.calls), 1)
        self.assertTrue(result['limitations'])

    def test_empty_response_does_not_invent_rows(self):
        result = GSCClient(FakeHTTP()).search_analytics('sc-domain:example.com', '2026-09-01', '2026-09-30')
        self.assertEqual(result['rows'], [])
        self.assertIsNone(result['next_start_row'])

    def test_comparison_uses_identical_filters_and_keeps_datasets(self):
        http = FakeHTTP([{'rows': [{'clicks': 2}]}, {'rows': []}])
        result = GSCClient(http).compare_periods('sc-domain:example.com', '2026-09-08', '2026-09-14', '2026-09-01', '2026-09-07', ['page'], [{'dimension': 'device', 'expression': 'MOBILE'}])
        self.assertEqual(len(http.calls), 2)
        for field in ['dimensions', 'dimensionFilterGroups', 'type', 'rowLimit']:
            self.assertEqual(http.calls[0][2]['json'][field], http.calls[1][2]['json'][field])
        self.assertEqual(result['comparison']['rows'], [])

    def test_unequal_comparison_rejected_before_requests(self):
        http = FakeHTTP()
        with self.assertRaises(GSCError):
            GSCClient(http).compare_periods('sc-domain:example.com', '2026-09-01', '2026-09-07', '2026-08-01', '2026-08-31')
        self.assertEqual(http.calls, [])

    def test_other_client_is_rejected(self):
        http = FakeHTTP()
        with self.assertRaises(GSCError):
            GSCClient(http, 'sc-domain:example.com').list_sitemaps('sc-domain:other.example')
        self.assertEqual(http.calls, [])

    def test_url_inspection_is_read_request(self):
        http = FakeHTTP([{'inspectionResult': {'indexStatusResult': {'verdict': 'PASS'}}}])
        result = GSCClient(http).inspect_url('sc-domain:example.com', 'https://shop.example.com/test/')
        self.assertEqual(http.calls[0][0], 'POST')
        self.assertEqual(http.calls[0][2]['json']['siteUrl'], 'sc-domain:example.com')
        self.assertIn('inspection_result', result)

    def test_lookalike_domains_and_other_origins_are_rejected(self):
        for site, url in [('sc-domain:example.com', 'https://example.com.evil.invalid/'),
                          ('https://example.com', 'https://example.com.evil.invalid/'),
                          ('https://example.com/', 'http://example.com/'),
                          ('https://example.com/shop/', 'https://example.com/other/')]:
            http = FakeHTTP()
            with self.assertRaises(GSCError):
                GSCClient(http).inspect_url(site, url)
            self.assertEqual(http.calls, [])


class SetupTests(unittest.TestCase):
    def test_generated_config_has_only_local_nonsecret_settings(self):
        data = tomllib.loads(config_block(Path('/fictional/connector'), 'test-profile', 'sc-domain:example.com', True))
        server = data['mcp_servers']['google_search_console']
        self.assertTrue(server['enabled'])
        self.assertEqual(server['env'], {'GSC_PROFILE': 'test-profile', 'GSC_SITE_URL': 'sc-domain:example.com'})
        self.assertEqual(len(server['enabled_tools']), 6)
        self.assertNotIn('bearer_token_env_var', server)

    def test_registration_preserves_existing_config(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'.codex').mkdir()
            target = root/'.codex/config.toml'
            original = '# Existing user choice\nmodel = "existing-model"\n'
            target.write_text(original, encoding='utf-8')
            self.assertTrue(register_config(root, config_block(root, 'qa', None, False)))
            self.assertTrue(target.read_text(encoding='utf-8').startswith(original))
            self.assertEqual(tomllib.loads(target.read_text(encoding='utf-8'))['model'], 'existing-model')

    def test_duplicate_registration_never_overwrites(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            block = config_block(root, 'qa', 'sc-domain:example.com', True)
            self.assertTrue(register_config(root, block))
            before = (root/'.codex/config.toml').read_bytes()
            self.assertFalse(register_config(root, block))
            self.assertEqual((root/'.codex/config.toml').read_bytes(), before)

    def test_quoted_server_name_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'.codex').mkdir()
            target = root/'.codex/config.toml'
            original = "[mcp_servers.'google_search_console']\ncommand = 'existing'\n"
            target.write_text(original, encoding='utf-8')
            self.assertFalse(register_config(root, config_block(root, 'qa', None, False)))
            self.assertEqual(target.read_text(encoding='utf-8'), original)

    def test_invalid_existing_config_is_never_changed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'.codex').mkdir()
            target = root/'.codex/config.toml'
            original = 'model = [invalid\n'
            target.write_text(original, encoding='utf-8')
            with self.assertRaises(OSError):
                register_config(root, config_block(root, 'qa', None, False))
            self.assertEqual(target.read_text(encoding='utf-8'), original)


class TransportTests(unittest.TestCase):
    def make_transport(self, status, raises=False):
        from gsc_auth import GoogleTransport
        class Vault:
            def save(self, value):
                self.saved = value
        class Credentials:
            def to_json(self):
                return 'fictional-test-credential'
        class Response:
            status_code = status
            def json(self):
                return {'rows': []}
        class Session:
            calls = []
            def request(self, *args, **kwargs):
                self.calls.append((args, kwargs))
                if raises:
                    raise RuntimeError('SYNTHETIC_PRIVATE_DETAIL')
                return Response()
        transport = GoogleTransport.__new__(GoogleTransport)
        transport.vault, transport.credentials, transport.session = Vault(), Credentials(), Session()
        return transport

    def test_no_mutation_method(self):
        transport = self.make_transport(200)
        with self.assertRaises(GSCError):
            transport('DELETE', 'https://www.googleapis.com/webmasters/v3/sites/sc-domain%3Aexample.com')
        self.assertEqual(transport.session.calls, [])

    def test_only_exact_read_endpoint_paths_are_allowed(self):
        transport = self.make_transport(200)
        for method, url in [('GET', 'https://www.googleapis.com/webmasters/v3/sites-unexpected'),
                            ('GET', 'https://www.googleapis.com/webmasters/v3/sites/anything'),
                            ('POST', 'https://www.googleapis.com/webmasters/v3/sites/a/b/searchAnalytics/query'),
                            ('POST', 'https://external.invalid/searchAnalytics/query')]:
            with self.assertRaises(GSCError):
                transport(method, url)
        self.assertEqual(transport.session.calls, [])
        transport('GET', 'https://www.googleapis.com/webmasters/v3/sites/sc-domain%3Aexample.com/sitemaps')
        transport('POST', 'https://www.googleapis.com/webmasters/v3/sites/sc-domain%3Aexample.com/searchAnalytics/query', json={})
        self.assertEqual(len(transport.session.calls), 2)

    def test_http_failures_and_quota_do_not_retry(self):
        for status in [401, 403, 429, 500, 302]:
            transport = self.make_transport(status)
            with self.assertRaises(GSCError):
                transport('GET', 'https://www.googleapis.com/webmasters/v3/sites')
            self.assertEqual(len(transport.session.calls), 1)
            self.assertFalse(transport.session.calls[0][1]['allow_redirects'])

    def test_private_exception_detail_is_not_returned(self):
        transport = self.make_transport(200, raises=True)
        with self.assertRaises(GSCError) as caught:
            transport('GET', 'https://www.googleapis.com/webmasters/v3/sites')
        self.assertNotIn('SYNTHETIC_PRIVATE_DETAIL', str(caught.exception))


if __name__ == '__main__':
    unittest.main()
