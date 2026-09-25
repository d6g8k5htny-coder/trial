"""Read-only adversarial re-review of combined main PR98 head 6e3f774.

A green harness means the declared observations reproduced. It is not admission.
"""
from pathlib import Path
import argparse, hashlib, json, os, subprocess, sys, tempfile

SUBJECT = "6e3f774f7ccfb5b760730698b1211dbff55ead13"
ADAPTER_SHA256 = "360969dedf779ad3cb13a970a26be4466df77f0fce40fed461761bd805741792"

def git(root,*args,ok=True):
    p=subprocess.run(["git","-C",str(root),*args],capture_output=True,text=True,timeout=30)
    if ok and p.returncode: raise RuntimeError(p.stderr)
    return p

def write(path,obj,strict=True):
    path.parent.mkdir(parents=True,exist_ok=True)
    if isinstance(obj,str): path.write_text(obj)
    else: path.write_text(json.dumps(obj,indent=2)+"\n")

def base_graph(controlling=False):
    return {
      "as_of":"2026-09-25",
      "premises":{"P":{"status_register_note":"OPEN","source":{"path":"proof.md"}}},
      "claims":{
        "T":{"grade":"LIVE_ROOT_THEOREM" if controlling else "OPEN",
             "controlling":controlling,"depends_on":["P"],"source":{"path":"theorem.md"}},
        "U":{"grade":"OPEN","source":{"path":"unrelated.md"}}
      }
    }

def init_repo(root,g,cw=None,au=None):
    git(root,"init","-q");git(root,"config","user.email","review@example.invalid")
    git(root,"config","user.name","Combined review fixture")
    write(root/"claims/graph.json",g)
    write(root/"architecture/scientific_state/v1/ID_CROSSWALK.json",
          cw or {"rows":[{"main_claim_or_premise_id":"P","authority":"a"}]})
    write(root/"architecture/scientific_state/v1/AUTHORITY_MAP.json",
          au or {"authorities":{"a":{},"b":{}},"this_package":{"id":"adapter"}})
    for name in ("proof.md","theorem.md","unrelated.md","mirror.md"):
        (root/name).write_text("fixture "+name+" v1\n")
    git(root,"add",".");git(root,"commit","-qm","before")
    return git(root,"rev-parse","HEAD").stdout.strip()

def commit(root,label):
    git(root,"add",".");git(root,"commit","--allow-empty","-qm",label)
    return git(root,"rev-parse","HEAD").stdout.strip()

def run_cli(subject,root,before,after,optimized=False):
    env=os.environ.copy()
    env["CLAIMS_GATE_BEFORE_REF"]=before; env["CLAIMS_GATE_AFTER_REF"]=after
    flags=["-O"] if optimized else []
    cmd=[sys.executable,*flags,"-B","-S",str(subject/"tools/claims_gate_adapter.py"),
         "event-compare","--repo-root",str(root)]
    p=subprocess.run(cmd,env=env,capture_output=True,text=True,timeout=60)
    try: report=json.loads(p.stdout)
    except Exception: report={"_raw":p.stdout,"_stderr":p.stderr}
    return p.returncode, report

def impacted(r): return set((r.get("reverse_impact") or {}).get("impacted") or [])

def case_owner_propagation(subject,mode):
    with tempfile.TemporaryDirectory() as d:
        root=Path(d); g=base_graph(False); before=init_repo(root,g)
        p=root/"architecture/scientific_state/v1/ID_CROSSWALK.json"
        cw=json.loads(p.read_text()); cw["rows"][0]["authority"]="b"; write(p,cw)
        after=commit(root,"owner drift")
        rc,r=run_cli(subject,root,before,after,mode)
        return {"rc":rc,"impacted":sorted(impacted(r)),
                "authority_owner_seeds":r.get("authority_owner_seeds"),
                "transition_ok":r.get("transition_ok"),
                "defect": rc==0 and "P" in impacted(r) and "T" not in impacted(r)}

def case_owner_controlling_escape(subject,mode):
    with tempfile.TemporaryDirectory() as d:
        root=Path(d); g=base_graph(True); before=init_repo(root,g)
        p=root/"architecture/scientific_state/v1/ID_CROSSWALK.json"
        cw=json.loads(p.read_text()); cw["rows"][0]["authority"]="b"; write(p,cw)
        after=commit(root,"owner drift controlling")
        rc,r=run_cli(subject,root,before,after,mode)
        return {"rc":rc,"impacted":sorted(impacted(r)),
                "controlling_impacted":r.get("controlling_impacted"),
                "transition_ok":r.get("transition_ok"),
                "defect": rc==0 and r.get("transition_ok") is True and "T" not in impacted(r)}

def case_malformed_old_crosswalk(subject,mode):
    with tempfile.TemporaryDirectory() as d:
        root=Path(d); g=base_graph(False); before=init_repo(root,g)
        # Amend BEFORE commit itself by creating a fresh malformed first commit.
        # Reset and rebuild from scratch so malformed JSON is historical input.
        git(root,"reset","--hard",before)
        p=root/"architecture/scientific_state/v1/ID_CROSSWALK.json"
        p.write_text('{"rows": [], "rows": [{"main_claim_or_premise_id":"P","authority":"a"}]}\n')
        git(root,"add",".");git(root,"commit","-qm","malformed old crosswalk")
        malformed=git(root,"rev-parse","HEAD").stdout.strip()
        write(p,{"rows":[{"main_claim_or_premise_id":"P","authority":"a"}]})
        after=commit(root,"valid new crosswalk")
        rc,r=run_cli(subject,root,malformed,after,mode)
        return {"rc":rc,"error":r.get("error"),"old_identity":r.get("old_crosswalk_identity"),
                "defect": rc==0 and (r.get("old_crosswalk_identity") or {}).get("absent_old_schema") is True}

