"""Independent final boundary review of main PR98 gate successor 2d3374c (E6 successor).

Green means the listed safety properties reproduced on the exact immutable source.
It is engineering evidence only, never mathematical/scientific acceptance.
"""
from pathlib import Path
import argparse, hashlib, json, os, subprocess, sys, tempfile

SUBJECT="2d3374c5827650f5c9b462a77b29e17b998dbd96"
ADAPTER_SHA256="3ebcbb8a7f9822763bc6e75ac2402741144410d5d0dfdc636d34216cd0665420"

def git(root,*args,ok=True):
    p=subprocess.run(["git","-C",str(root),*args],capture_output=True,text=True,timeout=30)
    if ok and p.returncode:
        raise RuntimeError(p.stderr)
    return p

def write(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(obj if isinstance(obj,str) else json.dumps(obj,indent=2)+"\n")

def graph(*,controlling_t=False,controlling_p=False):
    p={"status_register_note":"CONTROLLING" if controlling_p else "OPEN",
       "source":{"path":"proof.md"}}
    return {"as_of":"2026-09-25","premises":{"P":p},"claims":{
      "T":{"grade":"LIVE_ROOT_THEOREM" if controlling_t else "OPEN",
           "controlling":controlling_t,"depends_on":["P"],"source":{"path":"theorem.md"}},
      "U":{"grade":"OPEN","source":{"path":"unrelated.md"}}}}

def init(root,g,cw=None,au=None,files=None):
    git(root,"init","-q");git(root,"config","user.email","review@example.invalid")
    git(root,"config","user.name","Final gate review fixture")
    write(root/"claims/graph.json",g)
    write(root/"architecture/scientific_state/v1/ID_CROSSWALK.json",
          cw or {"rows":[{"main_claim_or_premise_id":"P","authority":"a"}]})
    write(root/"architecture/scientific_state/v1/AUTHORITY_MAP.json",
          au or {"authorities":{"a":{},"b":{}},"this_package":{"id":"adapter"}})
    base={"proof.md":"proof v1\n","theorem.md":"theorem v1\n","unrelated.md":"unrelated v1\n",
          "extra.md":"extra v1\n","master.md":"master v1\n"}
    if files: base.update(files)
    for name,body in base.items():
        p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(body)
    git(root,"add",".");git(root,"commit","-qm","before")
    return git(root,"rev-parse","HEAD").stdout.strip()

def commit(root,label):
    git(root,"add",".");git(root,"commit","--allow-empty","-qm",label)
    return git(root,"rev-parse","HEAD").stdout.strip()

def run(subject,root,before,after,opt):
    env=os.environ.copy();env["CLAIMS_GATE_BEFORE_REF"]=before;env["CLAIMS_GATE_AFTER_REF"]=after
    flags=["-O"] if opt else []
    p=subprocess.run([sys.executable,*flags,"-B","-S",str(subject/"tools/claims_gate_adapter.py"),
                      "event-compare","--repo-root",str(root)],
                     env=env,capture_output=True,text=True,timeout=60)
    try:r=json.loads(p.stdout)
    except Exception:r={"_raw":p.stdout,"_stderr":p.stderr}
    return p.returncode,r

def imp(r): return set((r.get("reverse_impact") or {}).get("impacted") or [])

def bind(path,**kw):
    x={"repo":"d6g8k5htny-coder/main","path":path}
    x.update(kw);return x

def fresh_expected(body:bytes): return hashlib.sha256(body).hexdigest()

def c_owner_propagation(subject,opt):
    with tempfile.TemporaryDirectory() as d:
        root=Path(d);g=graph();before=init(root,g)
        p=root/"architecture/scientific_state/v1/ID_CROSSWALK.json";cw=json.loads(p.read_text())
        cw["rows"][0]["authority"]="b";write(p,cw);after=commit(root,"owner")
        rc,r=run(subject,root,before,after,opt)
        return rc==0 and {"P","T"}<=imp(r) and "P" in (r.get("authority_owner_seeds") or [])

def c_owner_controlling(subject,opt):
    with tempfile.TemporaryDirectory() as d:
        root=Path(d);g=graph(controlling_t=True);before=init(root,g)
        p=root/"architecture/scientific_state/v1/ID_CROSSWALK.json";cw=json.loads(p.read_text())
        cw["rows"][0]["authority"]="b";write(p,cw);after=commit(root,"owner controlling")
        rc,r=run(subject,root,before,after,opt)
        return rc!=0 and r.get("transition_ok") is False and {"P","T"}<=imp(r) and "T" in (r.get("controlling_impacted") or [])

def c_malformed_old_crosswalk(subject,opt):
    with tempfile.TemporaryDirectory() as d:
        root=Path(d);g=graph();init(root,g)
        p=root/"architecture/scientific_state/v1/ID_CROSSWALK.json"
        p.write_text('{"rows":[],"rows":[{"main_claim_or_premise_id":"P","authority":"a"}]}\n')
        malformed=commit(root,"malformed old");write(p,{"rows":[{"main_claim_or_premise_id":"P","authority":"a"}]})
        after=commit(root,"valid new");rc,r=run(subject,root,malformed,after,opt)
        return rc!=0 and "duplicate JSON key" in str(r.get("error"))

def c_cross_repo_refusal(subject,opt):
    with tempfile.TemporaryDirectory() as d:
        root=Path(d);g=graph(controlling_p=True);g["premises"]["P"].pop("source")
        g["premises"]["P"]["source_bindings"]=[{"repo":"other/example","path":"proof.md",
            "commit":"f"*40,"sha256":"0"*64}]
        before=init(root,g);(root/"proof.md").write_text("unrelated local collision\n");after=commit(root,"local collision")
        rc,r=run(subject,root,before,after,opt);src=(r.get("new_sources") or {}).get("P") or {}
        binds=src.get("bindings") or []
        return rc!=0 and r.get("transition_ok") is False and any(b.get("kind")=="unsupported_cross_repo" for b in binds)

def c_duplicate_claims(subject,opt):
    with tempfile.TemporaryDirectory() as d:
        root=Path(d);g=graph();before=init(root,g);p=root/"claims/graph.json"
        s=json.dumps(g).replace('"depends_on": ["P"]','"depends_on": ["P"], "depends_on": []')
        p.write_text(s+"\n");after=commit(root,"dup");rc,r=run(subject,root,before,after,opt)
        return rc!=0 and "duplicate JSON key" in str(r.get("error"))

def c_second_binding(subject,opt):
    with tempfile.TemporaryDirectory() as d:
        root=Path(d);g=graph(controlling_t=True);g["premises"]["P"].pop("source")
        g["premises"]["P"]["source_bindings"]=[bind("proof.md"),bind("extra.md")]
        before=init(root,g);(root/"extra.md").write_text("extra changed only\n");after=commit(root,"second source")
        rc,r=run(subject,root,before,after,opt)
        return rc!=0 and {"P","T"}<=imp(r) and "T" in (r.get("controlling_impacted") or [])

def frozen_graph(*,freshness="external_sync_obligation",informational=False):
    body=b"scientific body\n";sha=fresh_expected(body)
    g=graph(controlling_p=True);g["premises"]["P"].pop("source")
    bindings=[bind("proof.md",role="scientific_object",extraction_rule="frozen_body",
                   expected_sha256=sha,mirror_freshness=freshness,source_drive_id="fixture-drive")]
    if informational:
        bindings.append(bind("master.md",role="informational_carrier",extraction_rule="whole_file",
                             mirror_freshness="external_sync_obligation"))
    g["premises"]["P"]["source_bindings"]=bindings
    wrapper="header\nBEGIN_FROZEN_BODY\nscientific body\nEND_FROZEN_BODY\nfooter v1\n"
    return g,wrapper

def c_wrapper_only(subject,opt):
    with tempfile.TemporaryDirectory() as d:
        root=Path(d);g,wrapper=frozen_graph();before=init(root,g,files={"proof.md":wrapper})
        (root/"proof.md").write_text(wrapper.replace("footer v1","footer v2"));after=commit(root,"wrapper only")
        rc,r=run(subject,root,before,after,opt)
        return rc==0 and r.get("transition_ok") is True and "P" not in imp(r)

def c_body_drift(subject,opt):
    with tempfile.TemporaryDirectory() as d:
        root=Path(d);g,wrapper=frozen_graph();before=init(root,g,files={"proof.md":wrapper})
        (root/"proof.md").write_text(wrapper.replace("scientific body","scientific CHANGED"));after=commit(root,"body drift")
        rc,r=run(subject,root,before,after,opt);src=(r.get("new_sources") or {}).get("P") or {}
        return rc!=0 and r.get("transition_ok") is False and src.get("kind")=="object_hash_mismatch"

def c_informational_noise(subject,opt):
    with tempfile.TemporaryDirectory() as d:
        root=Path(d);g,wrapper=frozen_graph(informational=True)
        before=init(root,g,files={"proof.md":wrapper,"master.md":"master carrier v1\n"})
        (root/"master.md").write_text("master unrelated edit\n");after=commit(root,"master noise")
        rc,r=run(subject,root,before,after,opt)
        return rc==0 and r.get("transition_ok") is True and "P" not in imp(r)

def c_stale_freshness(subject,opt):
    with tempfile.TemporaryDirectory() as d:
        root=Path(d);g,wrapper=frozen_graph(freshness="stale");before=init(root,g,files={"proof.md":wrapper})
        after=commit(root,"noop");rc,r=run(subject,root,before,after,opt)
        return rc!=0 and r.get("transition_ok") is False and "P" in (r.get("unresolved_controlling_sources") or [])

def c_precision_upgrade(subject,opt):
    with tempfile.TemporaryDirectory() as d:
        root=Path(d);g=graph(controlling_p=True);g["premises"]["P"].pop("source")
        g["premises"]["P"]["source_bindings"]=[bind("proof.md")]
        before=init(root,g)
        body=(root/"proof.md").read_bytes();g2=json.loads((root/"claims/graph.json").read_text())
        g2["premises"]["P"]["source_bindings"]=[bind("proof.md",role="scientific_object",
             extraction_rule="whole_file",expected_sha256=fresh_expected(body),
             mirror_freshness="external_sync_obligation")]
        write(root/"claims/graph.json",g2);after=commit(root,"precision upgrade");rc,r=run(subject,root,before,after,opt)
        return rc==0 and r.get("transition_ok") is True and "P" in (r.get("coverage_repairs") or [])


def c_precision_upgrade_semantic_change(subject,opt):
    """E6: a binding-precision migration cannot erase simultaneous claim semantics."""
    with tempfile.TemporaryDirectory() as d:
        root=Path(d);g=graph(controlling_t=True)
        g["claims"]["T"].pop("source")
        g["claims"]["T"]["source_bindings"]=[bind("theorem.md")]
        g["claims"]["T"]["statement"]="original theorem statement"
        before=init(root,g)
        body=(root/"theorem.md").read_bytes()
        g2=json.loads((root/"claims/graph.json").read_text())
        g2["claims"]["T"]["statement"]="SEMANTICALLY CHANGED theorem statement"
        g2["claims"]["T"]["source_bindings"]=[bind(
            "theorem.md",role="scientific_object",extraction_rule="whole_file",
            expected_sha256=fresh_expected(body),
            mirror_freshness="external_sync_obligation")]
        write(root/"claims/graph.json",g2)
        after=commit(root,"precision upgrade plus semantics")
        rc,r=run(subject,root,before,after,opt)
        return (rc!=0 and r.get("transition_ok") is False
                and "T" in (r.get("controlling_impacted") or [])
                and "T" not in (r.get("coverage_repairs") or []))

CASES=[
 ("owner_propagation",c_owner_propagation),("owner_controlling_refusal",c_owner_controlling),
 ("malformed_old_crosswalk",c_malformed_old_crosswalk),("cross_repo_refusal",c_cross_repo_refusal),
 ("duplicate_claims",c_duplicate_claims),("second_binding_drift",c_second_binding),
 ("wrapper_only_noise",c_wrapper_only),("scientific_body_drift",c_body_drift),
 ("informational_carrier_noise",c_informational_noise),("stale_freshness",c_stale_freshness),
 ("precision_upgrade",c_precision_upgrade),
 ("precision_upgrade_semantic_change",c_precision_upgrade_semantic_change),
]

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--subject-root",type=Path,required=True);ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args();subject=a.subject_root.resolve();out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    raw=(subject/"tools/claims_gate_adapter.py").read_bytes()
    if hashlib.sha256(raw).hexdigest()!=ADAPTER_SHA256: raise SystemExit("adapter SHA mismatch")
    rows=[]
    for opt in (False,True):
        mode="optimized" if opt else "normal"
        for name,fn in CASES:
            ok=bool(fn(subject,opt));row={"mode":mode,"case":name,"pass":ok};rows.append(row)
            (out/f"{mode}_{name}.json").write_text(json.dumps(row,indent=2)+"\n")
    tip=subprocess.run([sys.executable,"-B","-S",str(subject/"tools/claims_gate_adapter.py"),"tip-health"],
                       cwd=subject,capture_output=True,text=True,timeout=60)
    tip_ok=tip.returncode==0
    (out/"tip-health.log").write_text(tip.stdout+tip.stderr)
    result={"subject":SUBJECT,"adapter_sha256":ADAPTER_SHA256,"python":sys.version,
            "cases":rows,"all_cases_pass":all(r["pass"] for r in rows),
            "tip_health_exit_zero":tip_ok,"scientific_effect":"NONE",
            "scope":"F1-F5/E engineering boundary only; no mathematical acceptance or positive promotion authority."}
    result["passed"]=result["all_cases_pass"] and tip_ok
    (out/"REPORT.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))
    return 0 if result["passed"] else 1

if __name__=="__main__": raise SystemExit(main())
