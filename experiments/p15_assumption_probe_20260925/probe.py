#!/usr/bin/env python3
"""Bounded, read-only P15 assumption experiment. No network or status writes.

Inputs are exact public Math- bytes; outputs must be a NEW directory. Z3 is a
native runtime dependency. Solver proofs are exported, not independently checked.
"""
from __future__ import annotations
import argparse
import copy
import ctypes as C
import ctypes.util
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import platform
import re
import sys
import time

SPEC_SHA = '45d208d07428ed1b88c0021ca51f246a86e8283a0b90996d009cc21efd124afd'
PARENT_SHA = '87521901ca8e5405b4d1e47f1deb1cd0326affbd6f5967b53c4178590da993f9'
INPUT_COMMIT = '0ae7e8fdf5d359f80cf6a3dcd614120f7aa9a19c'
TARGETS = ('F5_CURVATURE_NONPOSITIVE', 'F10_STRICT_INTERIOR')
OPS = {'+', '-', '*', '/', '=', '<', '<=', '>', '>=', 'not', 'and', 'or'}
NUM = re.compile(r'\d+(?:\.\d+)?\Z')
SYMBOL = re.compile(r'[A-Za-z][A-Za-z0-9_]*\Z')

class Refusal(ValueError):
    """Malformed inputs or undecided cases must not become acceptance."""


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def strict_json(raw: str):
    def pairs(items):
        d = {}
        for k, v in items:
            if k in d:
                raise Refusal('duplicate JSON key: '+k)
            d[k] = v
        return d
    def nonfinite(value):
        raise Refusal('nonfinite JSON: '+value)
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=nonfinite)


def parse(text: str):
    """Parse one bounded S-expression; never evaluate code."""
    if len(text) > 1000000:
        raise Refusal('S-expression exceeds limit')
    toks = re.findall(r'\(|\)|[^\s()]+', text)
    i = 0
    def take(depth=0):
        nonlocal i
        if depth > 100 or i >= len(toks):
            raise Refusal('invalid/deep S-expression')
        t=toks[i];i+=1
        if t == '(':
            ans=[]
            while i<len(toks) and toks[i]!=')':
                ans.append(take(depth+1))
            if i==len(toks): raise Refusal('unclosed S-expression')
            i+=1
            return ans
        if t==')': raise Refusal('unexpected close')
        return t
    ans=take()
    if i!=len(toks): raise Refusal('multiple expressions/command injection')
    return ans


def sort_of(node, variables):
    if isinstance(node,str):
        if node in variables or NUM.fullmatch(node): return 'real'
        raise Refusal('unknown formula atom: '+node)
    if not node or node[0] not in OPS: raise Refusal('unsupported operator')
    op,*args=node
    sorts=[sort_of(a,variables) for a in args]
    if op in {'not','and','or'}:
        if (len(args)!=1 if op=='not' else len(args)<2) or set(sorts)!={'bool'}:
            raise Refusal('Boolean arity/sort mismatch')
        return 'bool'
    if set(sorts)!={'real'}: raise Refusal('arithmetic sort mismatch')
    if op in {'=','<','<=','>','>=','/'} and len(args)!=2: raise Refusal('binary arity')
    if op=='-' and len(args) not in {1,2}: raise Refusal('minus arity')
    if op in {'+','*'} and len(args)<2: raise Refusal('arithmetic arity')
    if op=='/':
        # Only nonzero rational CONSTANT denominators. No underspecified /0.
        def constant(t): return (bool(NUM.fullmatch(t)) if isinstance(t,str)
                                 else t and t[0] in {'+','-','*','/'} and all(constant(x) for x in t[1:]))
        if not constant(args[1]) or exact(args[1],{})==0:
            raise Refusal('division requires nonzero constant denominator')
    return 'bool' if op in {'=','<','<=','>','>='} else 'real'


def exact(t, v):
    if isinstance(t,str): return v[t] if t in v else Fraction(t)
    op,*args=t;xs=[exact(a,v) for a in args]
    if op=='not': return not xs[0]
    if op=='and': return all(xs)
    if op=='or': return any(xs)
    if op=='+': return sum(xs,Fraction(0))
    if op=='*':
        out=Fraction(1)
        for x in xs: out*=x
        return out
    if op=='-': return -xs[0] if len(xs)==1 else xs[0]-xs[1]
    if op=='/':
        if xs[1]==0: raise Refusal('zero rational denominator')
        return xs[0]/xs[1]
    if op=='=': return xs[0]==xs[1]
    if op=='<': return xs[0]<xs[1]
    if op=='<=': return xs[0]<=xs[1]
    if op=='>': return xs[0]>xs[1]
    if op=='>=': return xs[0]>=xs[1]
    raise Refusal('unsupported evaluator operator')