def case_malformed_old_authority(subject,mode):
    with tempfile.TemporaryDirectory() as d:
        root=Path(d); g=base_graph(False); before=init_repo(root,g)
        p=root/"architecture/scientific_state/v1/AUTHORITY_MAP.json"
        p.write_text('{"authorities":{"a":{}}, "authorities":{"a":{},"b":{}}}\n')
        git(root,"add",".");git(root,"commit","-qm","malformed old authority")
        malformed=git(root,"rev-parse","HEAD").stdout.strip()
        write(p,{"authorities":{"a":{},"b":{}},"this_package":{"id":"adapter"}})
        after=commit(root,"valid new authority")
        rc,r=run_cli(subject,root,malformed,after,mode)
        return {"rc":rc,"error":r.get("error"),"old_identity":r.get("old_authority_identity"),
                "pass": rc!=0 and bool(r.get("error"))}

def case_cross_repo_binding(subject,mode):
    with tempfile.TemporaryDirectory() as d:
        root=Path(d)
        g=base_graph(False)
        g["premises"]["P"].pop("source")
        g["premises"]["P"]["source_bindings"]=[
          {"repo":"different-owner/different-repo","path":"proof.md",
           "commit":"f"*40,"sha256":"0"*64}]
        before=init_repo(root,g)
        (root/"proof.md").write_text("changed local file that is NOT the declared repo\n")
        after=commit(root,"local collision")
        rc,r=run_cli(subject,root,before,after,mode)
        src=(r.get("new_sources") or {}).get("P") or {}
        bindings=src.get("bindings") or []
        local_blob=any(b.get("kind")=="blob" and b.get("path")=="proof.md" for b in bindings)
        return {"rc":rc,"impacted":sorted(impacted(r)),"source":src,
                "defect": rc==0 and local_blob and "P" in impacted(r)}

def case_strict_claims(subject,mode):
    with tempfile.TemporaryDirectory() as d:
        root=Path(d); g=base_graph(False); before=init_repo(root,g)
        p=root/"claims/graph.json"
        s=json.dumps(g).replace('"depends_on": ["P"]','"depends_on": ["P"], "depends_on": []')
        p.write_text(s+"\n"); after=commit(root,"dup claims")
        rc,r=run_cli(subject,root,before,after,mode)
        return {"rc":rc,"error":r.get("error"),"pass":rc!=0 and "duplicate JSON key" in str(r.get("error"))}

def case_source_binding_control(subject,mode):
    with tempfile.TemporaryDirectory() as d:
        root=Path(d);g=base_graph(False)
        g["premises"]["P"].pop("source")
        g["premises"]["P"]["source_bindings"]=[{"repo":"d6g8k5htny-coder/main","path":"proof.md"}]
        before=init_repo(root,g); (root/"proof.md").write_text("legit local change\n"); after=commit(root,"source binding")
        rc,r=run_cli(subject,root,before,after,mode)
        return {"rc":rc,"impacted":sorted(impacted(r)),"pass":rc==0 and {"P","T"} <= impacted(r)}

CASES=[
 ("owner_propagation",case_owner_propagation),
 ("owner_controlling_escape",case_owner_controlling_escape),
 ("malformed_old_crosswalk",case_malformed_old_crosswalk),
 ("malformed_old_authority",case_malformed_old_authority),
 ("cross_repo_binding",case_cross_repo_binding),
 ("strict_claims",case_strict_claims),
 ("source_binding_control",case_source_binding_control),
]

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--subject-root",type=Path,required=True);ap.add_argument("--output",type=Path,required=True)
    a=ap.parse_args();subject=a.subject_root.resolve();out=a.output.resolve();out.mkdir(parents=True,exist_ok=False)
    b=(subject/"tools/claims_gate_adapter.py").read_bytes()
    if hashlib.sha256(b).hexdigest()!=ADAPTER_SHA256: raise SystemExit("adapter SHA mismatch")
    rows=[]
    for mode in (False,True):
        mn="optimized" if mode else "normal"
        for name,fn in CASES:
            obs=fn(subject,mode);obs.update(case=name,mode=mn);rows.append(obs)
            (out/f"{mn}_{name}.json").write_text(json.dumps(obs,indent=2,sort_keys=True)+"\n")
    defects=[r for r in rows if r.get("defect")]
    controls=[r for r in rows if "pass" in r]
    report={"subject":SUBJECT,"adapter_sha256":ADAPTER_SHA256,"python":sys.version,
            "observations":rows,"defects_reproduced":len(defects),
            "defect_cases":sorted({r["case"] for r in defects}),
            "controls_all_pass":all(r["pass"] for r in controls),
            "interpretation":"Defect flags are adverse findings, not acceptance."}
    (out/"REPORT.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps(report,indent=2,sort_keys=True))
    # Green review harness requires controls to pass AND the suspected defects to reproduce in both modes.
    expected={"owner_propagation","owner_controlling_escape","malformed_old_crosswalk","cross_repo_binding"}
    got={x for x in expected if sum(1 for r in defects if r["case"]==x)==2}
    return 0 if report["controls_all_pass"] and got==expected else 1

if __name__=="__main__": raise SystemExit(main())
