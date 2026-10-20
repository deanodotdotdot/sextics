#!/usr/bin/env python3
import unittest
import copy
import json
import io
import os
from pathlib import Path
import subprocess
import tempfile
import sys
from unittest.mock import patch
import yaml
from check import ROOT, read_proposal
from check import module_order, polynomial, strip_comments, target_source
from review import approved, dispatched_approval, requires_owner_review
import publish
from acceptance import sha256

class WorkflowCommitBinding(unittest.TestCase):
    def run_step(self, name, *, main='b'*40, head='c'*40, workflow='b'*40):
        steps=yaml.safe_load((ROOT/'.github/workflows/solve-proposal.yml').read_text())['jobs']['verify']['steps']
        shell=next(step['run'] for step in steps if step.get('name')==name)
        self.assertIn('gh api "repos/$REPO/git/ref/heads/main"',shell)
        code=shell.split("python3 - <<'PYCODE'\n",1)[1].split('\nPYCODE',1)[0]
        # Reproduce GitHub retaining the creation-time PR base after main advances.
        pr={'state':'open','number':2,'user':{'login':'benediamond'},
            'base':{'sha':'a'*40,'ref':'main','repo':{'full_name':'hodge-computer/sextics'}},
            'head':{'sha':head}}
        branch={'ref':'refs/heads/main','object':{'type':'commit','sha':main}}
        output=io.StringIO()
        class Output:
            def __enter__(self):return output
            def __exit__(self,*args):pass
        def fixture_open(path,*args):
            if path=='fixture-output':return Output()
            return io.StringIO(json.dumps(branch if path.endswith('-main.json') else pr))
        env={'REPO':'hodge-computer/sextics','GITHUB_SHA':workflow,
             'GITHUB_OUTPUT':'fixture-output','BASE':'b'*40,'HEAD':'c'*40}
        with patch.dict(os.environ,env),patch('builtins.open',fixture_open):
            exec(compile(code,'workflow-inline','exec'),{})
        return output.getvalue()

    def test_current_main_overrides_creation_time_pr_base(self):
        self.assertIn('base='+'b'*40,self.run_step('Resolve current immutable PR commits'))

    def test_stale_workflow_revision_is_rejected(self):
        with self.assertRaisesRegex(AssertionError,'Main advanced'):
            self.run_step('Resolve current immutable PR commits',workflow='a'*40)

    def test_unchanged_live_main_and_head_pass(self):
        self.run_step('Reject a result for a superseded PR or base')

    def test_main_advancing_during_check_is_rejected(self):
        with self.assertRaisesRegex(AssertionError,'Main changed'):
            self.run_step('Reject a result for a superseded PR or base',main='d'*40)

    def test_pr_head_changing_during_check_is_rejected(self):
        with self.assertRaisesRegex(AssertionError,'PR changed'):
            self.run_step('Reject a result for a superseded PR or base',head='d'*40)

