"""Run the exact F1 suite and assertion-detected semantic mutants; no admission."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys,tempfile

MUTATIONS={
 'empty_violation_set':('for nid in sorted(newly_controlling | retained_impacted):','for nid in sorted(set()):'),
 'ignore_affected_controlling':('retained_impacted = new_controls.intersection(impact["impacted"])','retained_impacted = set()'),
 'disable_cli_refusal':('if args.command != "tip-health" and report.get("transition_ok") is not True:', 'if False and report.get("transition_ok") is not True:'),
 'ignore_second_status':('statuses.extend(node.get("source_statuses") or [])','statuses.extend([])'),
 'block_legitimate_demotion':('retained_impacted = new_controls.intersection(impact["impacted"])','retained_impacted = old_controls.intersection(impact["impacted"])'),
}
FILES=('tools/claims_gate_adapter.py','tools/semantic_digest.py','tests/test_claims_gate_enforcement.py')
def hashes(root):return {f:hashlib.sha256((root/f).read_bytes()).hexdigest() for f in FILES}
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--subject-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
 a=p.parse_args();root=a.subject_root.resolve();out=a.output.resolve()
 if root==out or root in out.parents:p.error('Output must be outside subject')
 out.mkdir(parents=True,exist_ok=False);before=hashes(root);source=(root/FILES[0]).read_text();reports=[]
 for mode,flag in [('normal',[]),('optimized',['-O'])]:
  cmd=[sys.executable,*flag,'-B','-S','-m','unittest','discover','-s','tests','-p','test_claims_gate_enforcement.py','-v']
  r=subprocess.run(cmd,cwd=root,capture_output=True,text=True,timeout=90)
  log=r.stdout+r.stderr;(out/f'{mode}.log').write_text(log)
  good=r.returncode==0 and 'Ran 21 tests' in log and '\nOK\n' in log
  mutants={}
  for name,(old,new) in MUTATIONS.items():
   if source.count(old)!=1:raise RuntimeError('Nonunique anchor: '+name)
   with tempfile.TemporaryDirectory(prefix='f1-mutant-') as temp:
    t=Path(temp)
    for f in FILES:
     q=t/f;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/f,q)
    (t/FILES[0]).write_text(source.replace(old,new))
    r=subprocess.run(cmd,cwd=t,capture_output=True,text=True,timeout=90)
   log=r.stdout+r.stderr;(out/f'{mode}_{name}.log').write_text(log)
   mutants[name]=r.returncode==1 and 'FAILED (failures=' in log and 'ERROR:' not in log and 'AssertionError' in log
  reports.append({'mode':mode,'test_count':21,'tests_passed':good,'mutants_assertion_detected':mutants})
 after=hashes(root);result={'python':sys.version,'source_sha256':before,'source_unchanged':before==after,'runs':reports,
 'passed':before==after and all(r['tests_passed'] and all(r['mutants_assertion_detected'].values()) for r in reports),
 'scope':'F1 only. Positive scientific admission and remaining source/context/ref/JSON defects are not implemented.'}
 (out/'REPORT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
 return 0 if result['passed'] else 1
if __name__=='__main__':raise SystemExit(main())
