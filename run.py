import sys
from pipeline import run_panel
args = [a for a in sys.argv[1:] if not a.startswith("--")]; use_llm = "--llm" in sys.argv
team = args[0] if args else "Ashford"
out, board = run_panel(team, llm=use_llm, corpus_dir="data/corpus_prose" if use_llm else "data/corpus")
print(f"=== STRATEGY BRIEF vs {team} ({'LLM parser, prose reports' if use_llm else 'rule parser'}) ===")
for title, key in [("Strengths","strengths"),("Weaknesses","weaknesses"),("Key matchups","key_matchups")]:
    print(f"\n{title}:"); [print(f"  - {c}  [{', '.join(s)}]") for c, s in out[key]]
print("\nRanked game plan:")
for p in out["plan"]: print(f"  {p['rank']:>2}. {p['text']}  [{', '.join(p['sources'])}]")
print("\nBoard log:"); [print("  ", l) for l in board.log]
