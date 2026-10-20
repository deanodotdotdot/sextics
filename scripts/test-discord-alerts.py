#!/usr/bin/env python3
import copy
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import urllib.error

spec = importlib.util.spec_from_file_location('alerts', Path(__file__).with_name('discord-alerts.py'))
alerts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(alerts)


def record(rid, solved=False):
    return {'id': rid, 'title': rid.title(), 'status': 'solved' if solved else 'open',
            'formalStatus': 'proved' if solved else 'unproved'}


class Alerts(unittest.TestCase):
    def setUp(self):
        self.old = {'records': [record('old-solve', True), record('open-target')]}
        self.state = alerts.snapshot(self.old)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.site = Path(self.tmp.name)
        for rid in ('open-target', 'new-target'):
            path = self.site / 'data' / rid
            path.mkdir(parents=True)
            (path / 'record.json').write_text(json.dumps({
                'credit': {'githubLogin': 'solver'},
                'pullRequest': {'number': 153, 'url': alerts.REPO + '/pull/153'}}))

    def test_bootstrap_and_ordinary_edits_do_not_announce_history(self):
        self.assertEqual(alerts.pending_events(self.old, self.state), [])
        updated = copy.deepcopy(self.old)
        updated['records'].reverse()
        updated['records'][0]['title'] = 'Edited title'
        self.assertEqual(alerts.pending_events(updated, self.state), [])

    def test_new_open_entry_and_newly_accepted_solve(self):
        index = {'records': [record('old-solve', True), record('open-target', True), record('new-target')]}
        events = alerts.pending_events(index, self.state)
        self.assertEqual([(k, n, r['id']) for k, n, r in events],
                         [('solve', 2, 'open-target'), ('instance', 3, 'new-target')])
        message = alerts.payload(*events[0], self.site)
        self.assertIn('solver', message['embeds'][0]['fields'][0]['value'])
        self.assertIn('/pull/153', message['embeds'][0]['fields'][1]['value'])
        self.assertEqual(message['allowed_mentions'], {'parse': []})

    def test_new_entry_already_solved_gets_one_message(self):
        index = {'records': self.old['records'] + [record('new-target', True)]}
        self.assertEqual([k for k, _, _ in alerts.pending_events(index, self.state)], ['solve'])

    def test_unaccepted_proof_does_not_announce_solve(self):
        index = {'records': [record('old-solve', True), {**record('open-target'), 'status': 'solved'}]}
        self.assertEqual(alerts.pending_events(index, self.state), [])

    def test_successful_messages_are_saved_individually_and_retry_skips_them(self):
        index = {'records': [record('old-solve', True), record('open-target', True), record('new-target')]}
        saved = []
        delivered = []
        def deliver(message):
            if delivered:
                raise RuntimeError('Discord unavailable')
            delivered.append(message)
        with self.assertRaises(RuntimeError):
            alerts.announce(index, self.state, self.site, deliver, lambda state: saved.append(copy.deepcopy(state)))
        self.assertEqual(len(saved), 1)
        self.assertEqual([r['id'] for _, _, r in alerts.pending_events(index, saved[-1])], ['new-target'])
        alerts.announce(index, saved[-1], self.site, delivered.append, lambda state: None)
        self.assertEqual(alerts.pending_events(index, saved[-1]), [])
        # Removing and restoring old entries also cannot repeat an announcement.
        self.assertEqual(alerts.pending_events({'records': []}, saved[-1]), [])
        self.assertEqual(alerts.pending_events(index, saved[-1]), [])

    def test_invalid_state_fails_closed(self):
        for state in ({}, {'schemaVersion': 1, 'instances': [], 'solves': ['unknown']},
                      {'schemaVersion': 1, 'instances': ['../bad'], 'solves': []}):
            with self.assertRaises(ValueError):
                alerts.validate_state(state)

    def test_send_confirms_saved_message_and_suppresses_mentions(self):
        response = io.BytesIO(b'{"id":"123"}')
        with patch.object(alerts.urllib.request, 'urlopen', return_value=response) as call:
            alerts.send('https://discord.com/api/webhooks/123/private-token',
                        {'content': 'Example', 'allowed_mentions': {'parse': []}})
        request = call.call_args.args[0]
        self.assertTrue(request.full_url.endswith('?wait=true'))
        self.assertEqual(json.loads(request.data)['allowed_mentions'], {'parse': []})

    def test_rate_limit_retries_but_ambiguous_timeout_does_not(self):
        error = urllib.error.HTTPError('redacted', 429, 'limited', {}, io.BytesIO(b'{"retry_after":1}'))
        with patch.object(alerts.urllib.request, 'urlopen',
                          side_effect=[error, io.BytesIO(b'{"id":"123"}')]) as call, patch.object(alerts.time, 'sleep'):
            alerts.send('https://discord.com/api/webhooks/123/private-token', {'content': 'Example'})
            self.assertEqual(call.call_count, 2)
        with patch.object(alerts.urllib.request, 'urlopen', side_effect=TimeoutError()) as call:
            with self.assertRaisesRegex(RuntimeError, 'inspect the channel'):
                alerts.send('https://discord.com/api/webhooks/123/private-token', {'content': 'Example'})
            self.assertEqual(call.call_count, 1)

    def test_secret_is_not_in_error_message(self):
        with patch.object(alerts.urllib.request, 'urlopen',
                          side_effect=urllib.error.URLError('private-token')):
            try:
                alerts.send('https://discord.com/api/webhooks/123/private-token', {'content': 'Example'})
            except RuntimeError as error:
                self.assertNotIn('private-token', str(error))

    def test_aws_failure_cannot_reset_delivery_state(self):
        from types import SimpleNamespace
        for error in ('AccessDenied', 'ExpiredToken', 'network failure'):
            with patch.object(alerts.subprocess, 'run',
                              return_value=SimpleNamespace(returncode=1, stderr=error)):
                with self.assertRaises(RuntimeError):
                    alerts.s3_read('bucket', 'key', optional=True)
        with patch.object(alerts.subprocess, 'run',
                          return_value=SimpleNamespace(returncode=1, stderr='An error (NoSuchKey)')):
            self.assertIsNone(alerts.s3_read('bucket', 'key', optional=True))


if __name__ == '__main__':
    unittest.main()
