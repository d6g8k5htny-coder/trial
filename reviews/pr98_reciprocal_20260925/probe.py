"""Source-bound read-only PR98 review. Success reproduces observations, not admission."""
from pathlib import Path
import argparse, copy, hashlib, json, os, shutil, subprocess, sys, tempfile

SUBJECT = '776fdb75eb718293e296937c33eb77c228616a86'
BLOBS = {'tools/claims_gate_adapter.py':'9b7cf55cfe2fbfe9a6aa6e9983f283a827b523ac',
         'tools/semantic_digest.py':'28a171662b8f6751d587e3db4852442fe7548ef6'}

def identities(root):
    result={}
    for name, expected in BLOBS.items():
        b=(root/name).read_bytes()
        blob=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
        if blob!=expected: raise RuntimeError('Subject blob mismatch: '+name)
        result[name]={'git_blob':blob,'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)}
    return result

def git(root,*args):
    p=subprocess.run(['git','-C',str(root),*args],capture_output=True,text=True,timeout=20)
    if p.returncode: raise RuntimeError(p.stderr)
    return p.stdout.strip()

def write_json(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2)+'\n')

def graph():
    return {'as_of':'2026-09-25','premises':{
        'P':{'status_register_note':'OPEN','source':{'path':'proof.md'}}},
        'claims':{'T':{'grade':'OPEN','controlling':False,'depends_on':['P'],
                       'source':{'path':'theorem.md'}},
                  'U':{'grade':'OPEN','source':{'path':'unrelated.md'}}}}

def commit(root,label):
    git(root,'add','.')
    git(root,'commit','--allow-empty','-qm',label)
    return git(root,'rev-parse','HEAD')

def run_case(subject,out,name,mode,setup=None,change=None,refs=False,positive=None,defect=None):
    with tempfile.TemporaryDirectory(prefix='pr98-review-') as temp:
        root=Path(temp)
        git(root,'init','-q');git(root,'config','user.email','review@example.invalid')
        git(root,'config','user.name','Synthetic review fixture')
        g=graph()
        cw={'rows':[{'main_claim_or_premise_id':'P','authority':'a'}]}
        au={'authorities':{'a':{},'b':{}},'this_package':{'id':'adapter'}}
        if setup: setup(g)
        write_json(root/'claims/graph.json',g)
        write_json(root/'architecture/scientific_state/v1/ID_CROSSWALK.json',cw)
        write_json(root/'architecture/scientific_state/v1/AUTHORITY_MAP.json',au)
        for f in ('proof.md','theorem.md','unrelated.md','mirror.md'):
            (root/f).write_text('Synthetic '+f+' version 1\n')
        before=commit(root,'before')
        if change: change(root,g,cw,au)
        after=commit(root,'after')
        b,a=before,after
        if refs:
            git(root,'branch','review-before',before);git(root,'branch','review-after',after)
            b,a='review-before','review-after'
        env=os.environ.copy();env['CLAIMS_GATE_BEFORE_REF']=b;env['CLAIMS_GATE_AFTER_REF']=a
        flags=['-O'] if mode=='optimized' else []
        command=[sys.executable,*flags,'-B','-S',str(subject/'tools/claims_gate_adapter.py'),
                 'event-compare','--repo-root',str(root)]
        p=subprocess.run(command,env=env,capture_output=True,text=True,timeout=30)
        try: report=json.loads(p.stdout)
        except json.JSONDecodeError: report=None
        observed={'case':name,'mode':mode,'returncode':p.returncode,'report':report,
                  'stderr':p.stderr,'before_fixture_commit':before,'after_fixture_commit':after,
                  'command':['PYTHON',*flags,'-B','-S','SUBJECT/tools/claims_gate_adapter.py',
                             'event-compare','--repo-root','SYNTHETIC_FIXTURE']}
        if defect is not None:
            observed['expected_class']='DEFECT_REPRODUCED'
            observed['observation_matches']=bool(defect(p.returncode,report))
        else:
            observed['expected_class']='CONTROL_PASSED'
            observed['observation_matches']=bool(positive(p.returncode,report))
        (out/(mode+'_'+name+'.json')).write_text(json.dumps(observed,indent=2)+'\n')
        return {k:v for k,v in observed.items() if k not in ('report','stderr','command')}

