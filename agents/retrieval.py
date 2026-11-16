import glob, math, os, re
from collections import Counter
TOK = re.compile(r"[a-z0-9\-]+")
class OppositionRetrievalAgent:
    """RAG over the scouting-report set (document-level TF-IDF; swap for embeddings if you like)."""
    name = "OppositionRetrievalAgent"
    def __init__(self, corpus_dir="data/corpus"):
        self.docs = {os.path.basename(p)[:-4]: open(p).read() for p in sorted(glob.glob(f"{corpus_dir}/*.txt"))}
        self.tf = {d: Counter(TOK.findall(t.lower())) for d, t in self.docs.items()}
        df = Counter(w for c in self.tf.values() for w in c); N = len(self.docs)
        self.idf = {w: math.log((1+N)/(1+n))+1 for w, n in df.items()}
        self.norm = {d: math.sqrt(sum((c[w]*self.idf[w])**2 for w in c)) for d, c in self.tf.items()}
    def retrieve(self, query, k=5):
        q = Counter(TOK.findall(query.lower())); out = []
        for d, c in self.tf.items():
            dot = sum(q[w]*self.idf.get(w,0)*c[w]*self.idf[w] for w in q if w in c)
            if dot > 0: out.append((d, dot/self.norm[d]))
        return sorted(out, key=lambda x: -x[1])[:k]
    def run(self, board):
        board.docs = self.retrieve(board.team)
        board.log.append(f"[{self.name}] retrieved {[d for d,_ in board.docs]}")
        return board.docs