def validate_formula(text,variables):
    t=parse(text)
    if sort_of(t,variables)!='bool': raise Refusal('Boolean formula required')
    return t


def classify(premise_status, negation_status):
    if premise_status=='unsat': return 'VACUOUS'
    if premise_status!='sat': return 'INCONCLUSIVE'
    return {'unsat':'VALID_ALGEBRA', 'sat':'COUNTEREXAMPLE'}.get(negation_status,'INCONCLUSIVE')


class Solver:
    def __init__(self, out:Path, library=None, budget=120):
        libname=library or ctypes.util.find_library('z3')
        if not libname: raise Refusal('native libz3 missing')
        self.lib=C.CDLL(libname)
        for name,args,result in [
            ('Z3_global_param_set',[C.c_char_p,C.c_char_p],None),
            ('Z3_mk_config',[],C.c_void_p),
            ('Z3_set_param_value',[C.c_void_p,C.c_char_p,C.c_char_p],None),
            ('Z3_mk_context',[C.c_void_p],C.c_void_p),
            ('Z3_del_config',[C.c_void_p],None),
            ('Z3_del_context',[C.c_void_p],None),
            ('Z3_eval_smtlib2_string',[C.c_void_p,C.c_char_p],C.c_char_p),
            ('Z3_get_error_code',[C.c_void_p],C.c_uint),
            ('Z3_get_full_version',[],C.c_char_p)]:
            fn=getattr(self.lib,name);fn.argtypes=args;fn.restype=result
        self.callback_type=C.CFUNCTYPE(None,C.c_void_p,C.c_uint)
        self.lib.Z3_set_error_handler.argtypes=[C.c_void_p,self.callback_type]
        self.lib.Z3_set_error_handler.restype=None
        self.lib.Z3_global_param_set(b'proof',b'true')
        self.version=self.lib.Z3_get_full_version().decode()
        self.out=out;self.query_count=0;self.start=time.monotonic();self.budget=budget
        path=Path(libname)
        if not path.is_file() and Path('/proc/self/maps').is_file():
            for line in Path('/proc/self/maps').read_text().splitlines():
                p=line.split()[-1]
                if '/libz3.' in p and Path(p).is_file(): path=Path(p);break
        self.library_hash=sha(path.read_bytes()) if path.is_file() else None

    def query(self, name, variables, formulas):
        if not SYMBOL.fullmatch(name): raise Refusal('unsafe query name')
        if len(set(variables))!=len(variables) or any(not SYMBOL.fullmatch(v) for v in variables):
            raise Refusal('bad variable declaration')
        for f in formulas: validate_formula(f,set(variables))
        remaining=self.budget-(time.monotonic()-self.start)
        if remaining<=0 or self.query_count>=600: raise Refusal('experiment budget exhausted')
        timeout=max(1,min(2000,int(remaining*1000)))
        commands=[f'(set-option :timeout {timeout})','(set-logic QF_NRA)']
        commands += [f'(declare-const {v} Real)' for v in variables]
        commands += [f'(assert {f})' for f in formulas]+['(check-sat)']
        initial='\n'.join(commands)+'\n'
        cfg=self.lib.Z3_mk_config()
        if not cfg: raise Refusal('cannot create solver config')
        self.lib.Z3_set_param_value(cfg,b'proof',b'true')
        ctx=self.lib.Z3_mk_context(cfg);self.lib.Z3_del_config(cfg)
        if not ctx: raise Refusal('cannot create solver context')
        errors=[]
        handler=self.callback_type(lambda _c,e:errors.append(e))
        self.lib.Z3_set_error_handler(ctx,handler)
        try:
            def call(cmd):
                raw=self.lib.Z3_eval_smtlib2_string(ctx,cmd.encode())
                text=raw.decode() if raw else ''
                if errors or self.lib.Z3_get_error_code(ctx) or '(error' in text:
                    raise Refusal('solver error: '+text[:200])
                return text
            first=call(initial).strip()
            if first not in {'sat','unsat','unknown'}: raise Refusal('invalid solver status')
            follow=('(get-proof)\n' if first=='unsat' else
                    '(get-value ('+' '.join(variables)+'))\n' if first=='sat' else
                    '(get-info :reason-unknown)\n')
            details=call(follow)
            if first=='unsat' and '(proof' not in details: raise Refusal('missing proof export')
            values=None
            if first=='sat':
                try:
                    pairs=parse(details)
                    if (not isinstance(pairs,list) or any(not isinstance(p,list) or len(p)!=2 for p in pairs)
                        or {p[0] for p in pairs}!=set(variables) or len(pairs)!=len(variables)):
                        raise Refusal('unexpected model shape')
                    values={k:exact(t,{}) for k,t in pairs}
                    if any(type(v) is not Fraction for v in values.values()): raise Refusal('non-rational model')
                    if any(exact(parse(f),values) is not True for f in formulas): raise Refusal('rational model fails formula')
                except (ValueError, TypeError, KeyError, ZeroDivisionError) as exc:
                    raise Refusal('model cannot be independently rational-checked') from exc
            raw_query='(set-option :produce-proofs true)\n'+initial+follow
            transcript=first+'\n'+details
            (self.out/(name+'.smt2')).write_text(raw_query)
            (self.out/(name+'.txt')).write_text(transcript)
            self.query_count+=1
            return {'status':first,'query_sha256':sha(raw_query.encode()),
                    'transcript_sha256':sha(transcript.encode()),
                    'rational_witness':{k:str(v) for k,v in values.items()} if values is not None else None,
                    'rational_witness_checked':values is not None}
        finally: self.lib.Z3_del_context(ctx)


