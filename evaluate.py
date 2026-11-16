import json, sys
from pipeline import run_panel
from agents.retrieval import OppositionRetrievalAgent
use_llm = "--llm" in sys.argv; cdir = "data/corpus_prose" if use_llm else "data/corpus"
truth = json.load(open("data/ground_truth.json")); docs = json.load(open("data/team_docs.json"))
ret = OppositionRetrievalAgent(cdir); found = correct = leak = total_cites = 0; rows = []
print(f"Mode: {'LLM parser on free-text reports' if use_llm else 'rule parser on fixed-format reports'}\n")
for team in docs:
    out, _ = run_panel(team, ret, llm=use_llm)
    for f in [t for t in truth if t["team"] == team]:
        hit = [p for p in out["plan"] if f["phrase"].lower() in p["text"].lower()]
        ok_f = bool(hit); ok_s = any(f["source"] in p["sources"] for p in hit)
        found += ok_f; correct += ok_s; rows.append((team, f["type"], f["phrase"], f["source"], ok_f, ok_s))
    for p in out["plan"]:
        total_cites += len(p["sources"]); leak += sum(s not in docs[team] for s in p["sources"])
n = len(truth)
print(f"{'Team':<11}{'Fact type':<12}{'Seeded phrase':<30}{'Src':<8}Found  CorrectSrc")
for r in rows: print(f"{r[0]:<11}{r[1]:<12}{r[2]:<30}{r[3]:<8}{str(r[4]):<7}{r[5]}")
print(f"\nSeeded facts in plan:            {found}/{n} ({found/n:.0%})")
print(f"Seeded facts with correct source: {correct}/{n} ({correct/n:.0%})")
print(f"Citations pointing to another team's report: {leak}/{total_cites}")
