"""Regressions for failures reproduced in the post-handoff critical review."""
import copy
from datetime import timedelta
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path[:0] = [str(Path(__file__).resolve().parents[1] / 'scripts/news-scraper')]
from health import HealthFailure, monitor
from main import atomic, run
from news import excerpt, extract
from relevance import classify
from soak import assess, output_directory
from state import validate
from test_news import ARTICLE, Http, Judge, NOW, URL, item


class ReviewFixTests(unittest.TestCase):
    def test_keyword_coincidence_cannot_establish_affiliation(self):
        value = dict(item(), title='Campus profile')
        for body in [
            'WMU welcomed University of Michigan mechanical engineering professor Jane Smith.',
            'WMU student Kevin joined a fraternity that promotes careers in aeronautical engineering.',
            'WMU does not offer a mechanical engineering degree at this satellite campus.',
            'WMU aerospace engineering students were visiting researchers from Stanford University.',
        ]:
            with self.subTest(body=body):
                self.assertIsNone(classify(value, body))
        for body in ['WMU aerospace engineering alumnus built a new aircraft.',
                     'She earned a degree in aerospace engineering at Western Michigan University.']:
            self.assertTrue(classify(value, body)['relevant'])

    def test_ordinary_welcome_and_registration_reporting_remains_news(self):
        for body in ['welcomes a new approach to propulsion research.',
                     'developed a registration system for wind tunnel testing.',
                     'presented results at a conference last week.']:
            html = ARTICLE.replace('tested a new propulsion system.', body)
            self.assertFalse(extract(html, URL, NOW)[2])

    @patch('main.source_urls', return_value=['https://wmich.edu/engineer/news'])
    def test_existing_story_survives_parser_drift(self, _):
        class Changed(Http):
            def get(self, url):
                return super().get(url).replace('tested a new propulsion system.', 'welcomes a new approach to propulsion research.')
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            run(root, client=Http(), classifier=Judge(), now=NOW)
            report, _ = run(root, client=Changed(), classifier=Judge(), now=NOW + timedelta(hours=25))
            self.assertEqual(report['items'], 1)
            class Broken(Http):
                def get(self, url):
                    return '<main>Changed publisher markup</main>' if url == URL else super().get(url)
            report, _ = run(root, client=Broken(), classifier=Judge(), now=NOW + timedelta(hours=50))
            self.assertEqual(report['items'], 1)
            self.assertEqual(report['pendingRetrieval'], 1)
            self.assertEqual(report['status'], 'partial')

    @patch('main.source_urls', return_value=['https://wmich.edu/engineer/news'])
    def test_event_parser_failure_retains_but_verified_cancellation_removes(self, _):
        url = 'https://wmich.edu/engineer/events/career-fair'
        event = {'@type': 'Event', 'name': 'Engineering career fair',
                 'startDate': '2026-11-04T13:00:00-05:00', 'description': 'An engineering career fair open to all students.'}
        class EventHttp:
            markup = True
            def get(self, target):
                if target != url: return '<main><a href="' + url + '">Event</a></main>'
                return '<article><h1>Engineering career fair</h1></article>' + (
                    '<script type="application/ld+json">' + json.dumps(event) + '</script>' if self.markup else '')
        with tempfile.TemporaryDirectory() as d:
            root, http = Path(d), EventHttp()
            first, _ = run(root, client=http, classifier=Judge(), now=NOW)
            self.assertEqual(first['items'], 1)
            http.markup = False
            second, _ = run(root, client=http, classifier=Judge(), now=NOW + timedelta(hours=25))
            self.assertEqual(second['items'], 1)
            self.assertEqual(second['pendingRetrieval'], 1)
            http.markup = True
            event['eventStatus'] = 'https://schema.org/EventCancelled'
            third, _ = run(root, client=http, classifier=Judge(), now=NOW + timedelta(hours=50))
            self.assertEqual(third['items'], 0)

    @patch('main.source_urls', return_value=['https://wmich.edu/engineer/news'])
    def test_held_decision_stays_visible_when_nothing_is_due(self, _):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            first, _ = run(root, client=Http(), classifier=Judge(None), now=NOW)
            second, _ = run(root, client=Http(), classifier=Judge(), now=NOW + timedelta(minutes=10))
            self.assertEqual(first['deferred'], 0)
            self.assertEqual(second['deferred'], 0)
            self.assertEqual(second['pendingClassification'], 1)
            self.assertEqual(second['status'], 'partial')
            third, _ = run(root, client=Http(), classifier=Judge(), now=NOW + timedelta(hours=7))
            self.assertEqual(third['pendingClassification'], 0)
            self.assertEqual(third['items'], 1)

    @patch('main.source_urls', return_value=['https://wmich.edu/engineer/news'])
    def test_legacy_failed_inventory_is_not_reported_as_fully_reviewed(self, _):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            atomic(root / 'scripts/news-scraper/state.json', {'version': 1, 'decisions': {},
                'inventory': {URL: {'lastAttempt': '2026-10-20T14:00:00Z', 'retryAfter': '2026-10-21T14:00:00Z', 'failures': 1}}})
            report, _ = run(root, client=Http(), classifier=Judge(), now=NOW)
            self.assertEqual(report['unreviewed'], 1)
            self.assertEqual(report['status'], 'partial')

    @patch('main.source_urls', return_value=['https://wmich.edu/engineer/news'])
    def test_changed_policy_revalidates_successes_without_waiting_a_day(self, _):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            run(root, client=Http(), classifier=Judge(), now=NOW)
            with patch('main.PROMPT_VERSION', 'new-policy'):
                report, _ = run(root, client=Http(), classifier=Judge(False), now=NOW + timedelta(minutes=10))
            self.assertEqual(report['items'], 0)
            self.assertEqual(report['rejected'], 1)

    def test_excerpt_keeps_complete_source_sentences_and_abbreviations(self):
        value = 'Dr. Smith studies propulsion. ' + 'The research helps students build spacecraft. ' * 10
        short = excerpt(value, 100)
        self.assertTrue(value.startswith(short))
        self.assertTrue(short.endswith('.'))
        self.assertNotEqual(short, 'Dr.')
        self.assertLessEqual(len(short), 100)

    def health(self):
        payload = b'{"items":[]}'
        value = {'schemaVersion': 1, 'checkedAt': '2026-10-20T15:00:00Z', 'status': 'partial',
                 'items': 0, 'classifierStatus': 'available', 'automaticRules': 'rules-4',
                 'sources': [{'source': 'https://wmich.edu/engineer/news', 'status': 'ok'}],
                 'inventory': 0, 'deferred': 0, 'socialCoverage': 'not_connected',
                 'feedSha256': hashlib.sha256(payload).hexdigest()}
        return value, payload

    def test_health_retries_transient_fetch_and_preserves_sanitized_cause(self):
        value, payload = self.health()
        attempts = []
        def fetch(url, _):
            if 'raw.githubusercontent' in url:
                attempts.append(url)
                if len(attempts) == 1: raise OSError('DO_NOT_LOG_SECRET')
                return json.dumps(value).encode()
            return payload
        self.assertEqual(monitor(fetch, lambda _: None, NOW)['items'], 0)
        self.assertEqual(len(attempts), 2)
        with self.assertRaisesRegex(HealthFailure, '^health_fetch:network_error$'):
            monitor(lambda *_: (_ for _ in ()).throw(OSError('DO_NOT_LOG_SECRET')), lambda _: None, NOW)
        value['checkedAt'] = '2026-10-01T00:00:00Z'
        with self.assertRaisesRegex(HealthFailure, '^health_validation:collector_stale_or_future$'):
            monitor(lambda *_: json.dumps(value).encode(), lambda _: None, NOW)

    def test_health_mismatch_is_distinguished_from_fetch_failure(self):
        value, _ = self.health()
        with self.assertRaisesRegex(HealthFailure, '^public_feed:public_feed_mismatch$'):
            monitor(lambda url, _: json.dumps(value).encode() if 'raw.githubusercontent' in url else b'wrong', lambda _: None, NOW)

    def test_state_rejects_unknown_outcomes(self):
        entry = {'lastAttempt': '2026-10-20T15:00:00Z', 'retryAfter': '2026-10-21T15:00:00Z', 'failures': 0, 'outcome': 'made_up'}
        with self.assertRaises(ValueError): validate({'version': 1, 'decisions': {}, 'inventory': {URL: entry}})

    def pages(self):
        return [{'width': w, 'height': h, 'assetVersion': 'test', 'advanceCount': 20, 'sinceAdvanceMs': 1000,
                 'timeOrigin': 1, 'currentDuration': 25000, 'paused': False, 'visibility': 'visible',
                 'newsEnabled': True, 'newsItems': 7, 'errors': 0, 'unhandledRejections': 0}
                for w, h in [(2560, 1440), (2048, 1152)]]

    def test_soak_detects_stalls_errors_restarts_and_missing_news(self):
        host = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa\nActiveState=active\nActiveEnterTimestamp=Today\n'
        pages = self.pages()
        good = assess(pages, {}, host, 'test')
        self.assertEqual(good['issues'], [])
        prior = dict(good, pages=copy.deepcopy(pages))
        pages[0].update({'advanceCount': 21, 'newsItems': 0, 'errors': 1})
        pages[1].update({'sinceAdvanceMs': 120000})
        bad = assess(pages, prior, host.replace('Today', 'Later').replace('aaaaaaaa-', 'bbbbbbbb-', 1), 'test')
        self.assertIn('2560:expected_news_missing', bad['issues'])
        self.assertIn('2560:javascript_errors', bad['issues'])
        self.assertIn('2048:slide_progress_stalled', bad['issues'])
        self.assertIn('host_rebooted', bad['issues'])
        self.assertIn('kiosk_service_restarted', bad['issues'])

    def test_soak_never_overwrites_old_evidence_or_writes_outside_scratch(self):
        with tempfile.TemporaryDirectory() as d, patch('soak.ROOT', Path(d)):
            target = Path(d) / 'scratch' / 'run'
            self.assertEqual(output_directory(str(target)), target.resolve())
            with self.assertRaises(FileExistsError): output_directory(str(target))
            with self.assertRaises(ValueError): output_directory(str(Path(d) / 'outside'))

    def test_soak_does_not_call_a_short_final_interval_a_stall(self):
        host = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa\nActiveState=active\nActiveEnterTimestamp=Today\n'
        pages = self.pages()
        for page in pages: page['observedAtMs'] = 10000
        previous = dict(assess(pages, {}, host, 'test'), pages=copy.deepcopy(pages))
        for page in pages: page['observedAtMs'] = 12000
        self.assertEqual(assess(pages, previous, host, 'test')['issues'], [])
        for page in pages: page['observedAtMs'] = 200000
        self.assertIn('2560:slide_progress_not_advanced', assess(pages, previous, host, 'test')['issues'])


if __name__ == '__main__': unittest.main()
