#!/usr/bin/env python3
"""Build the public comment leaderboard from mapped atlas discussions."""
import concurrent.futures
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def connection(node, kind):
    cursor = None
    while True:
        after = ',after:' + json.dumps(cursor) if cursor else ''
        typename = 'Discussion' if kind == 'comments' else 'DiscussionComment'
        query = ('query { node(id:' + json.dumps(node) + ') { ... on ' + typename
                 + ' { ' + kind + '(first:100' + after + ') { nodes {'
                 ' id url body createdAt isMinimized author { login } }'
                 ' pageInfo { hasNextPage endCursor } } } } }')
        result = json.loads(subprocess.check_output(['gh', 'api', 'graphql', '-f', 'query=' + query]))
        if result.get('errors'):
            raise RuntimeError(result['errors'])
        page = result['data']['node'][kind]
        yield from page['nodes']
        if not page['pageInfo']['hasNextPage']:
            return
        cursor = page['pageInfo']['endCursor']


def collect(entry):
    instance, thread = entry
    posts = []
    for parent in connection(thread['nodeId'], 'comments'):
        for comment in [parent, *connection(parent['id'], 'replies')]:
            if not comment['author']:
                continue
            posts.append(dict(githubLogin=comment['author']['login'], instanceId=instance,
                              number=comment['url'].split('discussioncomment-')[-1],
                              createdAt=comment['createdAt'],
                              body='This comment was hidden by a GitHub moderator.' if comment['isMinimized'] else comment['body'],
                              isReply=comment['id'] != parent['id']))
    return posts


def rank(posts):
    authors = {}
    for post in posts:
        authors.setdefault(post['githubLogin'], []).append(post)
    rows = [dict(githubLogin=login, score=len(comments),
                 reachedCountAt=max(c['createdAt'] for c in comments),
                 comments=sorted(comments, key=lambda c: c['createdAt'], reverse=True))
            for login, comments in authors.items()]
    rows.sort(key=lambda r: (-r['score'], r['reachedCountAt'], r['githubLogin'].lower()))
    for i, row in enumerate(rows):
        row['rank'] = i + 1
    return rows


if __name__ == '__main__':
    entries = json.loads((ROOT / 'discussions/index.json').read_text())['instances'].items()
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        posts = [post for batch in pool.map(collect, entries) for post in batch]
    output = ROOT / 'leaderboard/comment-counts.json'
    temporary = output.with_suffix('.tmp')
    temporary.write_text(json.dumps({'rows': rank(posts)}, indent=2) + '\n')
    temporary.replace(output)
    print(f'Indexed {len(posts)} comments and replies.')