def save_graph(root,g,*ignored): write_json(root/'claims/graph.json',g)
def imp(report): return set((report or {}).get('reverse_impact',{}).get('impacted',[]))
def accepted(rc,report): return rc==0 and isinstance(report,dict) and report.get('transition_ok') is True

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--subject-root',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();subject=args.subject_root.resolve();out=args.output.resolve()
    if out==subject or subject in out.parents: p.error('Evidence must be outside subject checkout')
    out.mkdir(parents=True,exist_ok=False)
    before=identities(subject);rows=[]
    for mode in ('normal','optimized'):
        def run(name,**kw):
            rows.append(run_case(subject,out,name,mode,**kw))
        run('unchanged_tip',positive=lambda rc,r:accepted(rc,r) and not imp(r))
        run('ordinary_source_edit',change=lambda root,*_: (root/'proof.md').write_text('Synthetic correction\n'),
            positive=lambda rc,r:accepted(rc,r) and imp(r)=={'P','T'})
        def deleted(root,g,*_):g['claims']['T']['depends_on']=[];save_graph(root,g)
        run('deleted_required_edge',change=deleted,
            positive=lambda rc,r:accepted(rc,r) and {'P','T'}<=imp(r) and 'U' not in imp(r))
        def sub_setup(g):g['claims']['T']['sub_obligations']=g['claims']['T'].pop('depends_on')
        def sub_deleted(root,g,*_):g['claims']['T']['sub_obligations']=[];save_graph(root,g)
        run('deleted_subobligation',setup=sub_setup,change=sub_deleted,
            positive=lambda rc,r:accepted(rc,r) and {'P','T'}<=imp(r) and 'U' not in imp(r))
        for field in ('depends_on','sub_obligations'):
            for value,label in ((False,'false'),(None,'null')):
                def malformed(root,g,*_,field=field,value=value):
                    g['claims']['T'][field]=value;save_graph(root,g)
                run('reject_'+field+'_'+label,change=malformed,
                    positive=lambda rc,r:rc!=0 and isinstance(r,dict) and 'error' in r)
        def invalid_asof(root,g,*_):g['as_of']='';save_graph(root,g)
        run('reject_empty_asof',change=invalid_asof,
            positive=lambda rc,r:rc!=0 and isinstance(r,dict) and 'error' in r)
        def refuted(g):g['premises']['P']['status_register_note']='REFUTED'
        def promote(root,g,*_):
            g['claims']['T'].update(grade='LIVE_ROOT_THEOREM',controlling=True);save_graph(root,g)
        run('illegal_promotion_over_refuted_premise',setup=refuted,change=promote,
            defect=lambda rc,r:accepted(rc,r) and 'T' in r['controlling_impacted'] and
             r['hold_proposals']['T']['refuted_required']==['P'])
        def controlling(g):g['claims']['T'].update(grade='LIVE_ROOT_THEOREM',controlling=True)
        run('changed_premise_consumer_still_controlling',setup=controlling,
            change=lambda root,*_:(root/'proof.md').write_text('Changed load-bearing lemma\n'),
            defect=lambda rc,r:accepted(rc,r) and 'T' in r['controlling_impacted'])
        def bindings(g):
            g['premises']['P'].pop('source')
            g['premises']['P']['source_bindings']=[{'repo':'d6g8k5htny-coder/main','path':'proof.md'}]
        run('canonical_source_bindings_bytes_ignored',setup=bindings,
            change=lambda root,*_:(root/'proof.md').write_text('Changed canonical source\n'),
            defect=lambda rc,r:accepted(rc,r) and not imp(r) and r['new_sources']['P']['kind']=='record_only')
        def shadow(g):g['premises']['P']['mirror_path']='mirror.md'
        run('first_path_shadows_second_source',setup=shadow,
            change=lambda root,*_:(root/'proof.md').write_text('Changed second declared source\n'),
            defect=lambda rc,r:accepted(rc,r) and not imp(r) and r['new_sources']['P']['path']=='mirror.md')
        def owner(root,g,cw,au):
            cw['rows'][0]['authority']='b'
            write_json(root/'architecture/scientific_state/v1/ID_CROSSWALK.json',cw)
        run('authority_owner_change_untracked',change=owner,
            defect=lambda rc,r:accepted(rc,r) and not imp(r) and 'before_crosswalk_identity' not in r)
        run('mutable_refs_accepted_as_commit_identity',refs=True,
            defect=lambda rc,r:accepted(rc,r) and r['base_commit']=='review-before' and r['head_commit']=='review-after')
        def duplicate(root,g,*_):
            path=root/'claims/graph.json';s=json.dumps(g)
            s=s.replace('"depends_on": ["P"]','"depends_on": ["P"], "depends_on": []')
            if s==json.dumps(g):raise RuntimeError('Duplicate-key fixture not inserted')
            path.write_text(s+'\n')
        run('duplicate_json_dependency_key_accepted',change=duplicate,
            defect=lambda rc,r:accepted(rc,r) and 'T' not in r['hold_proposals'])
    after=identities(subject)
    for name in BLOBS:
        target=out/'subject'/name;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(subject/name,target)
    result={'subject_commit':SUBJECT,'source_identities':before,'source_unchanged':before==after,
            'python':sys.version,'cases':rows,'expected_defect_cases_per_mode':7,
            'expected_control_cases_per_mode':9,'subject_admitted':False,
            'interpretation':'A matching observation may be a reproduced DEFECT, not subject acceptance.',
            'reviewer_lineage':'OpenAI; subject author Cursor, underlying provider not independently established',
            'all_observations_match':all(x['observation_matches'] for x in rows) and before==after}
    (out/'REPORT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
    return 0 if result['all_observations_match'] else 1

if __name__=='__main__': raise SystemExit(main())
