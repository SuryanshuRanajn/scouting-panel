"""Logic behind the Streamlit app (kept separate from the UI so it can be tested without Streamlit)."""
import hashlib, json, os
import llm as llm_mod
from agents.retrieval import OppositionRetrievalAgent
from pipeline import run_panel

class MissingKey(Exception): pass
_RET = {}

def ensure_data():
    if not os.path.exists("data/stats.json"):
        import data_build; data_build.build()
    if not os.path.isdir("data/corpus_prose"):
        import data_build_prose; data_build_prose.main()

def teams(): return list(json.load(open("data/team_docs.json")))
def corpus_dir(use_llm): return "data/corpus_prose" if use_llm else "data/corpus"
def retriever(use_llm):
    if use_llm not in _RET: _RET[use_llm] = OppositionRetrievalAgent(corpus_dir(use_llm))
    return _RET[use_llm]

def _uncached(doc_ids, ret):
    cache = json.load(open("data/parse_cache.json")) if os.path.exists("data/parse_cache.json") else {}
    return [d for d in doc_ids
            if f"{llm_mod.MODEL}:{d}:{hashlib.md5(ret.docs[d].encode()).hexdigest()}" not in cache]

def run_team(team, use_llm):
    ret = retriever(use_llm)
    if use_llm:
        miss = _uncached([d for d, _ in ret.retrieve(team)], ret)
        if miss and not os.environ.get("GEMINI_API_KEY"):
            raise MissingKey(f"{len(miss)} report(s) are not cached ({', '.join(miss)}) and no Gemini API key is set.")
    out, board = run_panel(team, ret, llm=use_llm, corpus_dir=corpus_dir(use_llm))
    docs = [(d, round(s, 3), ret.docs[d]) for d, s in board.docs]
    return dict(team=team, llm=use_llm, out=out, board=board, docs=docs)

def evaluate(use_llm):
    truth = json.load(open("data/ground_truth.json")); tdocs = json.load(open("data/team_docs.json"))
    ret = retriever(use_llm)
    if use_llm and not os.environ.get("GEMINI_API_KEY"):
        miss = _uncached(list(ret.docs), ret)
        if miss: raise MissingKey(f"{len(miss)} report(s) are not cached and no Gemini API key is set.")
    rows, found, correct, leak, cites = [], 0, 0, 0, 0
    for team in tdocs:
        out, _ = run_panel(team, ret, llm=use_llm, corpus_dir=corpus_dir(use_llm))
        for f in [t for t in truth if t["team"] == team]:
            hit = [p for p in out["plan"] if f["phrase"].lower() in p["text"].lower()]
            ok_f = bool(hit); ok_s = any(f["source"] in p["sources"] for p in hit)
            found += ok_f; correct += ok_s
            rows.append({"Team": team, "Fact type": f["type"], "Seeded phrase": f["phrase"], "Expected source": f["source"],
                         "In plan": "yes" if ok_f else "NO", "Correct source": "yes" if ok_s else "NO"})
        for p in out["plan"]:
            cites += len(p["sources"]); leak += sum(s not in tdocs[team] for s in p["sources"])
    return dict(rows=rows, found=found, correct=correct, n=len(truth), leak=leak, cites=cites)

def plan_text(res):
    o = res["out"]; L = [f"MATCH PLAN vs {res['team']}", ""]
    for p in o["plan"]: L.append(f"{p['rank']:>2}. {p['text']}  [{', '.join(p['sources'])}]")
    return "\n".join(L)