def panel(cases):
    """Fixed predeclared mutations; expected labels assessed before execution."""
    f5,f10=[cases[t] for t in TARGETS]
    result=[]
    def add(id,base,expected,change):
        c=copy.deepcopy(base);change(c);c['id']=id;c['expected']=expected;result.append(c)
    def h(i,value): return lambda c:c['hypotheses'].__setitem__(i,value)
    def goal(value): return lambda c:c.__setitem__('conclusion',value)
    add('F5_STRICT',f5,'COUNTEREXAMPLE',goal('(< c 0)'))
    add('F5_REVERSE',f5,'COUNTEREXAMPLE',goal('(>= c 0)'))
    add('F5_ZERO_SUM',f5,'COUNTEREXAMPLE',h(2,'(>= (+ a b) 0)'))
    add('F5_ZERO_X',f5,'COUNTEREXAMPLE',h(3,'(>= x 0)'))
    add('F5_SIGN_FLIP',f5,'COUNTEREXAMPLE',h(5,'(= (* d d c) (* a b x))'))
    add('F5_LINEAR_DENOM',f5,'VALID_ALGEBRA',h(5,'(= (* d c) (- (* a b x)))'))
    add('F5_HALF_FACTOR',f5,'VALID_ALGEBRA',h(5,'(= (* d d c) (- (/ (* a b x) 2)))'))
    add('F5_INCONSISTENT_X',f5,'VACUOUS',lambda c:c['hypotheses'].append('(<= x 0)'))
    add('F10_WEAK_GOAL',f10,'VALID_ALGEBRA',goal(f10['conclusion'].replace('(< ','(<= ',1)))
    add('F10_REVERSE',f10,'COUNTEREXAMPLE',goal(f10['conclusion'].replace('(< ','(> ',1)))
    add('F10_INCLUDE_HALF',f10,'COUNTEREXAMPLE',h(0,'(>= p (/ 1 2))'))
    add('F10_ZERO_MASS',f10,'COUNTEREXAMPLE',h(2,'(>= m 0)'))
    add('F10_INCLUDE_ONE',f10,'VALID_ALGEBRA',h(1,'(<= p 1)'))
    add('F10_DOUBLE_RATIO',f10,'COUNTEREXAMPLE',h(4,'(= (* (- 1 p) n) (* 2 p m))'))
    add('F10_NO_UPPER',f10,'VALID_ALGEBRA',lambda c:c['hypotheses'].pop(1))
    add('F10_INCONSISTENT_P',f10,'VACUOUS',lambda c:c['hypotheses'].append('(< p (/ 1 2))'))
    return result


def original_witness_baseline(case):
    values={k:Fraction(v) for k,v in case['witness'].items()}
    if not all(exact(parse(f),values) for f in case['hypotheses']): return 'NOT_APPLICABLE'
    return 'COUNTEREXAMPLE' if not exact(parse(case['conclusion']),values) else 'NO_COUNTEREXAMPLE'


