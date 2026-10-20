#!/usr/bin/env python3
"""Report readiness for owner merge; require explicit authorization for maintenance."""
import argparse
import json
import os
from pathlib import Path
from acceptance import require


def latest_owner_review(reviews, owner):
    relevant = [r for r in reviews if r['user']['login'].lower() == owner.lower() and
                r['state'] in ('APPROVED','CHANGES_REQUESTED','DISMISSED')]
    return max(relevant, key=lambda r:r['id'], default=None)


def approved(reviews, owner, head):
    latest = latest_owner_review(reviews, owner)
    return bool(latest and latest['state']=='APPROVED' and latest['commit_id']==head)


def dispatched_approval(event, actor, triggering_actor, approved_head, owner, head):
    return (event == 'workflow_dispatch' and actor.lower() == owner.lower() and
            triggering_actor.lower() == owner.lower() and approved_head == head)


def requires_owner_review(mode, *, maintenance):
    require(mode in ('preview', 'live'), 'Invalid mode')
    return maintenance


def summarize(message):
    print(message)
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as stream:
            stream.write(message+'\n')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--reviews',type=Path,required=True); p.add_argument('--head',required=True)
    p.add_argument('--event',default=''); p.add_argument('--actor',default='')
    p.add_argument('--triggering-actor',default=''); p.add_argument('--approved-head',default='')
    p.add_argument('--maintenance',action='store_true',help='Require owner authorization even in preview mode')
    p.add_argument('--report',type=Path,help='Report a completed proof check awaiting owner merge')
    args=p.parse_args()
    require(not (args.maintenance and args.report), 'Maintenance cannot use a solve report')
    policy=json.loads((Path(__file__).resolve().parents[2]/'.github/solve-policy.json').read_text())
    pages=json.loads(args.reviews.read_text())
    reviews=[r for page in pages for r in page]
    signed=dispatched_approval(args.event,args.actor,args.triggering_actor,args.approved_head,policy['owner'],args.head)
    if args.report:
        report=json.loads(args.report.read_text())
        require(report['schemaVersion']==2 and report['headCommit']==args.head and
                report['result']=='lean-checked-awaiting-owner' and report['kernelReplay'] is True,
                'The report must contain a completed proof check for this head')
        # Keep the report schema stable. Publication authenticates the owner's
        # merge through GitHub; a separate approving review is not required.
        report['ownerAuthorization']=None
        args.report.write_text(json.dumps(report,indent=2)+'\n')
        if policy['mode']=='preview':
            summarize('**Lean verification passed (preview only).** This run cannot publish an accepted solve.')
        else:
            summarize('**Lean verification passed. Ready for owner merge.** Merge this exact head with a merge commit while main is unchanged. The owner merge is the sign-off; no separate approving review or second Lean run is required.')
        return
    if not requires_owner_review(policy['mode'],maintenance=args.maintenance):
        summarize('Preview: checks are diagnostic; the owner makes the final merge decision.')
        return
    require(approved(reviews,policy['owner'],args.head) or signed,
            'The owner must authorize this exact commit by approving review or explicit workflow sign-off. New commits invalidate approval.')
    summarize('Owner approved this exact commit. Merge remains a manual owner action.')

if __name__=='__main__':main()
