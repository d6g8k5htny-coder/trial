"""Bounded public cross-repository replay. No token, private source or repository write.
Downloads only immutable, hash-pinned public sources and runs their stated tests.
Usage: python -B -S replay.py --output /absolute/new/directory
"""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.request

OWNER='d6g8k5htny-coder'
PUBLIC={'main','Math-','governance-','meta-framework','query-','google-drive','trial'}
PINS=[
 ('meta-framework','149b1287929ee1aa8b5e4418dfb5a8c44646201b','registry.json',3967,'32799b1fbed43d1cf02d14a4e62e0b6a43e6601a7c3b457bb2e730653ab6e7d6'),
 ('query-','8e201316d17cf4ff3c679e1e9906d4b016ac6730','research_query.py',5577,'54105dcd723e71b19263afc8f449a7d77b78cec27148f13603f33be7727e6b6b'),
 ('trial','f3147174381179b1ed3cc782417ca3901b79df69','federation/test_federation.py',5099,'9638dd37c2e73f54941668e25dff61465d2388e8a666d121330b8bc45e41813a'),
]
MUTANTS={
 'drop_cone_cutoff':('return I(Q(29,6))-root(I(6),2)','return I(Q(29,6))'),
 'halve_scalar_cone':('return I(Q(4,3))','return I(Q(2,3))'),
 'wrong_role_factor':('/(2*root(I(3),2)*pi**','/(4*root(I(3),2)*pi**'),
 'drop_reference_sqrt3':('/(2*root(I(3),2)*pi**','/(2*pi**'),
 'undersized_derivative_polynomial':('1458*(76*24**6+15)','1458*(75*24**6+15)'),
 'wrong_image_exponent':('derivative_bound=Q(image_constant,10**125)','derivative_bound=Q(image_constant,10**100)'),
}


def check(condition,message):
    if not condition:
        raise RuntimeError(message)


def fetch(root,repo,commit,path,size,digest):
    pp=PurePosixPath(path)
    check(repo in PUBLIC and re.fullmatch('[0-9a-f]{40}',commit),'nonpublic or mutable source')
    check(not pp.is_absolute() and '..' not in pp.parts and str(pp)==path and '\\' not in path and ':' not in path,'unsafe path')
    check(type(size) is int and 0<=size<=1000000 and re.fullmatch('[0-9a-f]{64}',digest),'invalid identity')
    url=f'https://raw.githubusercontent.com/{OWNER}/{repo}/{commit}/{path}'
    with urllib.request.urlopen(url,timeout=45) as response:
        raw=response.read(size+1)
    check(len(raw)==size and hashlib.sha256(raw).hexdigest()==digest,'identity mismatch: '+repo+'/'+path)
    dest=root/repo/path
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_bytes(raw)
    return dest


def run(command,cwd,env,logs,name,expected=None,mutant=False):
    proc=subprocess.run(command,cwd=cwd,env=env,capture_output=True,text=True,timeout=90)
    (logs/(name+'.stdout')).write_text(proc.stdout)
    (logs/(name+'.stderr')).write_text(proc.stderr)
    if mutant:
        check(proc.returncode!=0 and 'AssertionError' in proc.stderr,'mutation not assertion-detected: '+name)
    else:
        check(proc.returncode==0,'command failed: '+name)
        if expected is not None:
            check(f'Ran {expected} tests' in proc.stderr and 'skipped=' not in proc.stderr,'wrong/ skipped test count: '+name)
    return proc


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    out=args.output.resolve()
    check(not out.exists(),'output directory must be new')
    out.mkdir(parents=True)
    root=out/'workspace'; root.mkdir()
    logs=out/'logs'; logs.mkdir()
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',FEDERATION_WORKSPACE=str(root))
    identities=[]
    for pin in PINS:
        fetch(root,*pin); identities.append(pin)
    sys.path.insert(0,str(root/'query-'))
    import research_query as query
    catalog=query.load_catalog(root/'meta-framework/registry.json')
    for row in catalog['artifacts']:
        pin=(row['repository'],row['commit'],row['path'],row['bytes'],row['sha256'])
        fetch(root,*pin); identities.append(pin)
    check(len(identities)==8,'unexpected source count')
    verification=query.verify(catalog,root)
    (out/'LOOKUP.json').write_text(json.dumps(query.lookup(catalog,'side24-coefficient'),indent=2)+'\n')
    mathdir=root/'Math-/coefficients/side24_v1'
    modes=[]
    for mode,flags in [('normal',[]),('optimized',['-O'])]:
        cmd=[sys.executable,'-B',*flags,'-S']
        run(cmd+['-m','unittest','-v','test_coefficient'],mathdir,env,logs,'math_'+mode,expected=30)
        run(cmd+['-m','unittest','-v','test_federation'],root/'trial/federation',env,logs,'query_'+mode,expected=20)
        proc=run(cmd+['coefficient.py'],mathdir,env,logs,'coefficient_'+mode)
        check(proc.stdout.encode()==(mathdir/'ENCLOSURE.json').read_bytes(),'computed output differs from pinned output')
        check(json.loads(proc.stdout)['scientific_acceptance'] is False,'false scientific promotion')
        source=(mathdir/'coefficient.py').read_text()
        for tag,(old,new) in MUTANTS.items():
            check(source.count(old)==1,'mutation target is not unique: '+tag)
            scratch=out/'mutations'/mode/tag
            scratch.mkdir(parents=True)
            (scratch/'coefficient.py').write_text(source.replace(old,new))
            shutil.copyfile(mathdir/'test_coefficient.py',scratch/'test_coefficient.py')
            run(cmd+['-m','unittest','-v','test_coefficient'],scratch,env,logs,'mutation_'+tag+'_'+mode,mutant=True)
        modes.append(mode)
    for repo,commit,path,size,digest in identities:
        raw=(root/repo/path).read_bytes()
        check(len(raw)==size and hashlib.sha256(raw).hexdigest()==digest,'source changed during replay')
    report={'passed':True,'python':sys.version,'public_files_verified':len(identities),
            'catalog_artifacts_verified':len(verification['verified']),'distinct_math_tests':30,
            'distinct_engineering_tests':20,'distinct_math_mutations':len(MUTANTS),'modes':modes,
            'sources_unchanged':True,'private_sources_accessed':False,
            'meaning':'same-author source replay and engineering tests, not independent analytic acceptance'}
    (out/'REPORT.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps(report,sort_keys=True))


if __name__=='__main__':
    main()
