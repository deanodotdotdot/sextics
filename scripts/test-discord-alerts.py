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

    def test_complete_atlas_is_a_valid_initial_baseline(self):
        index = json.loads((Path(__file__).resolve().parents[1] / 'data/index.json').read_text())
        state = alerts.validate_state(alerts.snapshot(index))
        self.assertEqual(len(state['instances']), len(index['records']))
        self.assertIn('ytype-companion-fiberA-d4-strict-rational', state['instances'])
        self.assertEqual(alerts.pending_events(index, state), [])

    def test_new_open_entry_and_newly_accepted_solve(self):
        index = {'records': [record('old-solve', True), record('open-target', True), record('new-target')]}
        events = alerts.pending_events(index, self.state)
        self.assertEqual([(k, n, r['id']) for k, n, r in events],
                         [('solve', 2, 'open-target'), ('instance', 3, 'new-target')])
        message = alerts.payload(*events[0], self.site)
        self.assertIn('solver', message['embeds'][0]['fields'][0]['value'])
        self.assertIn('/pull/153', message['embeds'][0]['fields'][1]['value'])
        self.assertEqual(message['allowed_mentions'], {'parse': []})
        self.assertNotIn('username', message)
        self.assertNotIn('avatar_url', message)

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
            message_id = alerts.send('https://discord.com/api/webhooks/123/private-token',
                                     {'content': 'Example', 'allowed_mentions': {'parse': []}})
        self.assertEqual(message_id, '123')
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


class DiscussionAlerts(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.site = Path(self.tmp.name)
        (self.site / 'discussions').mkdir()
        (self.site / 'data').mkdir()
        (self.site / 'discussions/index.json').write_text(json.dumps({
            'repository': 'hodge-computer/sextics',
            'instances': {'holdout': {'number': 44}}}))
        (self.site / 'data/index.json').write_text(json.dumps({
            'records': [record('fermat', True), record('holdout')]}))
        self.event = {
            'action': 'created', 'repository': {'full_name': 'hodge-computer/sextics'},
            'discussion': {'number': 44, 'title': 'An old title'},
            'comment': {'id': 19002099, 'parent_id': None,
                        'html_url': alerts.REPO + '/discussions/44#discussioncomment-19002099',
                        'user': {'login': 'fqlx'},
                        'body': '@everyone `$(cat /secret)` <script>bad()</script>'}}

    def test_new_comment_links_to_website_and_uses_current_atlas_title(self):
        comment_id, message = alerts.discussion_payload(self.event, self.site)
        self.assertEqual(comment_id, 19002099)
        embed = message['embeds'][0]
        self.assertEqual(embed['title'], 'New discussion comment · 02')
        self.assertEqual(embed['description'], 'Holdout')
        self.assertEqual(embed['url'], alerts.SITE + '/#case/holdout/discussion/19002099')
        self.assertEqual(embed['fields'][0]['value'], '`fqlx`')
        self.assertIn('/discussion/19002099', embed['fields'][1]['value'])
        self.assertNotIn('username', message)
        self.assertNotIn('avatar_url', message)
        self.assertEqual(message['allowed_mentions'], {'parse': []})
        self.assertNotIn('secret', json.dumps(message))
        self.assertNotIn('@everyone', json.dumps(message))

    def test_reply_links_to_reply_itself(self):
        self.event['comment']['parent_id'] = 12345
        _, message = alerts.discussion_payload(self.event, self.site)
        self.assertTrue(message['embeds'][0]['url'].endswith('/19002099'))

    def test_edits_deletions_and_other_actions_are_ignored(self):
        for action in ('edited', 'deleted', None):
            self.event['action'] = action
            with self.subTest(action=action):
                self.assertIsNone(alerts.discussion_payload(self.event, self.site))

    def test_non_atlas_discussion_uses_github_and_escapes_title(self):
        self.event['discussion'].update(number=200, title='[link](https://example.com) *bold*')
        self.event['comment']['html_url'] = alerts.REPO + '/discussions/200#discussioncomment-19002099'
        _, message = alerts.discussion_payload(self.event, self.site)
        embed = message['embeds'][0]
        self.assertEqual(embed['title'], 'New discussion comment')
        self.assertEqual(embed['url'], self.event['comment']['html_url'])
        self.assertEqual(embed['description'], r'\[link\]\(https://example.com\) \*bold\*')

    def test_unexpected_repository_ids_urls_and_author_are_rejected(self):
        bad = []
        event = copy.deepcopy(self.event)
        event['repository']['full_name'] = 'someone/else'
        bad.append(event)
        for field, value in [('id', '../unsafe'), ('id', True), ('id', -2),
                             ('html_url', 'https://example.com/'),
                             ('user', {'login': '`unsafe`'})]:
            event = copy.deepcopy(self.event)
            event['comment'][field] = value
            bad.append(event)
        for event in bad:
            with self.subTest(event=event):
                with self.assertRaises(ValueError):
                    alerts.discussion_payload(event, self.site)

    def test_successful_delivery_saves_message_id_and_reruns_do_not_repeat(self):
        stored, delivered = {}, []
        def deliver(message):
            delivered.append(message)
            return '999999'
        for _ in range(2):
            alerts.announce_discussion(self.event, self.site, deliver, stored.get,
                                       lambda key, value: stored.__setitem__(key, value))
        self.assertEqual(len(delivered), 1)
        self.assertEqual(stored, {'notifications/discussion-comments/19002099.json': {
            'schemaVersion': 1, 'commentId': 19002099, 'discordMessageId': '999999'}})
        # An independently arriving reply has its own marker, not a shared history.
        reply = copy.deepcopy(self.event)
        reply['comment'].update(id=19002100, parent_id=19002099,
                                html_url=alerts.REPO + '/discussions/44#discussioncomment-19002100')
        alerts.announce_discussion(reply, self.site, deliver, stored.get,
                                   lambda key, value: stored.__setitem__(key, value))
        self.assertEqual(len(delivered), 2)
        self.assertEqual(len(stored), 2)

    def test_failure_does_not_mark_comment_sent(self):
        def fail(_):
            raise RuntimeError('Delivery uncertain')
        saved = []
        with self.assertRaisesRegex(RuntimeError, 'uncertain'):
            alerts.announce_discussion(self.event, self.site, fail, lambda _: None,
                                       lambda key, value: saved.append(value))
        self.assertEqual(saved, [])

    def test_corrupt_delivery_state_fails_closed(self):
        with self.assertRaisesRegex(ValueError, 'notification state'):
            alerts.announce_discussion(self.event, self.site, lambda _: self.fail('must not send'),
                                       lambda _: {}, lambda key, value: self.fail('must not save'))


if __name__ == '__main__':
    unittest.main()
