#!/usr/bin/env python3
"""Real Lean and OS-sandbox checks; no GitHub calls and no catalogue mutations."""
import json
from pathlib import Path
import tempfile
import unittest

import yaml

from check import ROOT, module_order
from sandbox import verify

PROOF = 'import HodgeTarget\nopen HodgeComputer MvPolynomial\nnoncomputable section\nnamespace Submission\n theorem certificate : HasCertificate HodgeSubmission.F HodgeSubmission.A HodgeSubmission.q := by\n  refine ⟨0, 1, (fun _ => 0), 0, ?_⟩\n  constructor\n  · exact one_ne_zero\n  · exact isHomogeneous_one (Fin 6) ℂ\n  · intro i; exact isHomogeneous_zero _ _ _\n  · exact isRelPrime_one_right\n  · simp [defect, HodgeSubmission.A, HodgeTestbed.directional, HodgeTestbed.divergenceNumerator, HodgeTestbed.divergence]\nend Submission\n'

class LeanAcceptance(unittest.TestCase):
    def setUp(self):
        self.instance={'id':'integration-fixture','F':'X0**6','q':1,'A':'0'}
        self.policy=json.loads((ROOT/'.github/solve-policy.json').read_text())
        self.tmp=tempfile.TemporaryDirectory(prefix='hodge-audit-test-')
        self.addCleanup(self.tmp.cleanup)
        self.output=Path(self.tmp.name)/'logs';self.output.mkdir()

    def verify(self,source,imports=None,witness=None):
        files={'Solution.lean':source.encode()}
        metadata={'theorem':'Submission.certificate'}
        if witness is not None:
            files['witness.json']=json.dumps(witness).encode()
            metadata['witnessTheorem']='Submission.witness'
        # Explicit imports bypass the source filter only in the axiom/sandbox defense tests.
        order,imports=module_order(files) if imports is None else (['Solution.lean'],imports)
        try:
            return verify(ROOT,files,self.instance,metadata,order,imports,self.policy,self.output)
        except ValueError:
            for log in self.output.glob('*.log'):
                if log.stat().st_size: print(log.name+': '+log.read_text()[-2000:],flush=True)
            raise

    def test_real_certificate_and_sandbox(self):
        sentinel=Path(self.tmp.name)/'outside-secret.txt';sentinel.write_text('test-only sentinel')
        forbidden=Path(self.tmp.name)/'outside-write.txt'
        # Bypass the source filter deliberately to test the OS barrier underneath it.
        probe=f'''\n#eval do
  let readable ← try
    let _ ← IO.FS.readFile {json.dumps(str(sentinel))}
    pure true
  catch _ => pure false
  if readable then throw (IO.userError "Sandbox exposed an outside file")
  let writable ← try
    IO.FS.writeFile {json.dumps(str(forbidden))} "bad"
    pure true
  catch _ => pure false
  if writable then throw (IO.userError "Sandbox allowed an outside write")
'''
        result=self.verify(PROOF+probe,['HodgeComputer.Verify'])
        self.assertTrue(result['kernelReplay'])
        self.assertFalse(forbidden.exists())
        self.assertLessEqual(set(result['axioms']),{'propext','Classical.choice','Quot.sound'})

    def test_each_module_replayed_including_unused_helpers(self):
        files={
            'Solution.lean': PROOF.encode(),
            'Unused.lean': b'import HodgeTarget\ntheorem unused_helper : True := True.intro\n',
        }
        order,imports=module_order(files)
        result=verify(ROOT,files,self.instance,{'theorem':'Submission.certificate'},
                      order,imports,self.policy,self.output)
        self.assertTrue(result['kernelReplay'])
        self.assertEqual({p.name for p in self.output.glob('kernel-*.log')},
                         {'kernel-HodgeTarget.log','kernel-Unused.log',
                          'kernel-Solution.log','kernel-HodgeChecked.log'})
        for module in ('Unused','Solution'):
            self.assertIn('replaying Proposal.'+module,
                          (self.output/('kernel-'+module+'.log')).read_text())

    def test_wrong_statement_rejected(self):
        with self.assertRaises(ValueError):self.verify('import HodgeTarget\ntheorem Submission.certificate : True := True.intro\n')
        self.assertIn('HodgeComputer.HasCertificate',(self.output/'compile-HodgeChecked.log').read_text())

    def test_displayed_witness_must_match_the_proved_witness(self):
        source=PROOF.replace('end Submission', '''theorem witness : Verify HodgeSubmission.F HodgeSubmission.A HodgeSubmission.q
    0 1 (fun _ => 0) 0 := by
  constructor
  · exact one_ne_zero
  · exact isHomogeneous_one (Fin 6) ℂ
  · intro i; exact isHomogeneous_zero _ _ _
  · exact isRelPrime_one_right
  · simp [defect, HodgeSubmission.A, HodgeTestbed.directional, HodgeTestbed.divergenceNumerator, HodgeTestbed.divergence]
end Submission''')
        # Both constants could be valid denominators, but the exported one must
        # be exactly the denominator bound by the submitted witness theorem.
        with self.assertRaises(ValueError):
            self.verify(source,witness={'d':0,'D':'2','N':['0']*6,'Q':'0'})
        log=(self.output/'compile-HodgeChecked.log').read_text()
        self.assertIn('Submission.witness',log)
        self.assertIn('HodgeWitness.D',log)

    def test_transitive_unapproved_axiom_rejected(self):
        source='''import HodgeTarget
axiom injected : HodgeComputer.HasCertificate HodgeSubmission.F HodgeSubmission.A HodgeSubmission.q
theorem Submission.certificate : HodgeComputer.HasCertificate HodgeSubmission.F HodgeSubmission.A HodgeSubmission.q := injected
'''
        with self.assertRaises(ValueError):self.verify(source,['HodgeComputer.Verify'])
        self.assertIn('Unapproved axiom: injected',(self.output/'theorem-audit.log').read_text())

if __name__=='__main__':unittest.main(verbosity=2)
