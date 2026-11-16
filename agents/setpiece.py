from collections import defaultdict
class SetPieceAgent:
    """Finds patterns that repeat across reports."""
    name = "SetPieceAgent"
    def run(self, board):
        groups = defaultdict(list)
        for doc_id, p in sorted(board.parsed.items()):
            for sp in p["set_pieces"]: groups[(sp["kind"], sp["pattern"])].append((doc_id, sp["detail"]))
        for (kind, pattern), hits in groups.items():
            docs = sorted({d for d, _ in hits}); rep = len(docs) >= 2
            claim = f"{kind} - {pattern}: {hits[0][1]}" + (f" (repeated in {len(docs)} reports)" if rep else "")
            board.post("set_piece", claim, docs, self.name, repeated=rep)
