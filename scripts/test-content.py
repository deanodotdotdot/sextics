#!/usr/bin/env python3
"""Test the content/acceptance boundary in disposable consistency fixtures.

Synthetic receipts below are not proof evidence and never enter the atlas.
The protected Lean runner and GitHub publisher are tested separately.
"""
import copy
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch
import zipfile

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts/proposals'))
from acceptance import accepted_sources, solution_record, statement_hash
from content import render
import publish as publisher

RID = 'test-example'

class ContentUpdates(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='hodge-content-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        instance = {'id':RID, 'title':'Consistency fixture', 'q':1,
                    'F':'X0**6', 'A':'X0**5*Y0', 'formalStatus':'unproved',
                    'visibility':'visible', 'category':'fixture', 'rationale':'why.md',
                    'render':{}, 'polynomialData':{'F':{}, 'A':{}}}
        self.write(f'data/{RID}/instance.rec', yaml.safe_dump(instance))
        self.write(f'data/{RID}/why.md', 'A prospective reason.')
        self.write('data/catalogue.json', json.dumps({'schemaVersion':2,'instanceIds':[RID]}))
        self.write('docs/index.json', json.dumps({'schemaVersion':1,'pages':[],
            'overview':{'source':'docs/overview.md','content':'docs/overview.html'}}))
        self.write('docs/overview.md', r'An overview with \(F^{q+1}\).')
        self.write('index.html', '<main></main>')
        self.write('assets/renderer.js', '// Renderer fixture')
        self.write('slices/home.json', json.dumps({'pairId': 'example', 'seed': 1, 'mesh': 'meshes/example.json', 'camera': {}}))
        self.run_build()

    def write(self, relative, text):
        path = self.root/relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def read(self, relative):
        return json.loads((self.root/relative).read_text())

    def run_build(self, success=True, check=False):
        result = subprocess.run([sys.executable,str(ROOT/'scripts/build-content.py'),'--root',str(self.root),
                                 *(['--check'] if check else [])], capture_output=True,text=True)
        self.assertEqual(result.returncode==0,success,result.stdout+result.stderr)
        return result

    def receipt_fixture(self, login='new-contributor'):
        folder=self.root/'data'/RID
        self.write(f'data/{RID}/proof.json',json.dumps({'schemaVersion':2,'instanceId':RID,
                   'theorem':'Submission.certificate','witnessTheorem':'Submission.witness'}))
        self.write(f'data/{RID}/Solution.lean','-- Content-binding fixture only, not a Lean proof.\n')
        self.write(f'data/{RID}/witness.json',json.dumps({'d':0,'D':'1/4','N':['0']*6,'Q':'0'}))
        self.write(f'data/{RID}/solution.md',r'An explanation with \(D=\frac14\).')
        instance=yaml.safe_load((folder/'instance.rec').read_text())
        pr={'number':123,'url':'https://github.com/hodge-computer/sextics/pull/123',
            'baseCommit':'a'*40,'headCommit':'b'*40,'mergeCommit':'c'*40}
        proof={'mode':'live','instanceId':RID,'kernelReplay':True,'result':'lean-checked-awaiting-owner',
               'axioms':['propext','Classical.choice','Quot.sound'],'verifierSha256':{'fixture':'d'*64},
               'sandbox':'docker-no-network','baseCommit':pr['baseCommit'],'headCommit':pr['headCommit'],
               'pullRequest':123,'githubLogin':login,'statementSha256':statement_hash(instance),
               'sourceHashes':accepted_sources(folder),'theorem':'Submission.certificate',
               'witnessChecked':True,'leanVersion':'consistency fixture'}
        receipt={'schemaVersion':1,'formalAcceptance':True,'repository':'hodge-computer/sextics',
                 'instanceId':RID,'verification':proof,'pullRequest':pr,'githubLogin':login,
                 'submittedAt':'2026-10-15T00:00:00Z','acceptedAt':'2026-10-15T00:01:00Z',
                 'run':{'workflowPath':'.github/workflows/solve-proposal.yml','id':123,'conclusion':'success'}}
        self.write(f'data/{RID}/acceptance.json',json.dumps(receipt))
        self.write(f'data/{RID}/solution.rec',yaml.safe_dump(solution_record(self.root,receipt)))
        return receipt

    def test_proof_files_alone_do_not_publish(self):
        self.receipt_fixture()
        (self.root/'data'/RID/'solution.rec').unlink()
        (self.root/'data'/RID/'acceptance.json').unlink()
        self.run_build()
        self.assertEqual(self.read(f'data/{RID}/record.json')['status'],'open')
        self.assertEqual(self.read('leaderboard/credits.json')['credits'],[])
        self.assertFalse((self.root/'data'/RID/'solution.html').exists())

    def test_acceptance_drives_all_exports_and_removal_clears_them(self):
        self.receipt_fixture()
        self.run_build()
        record=self.read(f'data/{RID}/record.json')
        self.assertEqual((record['status'],record['formalStatus']),('solved','proved'))
        self.assertEqual(record['render']['divisorTerms'],[[.25,[0]*6]])
        self.assertEqual(record['pullRequest']['number'],123)
        self.assertEqual(record['credit']['githubLogin'],'new-contributor')
        self.assertEqual(self.read('leaderboard/credits.json')['credits'][0]['githubLogin'],'new-contributor')
        path=self.root/'data'/RID/'solution.rec'; original=path.read_text()
        path.unlink()
        self.run_build(success=False,check=True)
        self.run_build()
        record=self.read(f'data/{RID}/record.json')
        self.assertEqual(record['status'],'open')
        self.assertNotIn('D',record)
        self.assertNotIn('divisorTerms',record['render'])
        self.assertEqual(self.read('leaderboard/credits.json')['credits'],[])
        for name in ('solution.json','solution.html'):
            self.assertFalse((path.parent/name).exists())
        path.write_text(original)
        self.run_build()
        self.run_build(check=True)

    def test_changed_binding_is_rejected_without_publishing_partial_output(self):
        self.receipt_fixture(); self.run_build()
        protected=self.root/'data'/RID
        mutations={'Solution.lean':'-- altered proof', 'proof.json':'{}',
                   'witness.json':'{}', 'instance.rec':(protected/'instance.rec').read_text().replace('q: 1','q: 2')}
        before={p:p.read_bytes() for p in self.root.rglob('*') if p.suffix in ('.json','.html') and p.name!='witness.json'}
        for name,content in mutations.items():
            with self.subTest(file=name):
                path=protected/name; original=path.read_bytes(); path.write_text(content)
                self.assertIn('has changed',self.run_build(success=False).stderr)
                path.write_bytes(original)
                self.assertEqual(before,{p:p.read_bytes() for p in before})

    def test_explanation_edits_preserve_acceptance_and_update_the_site(self):
        self.receipt_fixture(); self.run_build()
        folder=self.root/'data'/RID
        receipt=(folder/'acceptance.json').read_bytes()
        credits=self.read('leaderboard/credits.json')
        record=self.read(f'data/{RID}/record.json')
        revision=self.read('data/revision.json')
        self.write(f'data/{RID}/solution.md', r'Corrected explanation with \(D=\frac14\).')
        self.run_build()
        self.assertIn('Corrected explanation', (folder/'solution.html').read_text())
        self.assertEqual((folder/'acceptance.json').read_bytes(),receipt)
        self.assertEqual(self.read('leaderboard/credits.json'),credits)
        self.assertEqual(self.read(f'data/{RID}/record.json'),record)
        self.assertNotEqual(self.read('data/revision.json'),revision)
        self.run_build(check=True)

    def test_explanation_is_still_required(self):
        self.receipt_fixture()
        self.write(f'data/{RID}/solution.md','  \n')
        self.assertIn('Missing solution explanation', self.run_build(success=False).stderr)
        (self.root/'data'/RID/'solution.md').unlink()
        self.run_build(success=False)

    def test_relative_explanation_links_render_in_the_instance_context(self):
        self.receipt_fixture()
        self.write(f'data/{RID}/solution.md',
                   '[Motivation](why.md) and [proof](Solution.lean#L1).\n\n'
                   '[data](data/test-example/witness.json)')
        self.run_build()
        rendered=(self.root/f'data/{RID}/solution.html').read_text()
        self.assertIn('href="#case/test-example"',rendered)
        self.assertIn('href="https://github.com/hodge-computer/sextics/blob/main/data/test-example/Solution.lean#L1"',rendered)
        self.assertIn('href="data/test-example/witness.json"',rendered)

    def test_root_relative_source_links_go_to_github(self):
        self.write('formal/README.md', 'Contract')
        self.write('formal/lean/Example.lean', 'example : True := by trivial')
        for target in ['formal/README.md', '/formal/lean/Example.lean#L1']:
            rendered = render('[source](' + target + ')', root=self.root,
                              source_path=Path('data') / RID / 'solution.md')
            self.assertIn('https://github.com/hodge-computer/sextics/blob/main/' + target.lstrip('/'), rendered)

    def test_preflight_resolves_added_files_before_checkout_and_rejects_missing_links(self):
        source=Path('data')/RID/'solution.md'
        proof=source.parent/'Solution.lean'
        text='[proof][src]\n\n[src]: Solution.lean#L1'
        with self.assertRaisesRegex(ValueError,'solution.md: missing local link Solution.lean'):
            render(text,root=self.root,source_path=source)
        rendered=render(text,root=self.root,source_path=source,extra_files=[proof])
        self.assertIn('/data/test-example/Solution.lean#L1',rendered)
        self.assertFalse((self.root/proof).exists())
        for link in ('missing.md','../../../../etc/passwd','%2e%2e/%2e%2e/%2e%2e/etc/passwd'):
            with self.subTest(link=link),self.assertRaisesRegex(ValueError,'missing local link'):
                render('[bad]('+link+')',root=self.root,source_path=source,extra_files=[proof])

    def test_explanation_preflight_reports_invalid_formula(self):
        path=self.root/'candidate-solution.html'
        for formula,valid in [(r'\(D=1\)',True),(r'\(\undefinedHodgeCommand\)',False)]:
            path.write_text(render(formula))
            result=subprocess.run([sys.executable,str(ROOT/'scripts/check-content.py'),
                                   '--explanation',str(path)],capture_output=True,text=True)
            self.assertEqual(result.returncode==0,valid,result.stdout+result.stderr)
            if not valid:
                self.assertIn('candidate-solution.html',result.stderr)
                self.assertIn('undefinedHodgeCommand',result.stderr)

    def test_added_proof_helper_requires_reverification(self):
        self.receipt_fixture()
        self.write(f'data/{RID}/Helper.lean','-- new proof dependency')
        self.assertIn('has changed',self.run_build(success=False).stderr)

    def test_publisher_checks_initial_prose_but_allows_edited_prose_on_retry(self):
        receipt=self.receipt_fixture()
        folder=self.root/'data'/RID
        pr=receipt['pullRequest']
        report=receipt['verification']
        self.write('.github/solve-policy.json',json.dumps({'mode':'live'}))
        archive=io.BytesIO()
        with zipfile.ZipFile(archive,'w') as bundle:
            bundle.writestr('report.json',json.dumps(report))
        responses={
            'pulls/123':{'merged':True,'merge_commit_sha':pr['mergeCommit'],
                         'head':{'sha':pr['headCommit']},'user':{'login':receipt['githubLogin']},
                         'created_at':receipt['submittedAt'],'merged_at':'2026-10-15T00:01:00Z',
                         'html_url':pr['url']},
            'commits/'+pr['mergeCommit']:{},
            'commits/'+pr['headCommit']+'/statuses?per_page=100':[
                {'context':'solve/lean','state':'success','creator':{'login':'github-actions[bot]'},
                 'target_url':'https://github.com/hodge-computer/sextics/actions/runs/123'}],
            'actions/runs/123':{'path':'.github/workflows/solve-proposal.yml'},
            'actions/runs/123/artifacts?per_page=100':{'artifacts':[
                {'name':'solve-123-'+pr['headCommit'],'expired':False,'size_in_bytes':1000,'id':1}]},
            'actions/artifacts/1/zip':archive.getvalue(),
        }
        def api(path,**kwargs):
            return responses[path.removeprefix('repos/hodge-computer/sextics/')]
        # GitHub report authentication is independent of this content-boundary
        # test; only API responses and process execution are replaced here.
        with patch.object(publisher,'ROOT',self.root),patch.object(publisher,'api',api), \
             patch.object(publisher,'git',return_value=f'data/{RID}/proof.json\n'.encode()), \
             patch.object(publisher,'validate_report'), \
             patch.object(publisher.subprocess,'run',return_value=SimpleNamespace(returncode=0)):
            (folder/'acceptance.json').unlink()
            self.write(f'data/{RID}/solution.md','Changed since the proposal check.')
            with self.assertRaisesRegex(ValueError,'differs from the checked sources'):
                publisher.publish(123)
            self.assertFalse((folder/'acceptance.json').exists())
            self.write(f'data/{RID}/acceptance.json',json.dumps(receipt))
            publisher.publish(123)
            self.assertEqual(self.read(f'data/{RID}/acceptance.json'),receipt)
            self.write(f'data/{RID}/Solution.lean','-- changed proof')
            with self.assertRaisesRegex(ValueError,'proof or witness has changed'):
                publisher.publish(123)

    def test_invalid_receipt_and_claimed_identity_cannot_publish(self):
        original=self.receipt_fixture()
        for key,value in [('formalAcceptance',False),('githubLogin','another-user')]:
            receipt=copy.deepcopy(original);receipt[key]=value
            self.write(f'data/{RID}/acceptance.json',json.dumps(receipt))
            self.run_build(success=False)
        self.write(f'data/{RID}/acceptance.json',json.dumps(original))
        path=self.root/'data'/RID/'solution.rec'; solution=yaml.safe_load(path.read_text())
        solution['solver']['githubLogin']='another-user';path.write_text(yaml.safe_dump(solution))
        self.assertIn('differs from the accepted',self.run_build(success=False).stderr)

    def test_owner_merge_gates_initial_publication_and_credits_the_contributor(self):
        receipt=self.receipt_fixture(login='contributor')
        report=receipt['verification']; report['schemaVersion']=2
        pr=receipt['pullRequest']; folder=self.root/'data'/RID
        (folder/'acceptance.json').unlink(); (folder/'solution.rec').unlink()
        self.write('.github/solve-policy.json',json.dumps({'mode':'live','owner':'benediamond'}))
        archive=io.BytesIO()
        with zipfile.ZipFile(archive,'w') as bundle:
            bundle.writestr('report.json',json.dumps(report))
        responses={
            'pulls/123':{'merged':True,'merge_commit_sha':pr['mergeCommit'],
                         'merged_by':{'login':'stranger'},
                         'head':{'sha':pr['headCommit']},'user':{'login':'contributor'},
                         'created_at':receipt['submittedAt'],'merged_at':receipt['acceptedAt'],
                         'html_url':pr['url']},
            'commits/'+pr['mergeCommit']:{},
            'commits/'+pr['headCommit']+'/statuses?per_page=100':[
                {'context':'solve/lean','state':'success','creator':{'login':'github-actions[bot]'},
                 'target_url':'https://github.com/hodge-computer/sextics/actions/runs/123'}],
            'actions/runs/123':{'path':'.github/workflows/solve-proposal.yml','event':'pull_request_target'},
            'actions/runs/123/artifacts?per_page=100':{'artifacts':[
                {'name':'solve-123-'+pr['headCommit'],'expired':False,'size_in_bytes':1000,'id':1}]},
            'actions/artifacts/1/zip':archive.getvalue(),
        }
        def api(path,**kwargs):
            return responses[path.removeprefix('repos/hodge-computer/sextics/')]
        # Report authentication is covered in test_check.py; exercise the real
        # owner gate, receipt creation, and content binding without compiling Lean.
        with patch.object(publisher,'ROOT',self.root),patch.object(publisher,'api',api), \
             patch.object(publisher,'git',return_value=f'data/{RID}/proof.json\n'.encode()), \
             patch.object(publisher,'validate_report'), \
             patch.object(publisher.subprocess,'run',return_value=SimpleNamespace(returncode=0)):
            with self.assertRaisesRegex(ValueError,'configured owner'):
                publisher.publish(123)
            self.assertFalse((folder/'acceptance.json').exists())
            responses['pulls/123']['merged_by']['login']='benediamond'
            publisher.publish(123)
            accepted=self.read(f'data/{RID}/acceptance.json')
            self.assertEqual(accepted['ownerAuthorization']['method'],'owner_merge')
            self.assertEqual(accepted['ownerAuthorization']['mergeCommit'],pr['mergeCommit'])
            self.assertEqual(accepted['githubLogin'],'contributor')
            # Publication retries retain the already accepted approval evidence.
            publisher.publish(123)
            self.assertEqual(accepted,self.read(f'data/{RID}/acceptance.json'))
        self.run_build()
        self.assertEqual(self.read('leaderboard/credits.json')['credits'][0]['githubLogin'],'contributor')

    def test_instance_formal_flag_cannot_bypass_acceptance(self):
        path=self.root/'data'/RID/'instance.rec'
        path.write_text(path.read_text().replace('formalStatus: unproved','formalStatus: proved'))
        self.assertIn('no formal acceptance',self.run_build(success=False).stderr)

    def test_prose_math_escaping_and_ui_updates(self):
        before=self.read('data/revision.json')
        self.write(f'data/{RID}/why.md',r'A **reason** with \(X_0\) and <script>alert(1)</script>.'+'\n\n'+r'\[D^2 \mid F\]')
        self.run_build()
        rendered=(self.root/f'data/{RID}/why.html').read_text()
        self.assertIn('<strong>reason</strong>',rendered)
        self.assertIn('data-math>X_0</span>',rendered)
        self.assertIn(r'data-display>D^2 \mid F</div>',rendered)
        self.assertNotIn('<script>',rendered)
        self.assertNotEqual(before,self.read('data/revision.json'))
        before=self.read('data/revision.json')
        self.write('assets/renderer.js','// Changed renderer fixture');self.run_build()
        self.assertNotEqual(before,self.read('data/revision.json'))

    def test_math_heading_links_remain_stable(self):
        heading=r'## Solving \(E_1\) and \(E_2\)'+'\n'
        for preceding in ('',r'An earlier formula \(F^2\).'+'\n\n'):
            self.write('docs/overview.md',preceding+heading);self.run_build()
            rendered=(self.root/'docs/overview.html').read_text()
            self.assertIn('id="solving-e_1-and-e_2"',rendered)
            self.assertNotIn('hodgemathtoken',rendered.lower())

if __name__=='__main__': unittest.main()