class ProposalChecks(unittest.TestCase):
    def test_solve_cli_keeps_pending_review_separate_from_proof_result(self):
        owner=json.loads((ROOT/'.github/solve-policy.json').read_text())['owner']
        head='a'*40
        with tempfile.TemporaryDirectory() as tmp:
            reviews=Path(tmp)/'reviews.json'; reviews.write_text('[[]]')
            report=Path(tmp)/'report.json'
            checked={'schemaVersion':2,'headCommit':head,'kernelReplay':True,
                     'result':'lean-checked-awaiting-owner'}
            report.write_text(json.dumps(checked))
            command=[sys.executable,str(ROOT/'scripts/proposals/review.py'),
                     '--reviews',str(reviews),'--head',head,'--report',str(report)]
            result=subprocess.run(command,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertIn('Lean verification passed. Ready for owner merge',result.stdout)
            self.assertIsNone(json.loads(report.read_text())['ownerAuthorization'])
            result=subprocess.run(command+['--event','workflow_dispatch','--actor',owner,
                '--triggering-actor',owner,'--approved-head',head],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertIsNone(json.loads(report.read_text())['ownerAuthorization'])
            # A sign-off cannot be attached to an incomplete or different check.
            for mutation in ({'result':'structure-only'},{'headCommit':'b'*40},{'kernelReplay':False}):
                report.write_text(json.dumps({**checked,**mutation}))
                with self.subTest(mutation=mutation):
                    self.assertNotEqual(subprocess.run(command,capture_output=True).returncode,0)

    def test_maintenance_cli_rejects_missing_and_stale_approval(self):
        owner=json.loads((ROOT/'.github/solve-policy.json').read_text())['owner']
        head='a'*40
        with tempfile.TemporaryDirectory() as tmp:
            reviews=Path(tmp)/'reviews.json'
            command=[sys.executable,str(ROOT/'scripts/proposals/review.py'),
                     '--reviews',str(reviews),'--head',head,'--maintenance']
            reviews.write_text('[[]]')
            result=subprocess.run(command,capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)
            self.assertIn('owner must authorize',result.stderr)
            review={'id':1,'user':{'login':owner},'state':'APPROVED','commit_id':head}
            reviews.write_text(json.dumps([[review]]))
            self.assertEqual(subprocess.run(command,capture_output=True).returncode,0)
            review['commit_id']='b'*40
            reviews.write_text(json.dumps([[review]]))
            self.assertNotEqual(subprocess.run(command,capture_output=True).returncode,0)

    def test_maintenance_cannot_bypass_owner_review_in_preview(self):
        self.assertTrue(requires_owner_review('preview',maintenance=True))
        self.assertTrue(requires_owner_review('live',maintenance=True))
        self.assertFalse(requires_owner_review('live',maintenance=False))
        self.assertFalse(requires_owner_review('preview',maintenance=False))
        with self.assertRaises(ValueError): requires_owner_review('disabled',maintenance=False)

    def test_explicit_owner_dispatch(self):
        args=['workflow_dispatch','benediamond','benediamond','a'*40,'benediamond','a'*40]
        self.assertTrue(dispatched_approval(*args))
        for index,value in ((0,'pull_request_target'),(1,'stranger'),(2,'stranger'),(3,'b'*40)):
            bad=args.copy();bad[index]=value
            with self.subTest(index=index):self.assertFalse(dispatched_approval(*bad))

    def test_exact_polynomial_translation(self):
        self.assertIn('(1 / 87 : ℂ)',polynomial('610 * X0 * Y0**5 * Y2**6 / 87'))
        for expression in ('__import__("os").system("true")','X6','X0**-1','X0 / Y0','1.2*X0'):
            with self.subTest(expression=expression),self.assertRaises(ValueError): polynomial(expression)

    def test_nested_comments_do_not_hide_code(self):
        code=strip_comments('/- outer /- inner -/ done -/\naxiom bad : False')
        self.assertIn('axiom bad',code)
        self.assertNotIn('inner',code)
        with self.assertRaises(ValueError): strip_comments('/- not closed')

    def test_import_graph_and_executable_rejection(self):
        files={'Solution.lean':b'import Proposal.Helper\nimport HodgeTarget\ntheorem result : True := by trivial',
               'Helper.lean':b'import Mathlib.Tactic\n-- sorry in a comment is harmless'}
        self.assertEqual(module_order(files)[0],['Helper.lean','Solution.lean'])
        for code in (b'import Proposal.Missing',b'import Lake',b'axiom bad : False',b'#eval IO.println "fake pass"',b'run_cmd pure ()',b'theorem bad : False := by sorry'):
            with self.subTest(code=code),self.assertRaises(ValueError): module_order({'Solution.lean':code})

    def test_owner_approval_is_bound_to_the_exact_head(self):
        head='a'*40
        approved_review={'id':1,'user':{'login':'benediamond'},'state':'APPROVED','commit_id':head}
        self.assertTrue(approved([approved_review],'benediamond',head))
        self.assertFalse(approved([approved_review],'benediamond','b'*40))
        self.assertFalse(approved([approved_review],'other-user',head))
        dismissed={**approved_review,'id':2,'state':'DISMISSED'}
        self.assertFalse(approved([approved_review,dismissed],'benediamond',head))
        changes={**approved_review,'id':3,'state':'CHANGES_REQUESTED'}
        self.assertFalse(approved([approved_review,changes],'benediamond',head))


class PublicationAuthorization(unittest.TestCase):
    def setUp(self):
        self.head='a'*40; self.base='b'*40
        self.policy={'owner':'benediamond'}
        self.pr={'merged':True,'number':122,'head':{'sha':self.head},'merge_commit_sha':'d'*40,
                 'user':{'login':'contributor'},'merged_by':{'login':'benediamond'},
                 'base':{'ref':'main','repo':{'full_name':'hodge-computer/sextics'}}}
        self.report={'schemaVersion':2,'baseCommit':self.base,'headCommit':self.head,
                     'pullRequest':122,'githubLogin':'contributor','mode':'live',
                     'kernelReplay':True,'result':'lean-checked-awaiting-owner',
                     'verifierSha256':{path:sha256(b'trusted fixture') for path in
                       ('.github/workflows/solve-proposal.yml','scripts/proposals/review.py')}}
        self.run={'id':123,'event':'pull_request_target','head_sha':self.head,
                  'path':'.github/workflows/solve-proposal.yml','conclusion':'success',
                  'actor':{'login':'contributor'},'triggering_actor':{'login':'contributor'}}
        self.merge={'parents':[{'sha':self.base},{'sha':self.head}]}
        self.review={'id':1,'user':{'login':'benediamond'},'commit_id':self.head,'state':'APPROVED'}

    def validate(self):
        with patch.object(publish,'git',return_value=b'trusted fixture'):
            publish.validate_report(self.report,self.pr,self.run,self.merge,self.policy)


    def test_automatic_and_manual_run_commit_associations(self):
        self.validate()
        self.run.update(event='workflow_dispatch',head_sha=self.base)
        self.validate()
        self.run['head_sha']=self.head
        with self.assertRaisesRegex(ValueError,'protected base workflow'):self.validate()

    def test_failed_untrusted_stale_or_changed_runs_are_rejected(self):
        for field,value in (('conclusion','failure'),('event','pull_request'),
                            ('path','untrusted.yml'),('head_sha','c'*40)):
            original=copy.deepcopy(self.run)
            self.run[field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):self.validate()
            self.run=original
        self.merge['parents'][0]['sha']='d'*40
        with self.assertRaisesRegex(ValueError,'checked base and head'):self.validate()

    def test_old_reports_remain_valid_and_new_reports_bind_signoff_code(self):
        self.report['schemaVersion']=1
        del self.report['verifierSha256']['scripts/proposals/review.py']
        self.validate()
        self.report['schemaVersion']=2
        with self.assertRaisesRegex(ValueError,'sign-off source binding'):self.validate()
        self.report['schemaVersion']=3
        with self.assertRaisesRegex(ValueError,'report version'):self.validate()

    def test_owner_merge_authorizes_contributor_and_owner_authored_prs(self):
        for author in ('contributor','benediamond'):
            self.pr['user']['login']=author
            self.report['githubLogin']=author
            self.validate()
            authorization=publish.merge_authorization(self.pr,self.policy)
            self.assertEqual(authorization,{'method':'owner_merge','githubLogin':'benediamond',
                'headCommit':self.head,'mergeCommit':'d'*40})
            self.assertEqual(self.report['githubLogin'],author)

    def test_unmerged_or_nonowner_merges_are_rejected(self):
        for update in ({'merged':False},{'merged_by':{'login':'stranger'}}):
            previous=copy.deepcopy(self.pr)
            self.pr.update(update)
            with self.subTest(update=update),self.assertRaises(ValueError):self.validate()
            with self.subTest(update=update),self.assertRaises(ValueError):
                publish.merge_authorization(self.pr,self.policy)
            self.pr=previous


class ProposalBoundary(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='hodge-proposal-fixture-')
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.git('init','-q')
        self.write('data/example/instance.rec','id: example\nq: 1\nF: X0**6\nA: X0**5*Y0\n')
        self.write('protected.txt','protected')
        self.base=self.commit()
        self.write('data/example/proof.json',json.dumps({'schemaVersion':2,'instanceId':'example','theorem':'Submission.certificate'}))
        self.write('data/example/solution.md','An explanation.')
        self.write('data/example/Solution.lean','import HodgeTarget\n')
        self.policy={'maxFiles':64,'maxBytes':16777216}

    def git(self,*args):
        return subprocess.check_output(['git',*args],cwd=self.root,stderr=subprocess.DEVNULL).decode().strip()

    def write(self,name,text):
        p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)

    def commit(self):
        self.git('add','-A')
        self.git('-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm','Fixture')
        return self.git('rev-parse','HEAD')

    def check(self):
        head=self.commit()
        with patch('check.ROOT',self.root):return read_proposal(self.base,head,'new-contributor',self.policy)

    def test_one_valid_proposal(self):
        self.assertEqual(self.check()[0],'example')

    def test_existing_mixed_case_instance_id(self):
        rid='example-fiberA'
        (self.root/'data/example').rename(self.root/'data'/rid)
        self.write(f'data/{rid}/instance.rec',f'id: {rid}\nq: 1\nF: X0**6\nA: X0**5*Y0\n')
        for name in ('proof.json','solution.md','Solution.lean'):
            (self.root/'data'/rid/name).unlink()
        self.base=self.commit()
        self.write(f'data/{rid}/proof.json',json.dumps({'schemaVersion':2,'instanceId':rid,'theorem':'Submission.certificate'}))
        self.write(f'data/{rid}/solution.md','An explanation.')
        self.write(f'data/{rid}/Solution.lean','import HodgeTarget\n')
        self.assertEqual(self.check()[0],rid)

    def test_reject_protected_change(self):
        self.write('protected.txt','changed')
        with self.assertRaisesRegex(ValueError,'only (?:edit|add)'):self.check()

    def test_reject_atlas_leaderboard_and_verifier_edits(self):
        for name in ('data/example/instance.rec','leaderboard/accounts.json',
                     'scripts/proposals/check.py','.github/solve-policy.json'):
            with self.subTest(path=name):
                original=(self.root/name).read_bytes() if (self.root/name).exists() else None
                self.write(name,'unauthorized change')
                with self.assertRaisesRegex(ValueError,'only (?:edit|add)'):self.check()
                if original is None: (self.root/name).unlink()
                else: (self.root/name).write_bytes(original)

    def test_reject_symlink(self):
        (self.root/'data/example/Helper.lean').symlink_to('/etc/passwd')
        with self.assertRaisesRegex(ValueError,'Symlinks'):self.check()

    def test_reject_claimed_identity(self):
        self.write('data/example/proof.json',json.dumps({'schemaVersion':2,'instanceId':'example','theorem':'Submission.certificate','githubLogin':'benediamond'}))
        with self.assertRaisesRegex(ValueError,'attribution comes from GitHub'):self.check()

    def test_reject_oversized_blob_before_read(self):
        self.policy['maxBytes']=1
        with self.assertRaisesRegex(ValueError,'too large'):self.check()

if __name__=='__main__':unittest.main()
