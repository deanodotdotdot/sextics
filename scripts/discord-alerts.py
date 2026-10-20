#!/usr/bin/env python3
"""Announce newly published atlas entries and accepted solves through Discord."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request

STATE_KEY = 'notifications/discord-state.json'
SITE = 'https://hodge.computer'
REPO = 'https://github.com/hodge-computer/sextics'


def snapshot(index):
    records = index['records']
    return {'schemaVersion': 1,
            'instances': sorted(r['id'] for r in records),
            'solves': sorted(r['id'] for r in records
                             if r['status'] == 'solved' and r['formalStatus'] == 'proved')}


def validate_state(state):
    if state.get('schemaVersion') != 1:
        raise ValueError('Unsupported Discord notification state')
    for key in ('instances', 'solves'):
        if not isinstance(state.get(key), list) or not all(
                isinstance(x, str) and re.fullmatch(r'[A-Za-z0-9-]+', x) for x in state[key]):
            raise ValueError('Invalid Discord notification state')
    if not set(state['solves']) <= set(state['instances']):
        raise ValueError('Notification state contains an unknown solve')
    return state


def pending_events(index, state):
    """Retain past IDs across reorders, edits, rollbacks, and repeated deployments."""
    current = snapshot(index)
    added = set(current['instances']) - set(state['instances'])
    solved = set(current['solves']) - set(state['solves'])
    events = []
    for number, record in enumerate(index['records'], 1):
        rid = record['id']
        # An entry introduced already solved gets one solve announcement.
        if rid in solved:
            events.append(('solve', number, record))
        elif rid in added:
            events.append(('instance', number, record))
    return events


def payload(kind, number, record, site):
    rid = record['id']
    title = record['title']
    embed = {'title': f'{"New solve" if kind == "solve" else "New atlas instance"} · {number:02d}',
             'description': title, 'url': f'{SITE}/#case/{rid}',
             'color': 0x6ECCA8 if kind == 'solve' else 0x9CBCE4}
    if kind == 'solve':
        full = json.loads((site / 'data' / rid / 'record.json').read_text())
        login = full['credit']['githubLogin']
        pr = full['pullRequest']
        if not re.fullmatch(r'[A-Za-z0-9-]+', login) or pr['url'] != f'{REPO}/pull/{int(pr["number"])}':
            raise ValueError('Invalid solve attribution or PR link')
        embed['fields'] = [
            {'name': 'Contributor', 'value': f'[`{login}`](https://github.com/{login})', 'inline': True},
            {'name': 'Accepted proof', 'value': f'[PR #{pr["number"]}]({pr["url"]})', 'inline': True}]
    else:
        embed['fields'] = [{'name': 'Open target', 'value': f'[Explore and discuss]({SITE}/#case/{rid}/discussion)'}]
    return {'embeds': [embed], 'allowed_mentions': {'parse': []}}


def s3_read(bucket, key, *, optional=False):
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / 'object.json'
        result = subprocess.run(['aws', 's3api', 'get-object', '--bucket', bucket,
                                 '--key', key, str(path)], capture_output=True, text=True)
        if result.returncode:
            if optional and '(NoSuchKey)' in result.stderr:
                return None
            raise RuntimeError(f'Could not read notification input s3://{bucket}/{key}')
        return json.loads(path.read_text())


def s3_write(bucket, state):
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / 'state.json'
        path.write_text(json.dumps(state, indent=2) + '\n')
        subprocess.run(['aws', 's3api', 'put-object', '--bucket', bucket, '--key', STATE_KEY,
                        '--body', str(path), '--server-side-encryption', 'AES256',
                        '--content-type', 'application/json', '--cache-control', 'no-store'],
                       check=True, stdout=subprocess.DEVNULL)


def send(webhook, message):
    url = urllib.parse.urlsplit(webhook)
    if (url.scheme != 'https' or url.netloc != 'discord.com' or
            not re.fullmatch(r'/api(?:/v\d+)?/webhooks/\d+/[A-Za-z0-9._-]+', url.path)):
        raise ValueError('Expected a Discord incoming webhook URL')
    # wait=true confirms Discord saved the message; never print the secret URL.
    endpoint = urllib.parse.urlunsplit((url.scheme, url.netloc, url.path, 'wait=true', ''))
    request = urllib.request.Request(endpoint, json.dumps(message).encode(),
                                     {'Content-Type': 'application/json',
                                      'User-Agent': 'hodge.computer solve announcements'})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                result = json.load(response)
            if not result.get('id'):
                raise RuntimeError('Discord did not confirm a saved message')
            return
        except urllib.error.HTTPError as error:
            if error.code == 429 and attempt < 3:
                delay = min(60, max(1, float(json.loads(error.read()).get('retry_after', 5))))
                time.sleep(delay)
                continue
            raise RuntimeError(f'Discord rejected the announcement (HTTP {error.code})') from None
        except (urllib.error.URLError, TimeoutError):
            # Delivery may already have occurred. Do not blindly duplicate it.
            raise RuntimeError('Discord delivery could not be confirmed; inspect the channel before retrying') from None


def wait_for_site(site):
    expected = json.loads((site / 'data/revision.json').read_text())
    for attempt in range(40):
        try:
            with urllib.request.urlopen(f'{SITE}/data/revision.json?announcement={time.time_ns()}',
                                        timeout=10) as response:
                if json.load(response) == expected:
                    return
        except (OSError, ValueError):
            pass
        time.sleep(3)
    raise RuntimeError('The deployed revision is not visible yet; retry deployment to send pending alerts')


def announce(index, state, site, deliver, save):
    for kind, number, record in pending_events(index, state):
        deliver(payload(kind, number, record, site))
        rid = record['id']
        state['instances'] = sorted(set(state['instances']) | {rid})
        if kind == 'solve':
            state['solves'] = sorted(set(state['solves']) | {rid})
        save(state)
        print(f'Announced {kind}: {rid}', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=('prepare', 'send'))
    parser.add_argument('--bucket', required=True)
    parser.add_argument('--site', type=Path, required=True)
    args = parser.parse_args()
    webhook = os.environ.get('DISCORD_SOLVE_WEBHOOK_URL', '')
    if not webhook:
        print('Discord notifications are disabled: repository secret is not configured.')
        return
    state = s3_read(args.bucket, STATE_KEY, optional=True)
    if args.phase == 'prepare':
        if state is None:
            # First activation starts from what is already live, before upload.
            # Persist it now so a failed first send can be retried safely.
            state = snapshot(s3_read(args.bucket, 'data/index.json'))
            s3_write(args.bucket, validate_state(state))
            print('Initialized notifications from the existing published atlas.')
        else:
            validate_state(state)
        return
    if state is None:
        raise RuntimeError('Notification baseline was not prepared before deployment')
    validate_state(state)
    index = json.loads((args.site / 'data/index.json').read_text())
    if pending_events(index, state):
        wait_for_site(args.site)
        announce(index, state, args.site, lambda message: send(webhook, message),
                 lambda value: s3_write(args.bucket, value))
    else:
        print('No new atlas entries or accepted solves to announce.')


if __name__ == '__main__':
    main()
