"""Replay this incremental packet in a writable copy; no network required."""
from pathlib import Path
import json,os,subprocess,sys,time,hashlib,datetime
root=Path(__file__).resolve().parents[1];start=time.time();steps=[];records=[]
expected={}
for name in ['two-node-physical-current-improved.json','two-node-physical-current-patched.json']:
 for block in json.loads((root/name).read_text())['slices']:
  for row in block['rows']:expected[row['file']]=row['sha256']
def add(name,script,env=None):steps.append((name,script,env or {}))
add('source-fiber-normalization','audit_source_fiber_normalization.py')
add('critical-resultant','critical_quartic.py')
add('native-logarithmic-frame','audit_logarithmic_fields.py')
add('critical-normalized-residue','critical_normal_residue.py')
add('critical-cover-ramification','audit_critical_cusp.py')
add('independent-source-log-frame-resultant','independent_new_identities.py')
add('independent-critical-residue','independent_critical_residue.py')
add('scalar-unit-ideal-geometric-inputs','audit_coupled_unit_geometry.py')
add('native-double-node-current','build_two_node_coupled_current.py')
add('actual-improved-two-node-current','apply_two_node_physical_current_improved.py')
add('independent-two-node-current','independent_two_node_improved_audit.py')
add('improved-original-field-positive','algebraic_two_node_improved_original_field_check.py')
add('improved-original-field-negative','algebraic_two_node_improved_original_field_check.py',{'DECK_SIGN':'-1'})
add('actual-patched-current','patch_two_node_current.py')
add('direct-native-patched-reconstruction','verify_patched_native_residual.py')
add('generic-patched-support','audit_patched_generic_support.py')
add('independent-patch-support','independent_patched_audit.py')
add('patched-original-field-positive','algebraic_two_node_patched_original_field_check.py')
add('patched-original-field-negative','algebraic_two_node_patched_original_field_check.py',{'DECK_SIGN':'-1'})
add('displayed-formulas','audit_displayed_formulas.py')
logdir=root/'verification-logs';logdir.mkdir(exist_ok=True)
for name,script,extra in steps:
 t=time.time();env=os.environ.copy();env.update(extra)
 with (logdir/(name+'.log')).open('w') as out:r=subprocess.run([sys.executable,str(root/'code'/script)],cwd=root,env=env,stdout=out,stderr=subprocess.STDOUT)
 record={'name':name,'script':'code/'+script,'environment_override':extra,'returncode':r.returncode,'seconds':round(time.time()-t,3)};records.append(record);print('PASS' if r.returncode==0 else 'FAIL',name,record['seconds'],flush=True)
 if r.returncode:raise SystemExit('Replay failed: '+name)
for name,digest in expected.items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest,name
out={'status':'PASS','step_count':len(records),'steps':records,'all_32_residual_files_reproduced_byte_for_byte':True,'residual_sha256':expected,'seconds':round(time.time()-start,3),'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'certificate':False,'scope':'Exact computational checks of the stated partial results. No formal proof assistant, global zero residual or original F^2 certificate.'};(root/'VERIFICATION.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS',len(records),'steps; all32 residual files reproduced',out['seconds'],flush=True)
