"""Writes FREE-TEXT versions of the same 12 reports (same IDs, same seeded facts) to data/corpus_prose/."""
import os
from data_build import T, EXTRA
POS = {"LW":"left winger","RW":"right winger","ST":"striker","CAM":"attacking midfielder","CB":"centre-back",
       "RWB":"right wing-back","LWB":"left wing-back","DM":"holding midfielder","CM":"central midfielder","LB":"left-back","RB":"right-back"}
def main():
    os.makedirs("data/corpus_prose", exist_ok=True); n = 0
    for t in T:
        n += 1; did = f"RPT-{n:02d}"; s1, s2 = t["st"]; w1, w2 = t["wk"]; k, p, d = t["sp"]
        kp = " ".join(f"{nm} plays as {POS[pos]} ({pos}) and is dangerous because of his {a} - rated {r} in our data; {note}."
                      for nm, pos, a, r, note in t["kp"])
        txt = (f"Scouting report {did}. We went to watch {t['team']} and they started in a {t['form'][0]}; {t['form'][1]}. "
               f"Strengths worth respecting: {s1}, and also {s2}. "
               f"Where we can hurt them, we noted that {w1}; additionally, {w2}. "
               f"Individually, keep an eye on this: {kp} "
               f"From dead balls, their {k} routine stood out: {d}.\n")
        open(f"data/corpus_prose/{did}.txt", "w").write(txt)
    for tm, wk in EXTRA.items():
        n += 1; did = f"RPT-{n:02d}"; t = next(x for x in T if x["team"] == tm); k, p, d = t["sp"]
        txt = (f"Scouting report {did} - an earlier season fixture against {tm}. They played the same {t['form'][0]} shape. "
               f"Again {t['st'][0]} was their main asset, while {wk}. On set pieces, {k}s again followed the pattern: {d}.\n")
        open(f"data/corpus_prose/{did}.txt", "w").write(txt)
    print(f"wrote {n} prose reports to data/corpus_prose/")
if __name__ == "__main__": main()