def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('--spec',required=True,type=Path)
    a.add_argument('--parent-proof',required=True,type=Path)
    a.add_argument('--output',required=True,type=Path)
    a.add_argument('--library')
    args=a.parse_args();root=Path(__file__).resolve().parent;out=args.output.resolve()
    if out.exists() or out==root or root in out.parents: raise Refusal('new output outside experiment source required')
    raw=args.spec.read_bytes();parent=args.parent_proof.read_bytes()
    if sha(raw)!=SPEC_SHA or sha(parent)!=PARENT_SHA: raise Refusal('source-byte identity mismatch')
    spec=strict_json(raw.decode());cases={c['id']:c for c in spec['cases']}
    if any(t not in cases for t in TARGETS): raise Refusal('target missing')
    source_hashes={p.name:sha(p.read_bytes()) for p in sorted(root.iterdir()) if p.is_file()}
    out.mkdir(parents=True);queries=out/'queries';queries.mkdir()
    solver=Solver(queries,args.library)
    rows=[];summary={}
    for target in TARGETS:
        c=cases[target];hyp=c['hypotheses'];valid=[]
        for mask in range(1<<len(hyp)):
            kept=[i for i in range(len(hyp)) if mask&(1<<i)]
            hs=[hyp[i] for i in kept];name=target+'_'+str(mask)
            premise=solver.query(name+'_premises',c['variables'],hs)
            neg=solver.query(name+'_negation',c['variables'],hs+['(not '+c['conclusion']+')'])
            disposition=classify(premise['status'],neg['status'])
            if disposition=='VALID_ALGEBRA': valid.append(mask)
            rows.append({'target':target,'mask':mask,'kept_hypothesis_indices':kept,
                         'classification':disposition,'premises':premise,'negation':neg})
        minima=[m for m in valid if not any(v!=m and v&m==v for v in valid)]
        summary[target]={'subset_count':1<<len(hyp),'valid_subset_count':len(valid),
                         'minimal_sufficient_masks':minima,
                         'minimal_sufficient_hypotheses':[[hyp[i] for i in range(len(hyp)) if m&(1<<i)] for m in minima]}
    panel_rows=[]
    for c in panel(cases):
        premise=solver.query(c['id']+'_premises',c['variables'],c['hypotheses'])
        neg=solver.query(c['id']+'_negation',c['variables'],c['hypotheses']+['(not '+c['conclusion']+')'])
        disposition=classify(premise['status'],neg['status'])
        panel_rows.append({'id':c['id'],'expected':c['expected'],'classification':disposition,
                           'matched_expected':c['expected']==disposition,
                           'fixed_original_witness_baseline':original_witness_baseline(c),
                           'premises':premise,'negation':neg})
    false_rows=[r for r in panel_rows if r['expected']=='COUNTEREXAMPLE']
    report={'object':'P15-ASSUMPTION-PROBE-20260925-v1','utc':datetime.now(timezone.utc).isoformat(),
            'input_math_commit':INPUT_COMMIT,'spec_sha256':SPEC_SHA,'parent_proof_sha256':PARENT_SHA,
            'python':sys.version,'optimized':bool(sys.flags.optimize),'platform':platform.platform(),
            'z3_version':solver.version,'native_library_sha256':solver.library_hash,
            'source_hashes':source_hashes,'solver_queries':solver.query_count,
            'elapsed_seconds':time.monotonic()-solver.start,'assumption_results':summary,
            'assumption_rows':rows,'mutation_panel':panel_rows,
            'false_panel_count':len(false_rows),
            'fixed_witness_detected_false':sum(r['fixed_original_witness_baseline']=='COUNTEREXAMPLE' for r in false_rows),
            'fixed_witness_inapplicable_false':sum(r['fixed_original_witness_baseline']=='NOT_APPLICABLE' for r in false_rows),
            'solver_detected_false_with_rational_counterexample':sum(r['classification']=='COUNTEREXAMPLE' and r['negation']['rational_witness_checked'] for r in false_rows),
            'all_expected_matched':all(r['matched_expected'] for r in panel_rows),
            'inconclusive_count':sum(r['classification']=='INCONCLUSIVE' for r in rows+panel_rows),
            'scientific_effect':'NONE','promotion_permission':False,
            'experiment_disposition':'PENDING_DISTINCT_AGENT_REVIEW',
            'independent_translation_review':False,'independent_proof_recheck':False,
            'scope_warning':'Fixed small panel, not an estimate of field-wide reliability. Algebraic redundancy does not authorize removal of probability-model assumptions.'}
    if source_hashes!={p.name:sha(p.read_bytes()) for p in sorted(root.iterdir()) if p.is_file()}:
        raise Refusal('experiment source changed')
    (out/'REPORT.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ['assumption_results','solver_queries','elapsed_seconds','false_panel_count','fixed_witness_detected_false','fixed_witness_inapplicable_false','solver_detected_false_with_rational_counterexample','all_expected_matched','inconclusive_count']},indent=2))
    return 0 if report['all_expected_matched'] and not report['inconclusive_count'] else 1

if __name__=='__main__':
    try: sys.exit(main())
    except (Refusal,OSError,ValueError,KeyError) as e:
        print('FAIL CLOSED:',e,file=sys.stderr);sys.exit(1)
