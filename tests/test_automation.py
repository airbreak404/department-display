from datetime import datetime, timedelta, timezone
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/news-scraper'))
from events import extract_event, CUSTER
from health import check, verify_deployment
from main import run
from news import merge, validate_item
from relevance import classify
from state import validate as validate_state
from classifier import Classifier, MAX_CALLS
from test_news import ARTICLE, Http, Judge, NOW, URL, item
import publish


class AutomationTests(unittest.TestCase):
    def test_vendored_qr_encoder_matches_reviewed_distribution(self):
        import hashlib
        path = Path(__file__).resolve().parents[1] / 'js/vendor/qrcodegen.js'
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),
                         '2511bc17f40a3c41d4a0578995db956b38997334d3d20113a5d4dc5c49c69480')
    def judge(self):
        judge = Classifier.__new__(Classifier)
        judge.client, judge.calls, judge.last_call = Mock(), 0, 0
        judge.error, judge.failures, judge.consecutive_failures = None, {}, 0
        return judge

    @patch('classifier.time.sleep')
    def test_ai_quota_stops_without_leaking_exception(self, _):
        judge = self.judge()
        class Quota(Exception): code = 429
        judge.client.models.generate_content.side_effect = Quota('DO_NOT_LOG_CANARY')
        self.assertIsNone(judge.classify(item(), 'untrusted article'))
        self.assertIsNone(judge.client)
        self.assertEqual(judge.calls, 1)
        self.assertEqual(judge.error, 'api_unavailable')
        self.assertNotIn('CANARY', json.dumps(judge.failures))

    @patch('classifier.time.sleep')
    def test_ai_invalid_response_breaker_and_call_cap(self, _):
        judge = self.judge()
        judge.client.models.generate_content.return_value.text = '{'
        for _ in range(3): self.assertIsNone(judge.classify(item(), 'untrusted article'))
        self.assertEqual(judge.calls, 6)
        self.assertEqual(judge.error, 'circuit_open')
        self.assertIsNone(judge.client)
        judge = self.judge()
        judge.calls = MAX_CALLS
        self.assertIsNone(judge.classify(item(), 'untrusted article'))
        judge.client.models.generate_content.assert_not_called()

    @patch('classifier.time.sleep')
    def test_ai_configuration_and_recovery(self, _):
        judge = self.judge()
        judge.error, judge.consecutive_failures = 'classification_failed', 1
        judge.client.models.generate_content.return_value.text = json.dumps({'id': item()['id'], 'relevant': True, 'reason': 'Explicit MAE appointment'})
        self.assertTrue(judge.classify(item(), 'public article')['relevant'])
        self.assertIsNone(judge.error)
        config = judge.client.models.generate_content.call_args.kwargs['config']
        self.assertEqual(config.tools, [])
        self.assertEqual(config.max_output_tokens, 1024)
        self.assertEqual(config.response_mime_type, 'application/json')

    def test_offline_relevance_and_foreign_department(self):
        direct = 'Western Michigan University aerospace engineering alumnus developed a new aircraft.'
        self.assertTrue(classify(item(), direct)['relevant'])
        self.assertIsNone(classify(item(), 'WMU hosts a professor in mechanical and aerospace engineering at NC State University.'))
        self.assertIsNone(classify(item(), 'WMU hosts a professor of mechanical engineering from University of Michigan.'))
        self.assertIsNone(classify(item(), 'WMU electrical engineering students received a scholarship.'))
        self.assertFalse(classify(dict(item(), title='Student music recital'), 'WMU students perform music for all students.')['relevant'])

    def test_inclusive_ceas_opportunity(self):
        opportunity = dict(item(), title='Engineering career fair')
        self.assertTrue(classify(opportunity, 'An engineering career fair is open to all students.')['relevant'])
        self.assertIsNone(classify(item(), 'A scholarship is available only to paper engineering students.'))
        self.assertIsNone(classify(dict(item(), url='https://wmich.edu/music/news/2026/10/x'), 'A workshop is open to all students.'))

    def test_automatic_without_key_and_no_manual_queue(self):
        class LocalHttp(Http):
            def get(self, url):
                return super().get(url).replace('Mechanical and aerospace', 'WMU mechanical and aerospace')
        with tempfile.TemporaryDirectory() as temp, patch('main.source_urls', return_value=['https://wmich.edu/engineer/news']):
            judge = Judge(None)
            judge.error = 'missing_key'
            report, code = run(Path(temp), client=LocalHttp(), classifier=judge, now=NOW)
            self.assertEqual((code, report['rulesApproved'], report['items'], judge.calls), (0, 1, 1, 0))
            self.assertTrue(report['automationReady'])

    def test_persistent_backoff_and_cache_recovery(self):
        with tempfile.TemporaryDirectory() as temp, patch('main.source_urls', return_value=['https://wmich.edu/engineer/news']):
            root = Path(temp)
            run(root, client=Http([URL]), classifier=Judge(), now=NOW)
            state = json.loads((root / 'scripts/news-scraper/state.json').read_text())
            self.assertEqual(state['inventory'][URL]['failures'], 1)
            report, _ = run(root, client=Http(), classifier=Judge(), now=NOW + timedelta(minutes=30))
            self.assertEqual(report['candidates'], [])
            (root / 'scripts/news-scraper/state.json').write_text('{')
            report, _ = run(root, client=Http(), classifier=Judge(), now=NOW + timedelta(hours=4))
            self.assertTrue(report['cacheRecovered'])
            self.assertEqual(report['items'], 1)

    def test_event_dates_expiry_and_cancel(self):
        event = {'@type': 'Event', 'name': 'MAE career fair', 'startDate': '2026-11-04T13:00:00-05:00',
                 'endDate': '2026-11-04T15:00:00-05:00', 'description': 'Open to all students.'}
        def markup(value):
            return '<article><h1>MAE career fair</h1></article><script type="application/ld+json">' + json.dumps(value) + '</script>'
        value, _ = extract_event(markup(event), 'https://wmich.edu/engineer/events/career-fair', NOW)
        self.assertIsNone(value['publishedDate'])
        self.assertEqual(value['eventStartsAt'], '2026-11-04T18:00:00Z')
        self.assertEqual(value['expiresAt'], value['eventStartsAt'])
        validate_item(value, NOW)
        self.assertEqual(merge([value], [], set(), datetime(2026, 11, 4, 18, tzinfo=timezone.utc)), [])
        for changed in [dict(event, startDate='2026-11-04'), dict(event, startDate='2026-11-04T13:00:00'),
                        dict(event, eventStatus='https://schema.org/EventCancelled'),
                        dict(event, name='Unrelated event'), dict(event, endDate='2026-11-03T15:00:00-05:00')]:
            with self.assertRaises(ValueError):
                extract_event(markup(changed), value['url'], NOW)

    def test_series_does_not_recycle_past_talks_or_guess_year(self):
        markup = '''<article><h1>Custer Speaker Series</h1><h2>Fall 2026 Speakers</h2>
        <div class="accordion-item"><h4>Jason Tedrow</h4><h5>Engineering leadership</h5>
        <p>Wednesday, Nov. 4<br>1 p.m., Floyd Hall</p></div></article>'''
        value, _ = extract_event(markup, CUSTER, NOW)
        self.assertEqual(value['expiresAt'], '2026-11-04T18:00:00Z')
        for broken in [markup.replace('Fall 2026 Speakers', 'Speakers'), markup.replace('Wednesday', 'Tuesday')]:
            with self.assertRaises(ValueError): extract_event(broken, CUSTER, NOW)
        with self.assertRaises(ValueError): extract_event(markup, CUSTER, NOW + timedelta(days=20))

    def test_health_checks_run_age_independently_of_content_age(self):
        value = {'schemaVersion': 1, 'checkedAt': '2026-10-20T15:00:00Z', 'status': 'ok', 'items': 6,
                 'classifierStatus': 'available', 'automaticRules': 'rules-1', 'sources': [{'source': 'https://wmich.edu/engineer/news', 'status': 'ok'}],
                 'inventory': 10, 'deferred': 0, 'socialCoverage': 'not_connected'}
        check(value, NOW)
        with self.assertRaises(ValueError): check(value, NOW + timedelta(hours=19))
        with self.assertRaises(ValueError): check(dict(value, sources=[]), NOW)

    def test_health_detects_missing_publication_even_with_fresh_collection(self):
        import hashlib
        payload = b'{"schemaVersion":1,"contentUpdatedAt":null,"items":[]}'
        health = {'feedSha256': hashlib.sha256(payload).hexdigest()}
        verify_deployment(health, payload)
        with self.assertRaises(ValueError): verify_deployment(health, payload + b' ')
        with self.assertRaises(ValueError): verify_deployment({}, payload)

    def test_tampered_cache_cannot_approve(self):
        with self.assertRaises(ValueError): validate_state({'version': 1, 'decisions': {'bad': {}}, 'inventory': {}})
        with self.assertRaises(ValueError): validate_state({'version': 1, 'decisions': {}, 'inventory': {'https://evil.example/x': {}}})

    def test_publisher_validates_all_artifacts_before_replacing_feed(self):
        with tempfile.TemporaryDirectory() as temp, patch('main.source_urls', return_value=['https://wmich.edu/engineer/news']):
            root = Path(temp)
            run(root, client=Http(), classifier=Judge(), now=NOW)
            before = (root / 'data/news.json').read_bytes()
            artifacts = root / 'incoming'
            artifacts.mkdir()
            for path, name in [('data/news.json', 'news.json'), ('data/news-health.json', 'news-health.json')]:
                (artifacts / name).write_bytes((root / path).read_bytes())
            (artifacts / 'state.json').write_text(json.dumps({'version': 1, 'decisions': {'tampered': {}}}))
            with patch('publish.ROOT', root), self.assertRaises(ValueError): publish.apply(artifacts)
            self.assertEqual((root / 'data/news.json').read_bytes(), before)
            (artifacts / 'state.json').write_text(json.dumps({'version': 1, 'decisions': {}, 'inventory': {}}))
            (artifacts / 'unexpected.json').write_text('{}')
            with patch('publish.ROOT', root), self.assertRaises(ValueError): publish.apply(artifacts)
            self.assertEqual((root / 'data/news.json').read_bytes(), before)


if __name__ == '__main__': unittest.main()
