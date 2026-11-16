import re
LINE = re.compile(r"^(Team|Formation|Strength|Weakness|Key player|Set piece):\s*(.+?)\.?$")
def parse_report(doc_id, text):
    r = dict(doc=doc_id, team=None, formation=None, strengths=[], weaknesses=[], key_players=[], set_pieces=[])
    for line in text.splitlines():
        m = LINE.match(line.strip())
        if not m: continue
        k, v = m.groups(); parts = [p.strip() for p in v.split("|")]
        if k == "Team": r["team"] = v
        elif k == "Formation": r["formation"] = {"shape": parts[0], "note": parts[1] if len(parts) > 1 else ""}
        elif k == "Strength": r["strengths"].append(v)
        elif k == "Weakness": r["weaknesses"].append(v)
        elif k == "Key player":
            r["key_players"].append(dict(name=parts[0], pos=parts[1], attr=parts[2], rating=int(parts[3]), note=parts[4]))
        elif k == "Set piece": r["set_pieces"].append(dict(kind=parts[0], pattern=parts[1], detail=parts[2]))
    return r
class ReportParserAgent:
    name = "ReportParserAgent"
    def __init__(self, corpus): self.corpus = corpus   # dict doc_id -> text
    def run(self, board):
        for doc_id, _ in board.docs:
            p = parse_report(doc_id, self.corpus[doc_id]); board.parsed[doc_id] = p
            if p["formation"]: board.post("formation", f"{p['formation']['shape']} - {p['formation']['note']}", [doc_id], self.name)
            for s in p["strengths"]: board.post("strength", s, [doc_id], self.name)
            for w in p["weaknesses"]: board.post("weakness", w, [doc_id], self.name)
