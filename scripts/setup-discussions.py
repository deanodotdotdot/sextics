#!/usr/bin/env python3
"""Prepare instance discussion posts locally; publish only with --apply after owner approval."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import time
import yaml

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = 'hodge-computer/sextics'


def plan():
    catalogue = json.loads((ROOT / 'data/catalogue.json').read_text())
    entries = []
    for instance_id in catalogue['instanceIds']:
        record = yaml.safe_load((ROOT / 'data' / instance_id / 'instance.rec').read_text())
        body = f'''<!-- hodge-instance:{instance_id} -->
A shared conversation about **{record['title']}** and its fixed target $(F,q,A)$.

[Explore this instance](https://hodge.computer/#case/{instance_id}) · [Exact statement](https://github.com/{REPOSITORY}/blob/main/data/{instance_id}/instance.rec) · [Mathematical context](https://github.com/{REPOSITORY}/blob/main/data/{instance_id}/why.md)

Questions, partial calculations, promising approaches, and independent checks are welcome. Explain what you tried, distinguish evidence from proof, and credit the human mathematical results and collaborators you use. If an AI agent posts on your behalf, identify its assistance in the comment.

This thread is shared with the website. To submit a proof for acceptance, follow the [contribution instructions](https://github.com/{REPOSITORY}/blob/main/CONTRIBUTING.md) and open a solution PR. A discussion comment does not replace a checked proof.
'''
        entries.append({'instanceId': instance_id, 'title': record['title'], 'body': body})
    return {'repository': REPOSITORY, 'category': 'General', 'threads': entries}


def gh(*args):
    result = subprocess.run(['gh', *args], text=True, capture_output=True, check=False)
    if result.returncode:
        raise SystemExit('GitHub request failed; batch stopped: ' + result.stderr.strip()[:400])
    response = json.loads(result.stdout) if result.stdout.strip() else {}
    if response.get('errors'):
        raise SystemExit('GitHub rejected the query; no further changes were attempted.')
    return response


def graphql(query, **variables):
    args = ['api', 'graphql', '-f', 'query=' + query]
    for key, value in variables.items():
        if value is not None:
            args += ['-f', key + '=' + str(value)]
    return gh(*args)['data']


def apply(prepared, enable=False):
    if prepared != plan():
        raise SystemExit('The prepared posts differ from the current catalogue. Regenerate and review the plan first.')
    if enable:
        gh('api', 'repos/' + REPOSITORY, '--method', 'PATCH', '-F', 'has_discussions=true')
    repo = graphql('''query { repository(owner:"hodge-computer",name:"sextics") {
      id hasDiscussionsEnabled discussionCategories(first:100) { nodes { id name } }
    } }''')['repository']
    if not repo['hasDiscussionsEnabled']:
        raise SystemExit('Discussions is disabled. Enabling it requires owner authorization and --enable.')
    category = next((c for c in repo['discussionCategories']['nodes'] if c['name'] == prepared['category']), None)
    if not category:
        raise SystemExit('Create the reviewed General category on GitHub, then rerun this command.')
    author = gh('api', 'user')['login']
    # Discover existing marker posts on every run, including after a partial failure.
    # This also recovers a successful creation whose response was lost.
    found = {}; cursor = None
    while True:
        page = graphql('''query($after:String){ repository(owner:"hodge-computer",name:"sextics") {
          discussions(first:100,after:$after) { nodes { id number title body author { login } } pageInfo { hasNextPage endCursor } }
        } }''', after=cursor)['repository']['discussions']
        for discussion in page['nodes']:
            for item in prepared['threads']:
                marker = '<!-- hodge-instance:' + item['instanceId'] + ' -->'
                if discussion['body'].startswith(marker):
                    if (discussion['body'] != item['body'] or discussion['title'] != item['title']
                            or (discussion.get('author') or {}).get('login') != author):
                        raise SystemExit('An existing marker has different content or authorship; inspect before continuing.')
                    if item['instanceId'] in found:
                        raise SystemExit('Duplicate instance discussion markers found; inspect before continuing.')
                    found[item['instanceId']] = {'number': discussion['number'], 'nodeId': discussion['id']}
        if not page['pageInfo']['hasNextPage']:
            break
        cursor = page['pageInfo']['endCursor']
    destination = ROOT / 'discussions/index.json'
    destination.parent.mkdir(exist_ok=True)
    def save():
        value = {'repository': REPOSITORY, 'instances': found}
        temporary = destination.with_suffix('.json.tmp')
        temporary.write_text(json.dumps(value, indent=2) + '\n')
        os.replace(temporary, destination)
    for item in prepared['threads']:
        if item['instanceId'] not in found:
            time.sleep(3)
            discussion = graphql('''mutation($repo:ID!,$category:ID!,$title:String!,$body:String!){
              createDiscussion(input:{repositoryId:$repo,categoryId:$category,title:$title,body:$body}) {
                discussion { id number }
              }
            }''', repo=repo['id'], category=category['id'], title=item['title'], body=item['body'])['createDiscussion']['discussion']
            found[item['instanceId']] = {'number': discussion['number'], 'nodeId': discussion['id']}
        save()
        print(item['instanceId'] + ': discussion #' + str(found[item['instanceId']]['number']), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, required=True, help='JSON file to write locally, or reviewed plan to apply')
    parser.add_argument('--apply', action='store_true', help='Create missing threads on GitHub; requires explicit owner permission')
    parser.add_argument('--enable', action='store_true', help='Also enable repository Discussions; requires explicit owner permission')
    args = parser.parse_args()
    if args.apply:
        apply(json.loads(args.plan.read_text()), args.enable)
    else:
        if args.enable:
            parser.error('--enable requires --apply')
        args.plan.write_text(json.dumps(plan(), indent=2, ensure_ascii=False) + '\n')
        print('Prepared ' + str(len(plan()['threads'])) + ' discussion posts locally. No GitHub requests were made: ' + str(args.plan))
