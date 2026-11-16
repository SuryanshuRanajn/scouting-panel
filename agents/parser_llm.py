"""LLM Report Parser: reads FREE-TEXT scouting reports and returns the same structure as the rule parser."""
import hashlib, json, os, time
import llm, tools
CACHE = "data/parse_cache.json"
PATTERNS = ["near post","far post","short routine","short corner","long throw","inswinger to far post",
            "wall-and-run","decoy runs","direct shot","edge of the box","penalty spot","other"]
SYSTEM = f"""You extract structured data from a football scouting report. Return ONLY valid JSON, no commentary.
Schema:
{{"team": str,
 "formation": {{"shape": str, "note": str}},
 "strengths": [str], "weaknesses": [str],
 "key_players": [{{"name": str, "pos": str, "attr": str, "rating": int, "note": str}}],
 "set_pieces": [{{"kind": str, "pattern": str, "detail": str}}]}}
Rules:
- Copy the report's own wording for strengths, weaknesses, notes and details. Do not invent facts.
- shape looks like "4-3-3". pos is one of LW, RW, LWB, RWB, ST, CB, CAM, CM, DM, LB, RB.
- attr is one of pace, aerial, dribbling, passing, finishing, tackling. rating is the number given in the report.
- kind is one of corner, free kick, throw-in, penalty.
- pattern MUST be one label from this list: {PATTERNS}. Use "other" if none fits.
- Use [] for anything the report does not mention."""
def _load():
    return json.load(open(CACHE)) if os.path.exists(CACHE) else {}
def _clean(r, doc_id):
    ok_pos, ok_attr = set(tools.COUNTER), set(tools.ATTR_COUNTER)
    r.setdefault("strengths", []); r.setdefault("weaknesses", [])
    r["doc"] = doc_id
    r["key_players"] = [k for k in r.get("key_players", []) if k.get("pos") in ok_pos and k.get("attr") in ok_attr]
    for k in r["key_players"]: k["rating"] = int(k.get("rating", 0)); k.setdefault("note", "")
    r["set_pieces"] = [s for s in r.get("set_pieces", []) if s.get("pattern") in PATTERNS]
    if not r.get("formation"): r["formation"] = None
    return r
class LLMReportParserAgent:
    name = "LLMReportParserAgent"
    def __init__(self, corpus): self.corpus = corpus
    def run(self, board):
        cache = _load()
        for doc_id, _ in board.docs:
            text = self.corpus[doc_id]; key = f"{llm.MODEL}:{doc_id}:{hashlib.md5(text.encode()).hexdigest()}"
            if key not in cache:
                print(f"   [LLM] parsing {doc_id} ...")
                cache[key] = llm.ask_json(SYSTEM, f"Report {doc_id}:\n{text}")
                json.dump(cache, open(CACHE, "w"), indent=1); time.sleep(3)   # be gentle with free-tier limits
            p = _clean(dict(cache[key]), doc_id); board.parsed[doc_id] = p
            if p["formation"]: board.post("formation", f"{p['formation']['shape']} - {p['formation']['note']}", [doc_id], self.name)
            for s in p["strengths"]: board.post("strength", s, [doc_id], self.name)
            for w in p["weaknesses"]: board.post("weakness", w, [doc_id], self.name)
