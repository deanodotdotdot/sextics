"""Replay the material exact checks from a self-contained release copy.

Use --full to regenerate the large residual numerators as well. This script
writes audit JSON and logs; run it in a copy if preserving a manifest.
The research run launches it under guard.py --verification.
"""
from pathlib import Path
import datetime as dt
import hashlib,json,os,subprocess,sys,time

root=Path(__file__).resolve().parents[1]
full='--full' in sys.argv
st=time.time();started=dt.datetime.now(dt.timezone.utc).isoformat()
initial=json.loads((root/'taylor-full-residual.json').read_text())
expected={z['file']:z['sha256'] for z in initial['rows']}
steps=[]
def add(name,script,*args,env=None):steps.append((name,script,list(args),env or {}))
add('native-full-connection','packet/audit/theta/verify_full_base_connection.py')
add('actual-source','code/audit_actual_source.py')
add('corrected-i-congruence','code/audit_i_congruence.py')
add('corrected-support-fiber','code/audit_support_and_fiber.py')
add('independent-cutoff','code/independent_taylor_cutoff.py')
add('source-fiber-normalization','code/audit_source_fiber_normalization.py')
add('original-chart','code/verify_original_chart.py')
add('original-density','code/original_density_binding.py')
add('generic-original-transport','code/audit_original_transport.py')
add('preferred-original-expression','code/build_taylor_original_expression.py')
add('original-field-positive','code/algebraic_taylor_original_field_check.py')
add('original-field-negative','code/algebraic_taylor_original_field_check.py',env={'DECK_SIGN':'-1'})
add('partial-field-admissibility','code/audit_partial_admissibility.py')
add('restricted-cutoff-minimum','code/audit_scalar_cutoff_minimum.py')
if full:add('direct-full-residual','code/expand_taylor_residual.py')
add('independent-full-residual','code/verify_taylor_full_residual.py')
add('residual-denominator','code/audit_residual_exact_poles.py')
add('native-relative-bounds','code/audit_relative_i_completeness.py')
add('w-infinity','code/other_direction_infinity.py')
add('j-infinity','code/j_infinity_shear_polynomial.py')
add('taylor-i-w-bounds','code/audit_taylor_relative_completeness.py')
add('taylor-j-bounds','code/audit_j_relative_completeness.py')
add('bare-source-bounds','code/audit_bare_source_relative_bounds.py')
for direction in ['i','j','w']:
 add('bare-'+direction+'-operator','code/independent_bare_source_'+direction+'_operator.py',env={'SYMPY_GROUND_TYPES':'python'})
 add('bare-'+direction+'-minor','code/verify_bare_source_'+direction+'_witness_stdlib.py')
for direction,mid in [('i',''),('j','j_'),('w','w_')]:
 add('taylor-'+direction+'-operator','code/independent_taylor_'+mid+'relative_operator.py',env={'SYMPY_GROUND_TYPES':'python'})
 add('taylor-'+direction+'-minor','code/verify_taylor_'+mid+'rank_witness_stdlib.py')
add('corrected-i-operator','code/independent_corrected_relative_operator.py',env={'SYMPY_GROUND_TYPES':'python'})
add('corrected-i-minor','code/verify_corrected_rank_witness_stdlib.py')
add('prior-i-operator','code/independent_relative_operator.py',env={'SYMPY_GROUND_TYPES':'python'})
add('prior-i-minor','code/verify_rank_witness_stdlib.py')
add('actual-delta-lowering','code/build_actual_delta_lowering.py')
record={'status':'running','started_utc':started,'full_regeneration':full,'steps':[]}
out=root/'VERIFICATION-SUMMARY.json'
def save():out.write_text(json.dumps(record,indent=2)+'\n')
save()
for index,(name,script,args,extra) in enumerate(steps):
 now=time.time();log='logs/release-'+name+'.log'
 print(f'BEGIN {index+1}/{len(steps)} {name}',flush=True)
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1');env.update(extra)
 with (root/log).open('w') as dest:
  result=subprocess.run([sys.executable,str(root/script),*args],cwd=root,env=env,stdout=dest,stderr=subprocess.STDOUT)
 record['steps'].append({'name':name,'script':script,'args':args,'environment_overrides':extra,'returncode':result.returncode,'seconds':time.time()-now,'log':log})
 save()
 if result.returncode:
  record['status']='FAILED';record['failed_step']=name;save()
  print('FAILED',name,'see',log,flush=True);raise SystemExit(result.returncode)
 print(f'PASS {index+1}/{len(steps)} {name} ({time.time()-now:.1f}s)',flush=True)
for path,digest in expected.items():assert hashlib.sha256((root/path).read_bytes()).hexdigest()==digest,path
current=json.loads((root/'original-taylor-partial-field-expression.json').read_text())
assert current['current']=='taylor-discriminant-current.json'
assert 'Dsource=' in current['fiber_numerator'] and 'FDnum' in current['ux']
for d,n,m,det in [('i',12,105,658),('j',8,73,432),('w',20,169,200)]:
 bounds=json.loads((root/'bare-source-relative-completeness-audit.json').read_text())
 family=next(f for f in bounds['families'] if f['direction']==d)
 assert family['numerator_degree_bound']==n and family['screened_bound']==n
 witness=json.loads((root/('bare-source-'+d+'-witness-independent-audit.json')).read_text())
 assert witness['minor_size']==m and witness['determinant_mod_prime']==det
record.update(status='PASS',finished_utc=dt.datetime.now(dt.timezone.utc).isoformat(),seconds=time.time()-st,residual_numerators_reproduced_byte_for_byte=full,residual_numerator_hashes_verified=expected,preferred_expression_normalization_verified=True,complete_bare_source_bounds_bound_to_final_witnesses=True,scope='Material checks replayed from the self-contained release copy. This confirms partial research; it is not a certificate or unrestricted nonexistence proof.')
save();print('PASS release replay',len(steps),'steps',time.time()-st,'seconds',flush=True)
