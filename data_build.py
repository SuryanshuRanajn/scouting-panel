"""Generates the synthetic corpus, seeded-fact ground truth and mock stats files."""
import json, os
HOME = {  # our team (Lakeside): pos -> (name, ratings)
 "RB": ("Arjun Rao",   dict(pace=74, aerial=70, tackling=80, dribbling=65, passing=70, finishing=40)),
 "LB": ("Imran Khan",  dict(pace=82, aerial=68, tackling=76, dribbling=70, passing=72, finishing=45)),
 "CB": ("Dev Mehta",   dict(pace=66, aerial=86, tackling=84, dribbling=50, passing=65, finishing=35)),
 "DM": ("Karan Bose",  dict(pace=68, aerial=74, tackling=83, dribbling=62, passing=79, finishing=50)),
 "CAM":("Vikram Joshi",dict(pace=75, aerial=60, tackling=60, dribbling=85, passing=87, finishing=72)),
 "RW": ("Sahil Verma", dict(pace=88, aerial=55, tackling=50, dribbling=84, passing=74, finishing=70)),
 "LW": ("Yash Thakur", dict(pace=85, aerial=52, tackling=48, dribbling=82, passing=72, finishing=71)),
 "ST": ("Rohit Nair",  dict(pace=80, aerial=78, tackling=40, dribbling=74, passing=65, finishing=86)),
}
# opp team: formation, strengths, weaknesses (first is seeded), key players (first seeded), set piece (seeded)
T = [
 dict(team="Ashford", form=("4-3-3","drops into a 4-5-1 mid block without the ball"),
  st=["fast counter-attacks through the wide forwards","high pressing after losing the ball"],
  wk=["centre-backs are slow on the turn against balls in behind","right-back leaves space when the team presses high"],
  kp=[("Tomas Reyes","LW","pace",90,"cuts inside onto his right foot"),("Sam Okoye","ST","finishing",84,"clinical in the box")],
  sp=("corner","near post","70% of corners are whipped to the near post"), wkp="slow on the turn"),
 dict(team="Brightwell", form=("4-4-2","flat banks of four, compact"),
  st=["compact defensive block","crosses from both flanks"],
  wk=["full-backs are poor at tracking late runs from midfield","slow to shift play when pressed"],
  kp=[("Luca Berg","CAM","passing",88,"dictates tempo between the lines"),("Ivo Petrov","ST","aerial",86,"target man for crosses")],
  sp=("free kick","short routine","short free-kick routine to the edge of the box before a driven shot"), wkp="tracking late runs"),
 dict(team="Cragmoor", form=("3-5-2","wing-backs push up to form a front five"),
  st=["wing-backs provide width","strong in aerial duels"],
  wk=["space behind the wing-backs on transitions","goalkeeper hesitates on crosses"],
  kp=[("Dmitri Volkov","RWB","pace",85,"relentless runs down the right"),("Karim Haddad","CB","aerial",88,"wins most headers")],
  sp=("throw-in","long throw","long throw-ins into the six-yard box from the right side"), wkp="space behind the wing-backs"),
 dict(team="Dunmere", form=("4-2-3-1","double pivot shields the back four"),
  st=["possession through the double pivot","creative number ten"],
  wk=["double pivot is dragged out of position by the press","slow to reorganise after losing possession"],
  kp=[("Marco Silva","CAM","dribbling",89,"beats players in tight spaces"),("Ben Clarke","DM","tackling",82,"breaks up play")],
  sp=("corner","inswinger to far post","inswinging corners targeted at the far post"), wkp="dragged out of position"),
 dict(team="Eastvale", form=("5-4-1","deep low block"),
  st=["disciplined low block","dangerous on the break through a lone striker"],
  wk=["lacks creativity in build-up","tires after the 70th minute"],
  kp=[("Ahmed Nasser","ST","pace",87,"runs the channels"),("Piotr Zielinski","CB","aerial",83,"commands the box")],
  sp=("free kick","wall-and-run","indirect free kicks played into a runner peeling off the wall"), wkp="lacks creativity"),
 dict(team="Fairholt", form=("4-3-3","very high defensive line"),
  st=["high line compresses the pitch","full-backs overlap constantly"],
  wk=["high line is vulnerable to through balls","weak in aerial duels at the back"],
  kp=[("Jonas Weber","RW","dribbling",86,"takes on his full-back every time"),("Eli Mensah","CM","passing",80,"switches play quickly")],
  sp=("corner","short corner","short corner to a player on the edge of the area"), wkp="through balls"),
 dict(team="Glenrock", form=("4-1-4-1","single pivot with a flat midfield four"),
  st=["strong pressing triggers","good set-piece delivery"],
  wk=["lone holding midfielder is exposed when bypassed","left-back struggles against pace"],
  kp=[("Noah Park","DM","tackling",85,"screens the back four"),("Raul Ortega","LB","pace",70,"adds width but is beaten for speed")],
  sp=("corner","decoy runs","decoy runs at the near post to free a header at the penalty spot"), wkp="exposed when bypassed"),
 dict(team="Harrowgate", form=("3-4-3","front three interchange positions"),
  st=["front three interchange positions","quick ball circulation"],
  wk=["back three is stretched by wide overloads","poor discipline with many fouls near the box"],
  kp=[("Idris Kamara","LW","dribbling",88,"drifts inside from the left"),("Henrik Larsen","CB","tackling",81,"aggressive stepping out")],
  sp=("free kick","direct shot","direct free kicks from the left of the area taken by Kamara"), wkp="stretched by wide overloads"),
]
EXTRA = {  # older reports for first four teams -> repeated set-piece pattern + a distractor weakness
 "Ashford":"pressing line is easily split by one-twos","Brightwell":"midfield two is overrun in transition",
 "Cragmoor":"centre-back trio loses shape when the ball is switched","Dunmere":"full-backs rarely overlap"}

def build(root="."):
    os.makedirs(f"{root}/data/corpus", exist_ok=True)
    truth, docmap, stats, n = [], {}, {"home": {}, "opp": {}}, 0
    for pos,(nm,r) in HOME.items(): stats["home"][pos] = {"name": nm, **r}
    def write(doc_id, lines):
        with open(f"{root}/data/corpus/{doc_id}.txt","w") as f: f.write("\n".join(lines)+"\n")
    for t in T:
        n += 1; did = f"RPT-{n:02d}"; docmap.setdefault(t["team"],[]).append(did)
        L=[f"Scouting report {did} - match observed: Lakeside scouting trip", f"Team: {t['team']}",
           f"Formation: {t['form'][0]} | {t['form'][1]}"]
        L += [f"Strength: {s}." for s in t["st"]] + [f"Weakness: {w}." for w in t["wk"]]
        for nm,pos,attr,rt,note in t["kp"]:
            L.append(f"Key player: {nm} | {pos} | {attr} | {rt} | {note}.")
            stats["opp"][nm]={"pos":pos,"attr":attr,"rating":rt}
        k,p,d = t["sp"]; L.append(f"Set piece: {k} | {p} | {d}.")
        write(did,L)
        truth += [dict(team=t["team"],type="formation",phrase=t["form"][0],source=did),
                  dict(team=t["team"],type="weakness",phrase=t["wkp"],source=did),
                  dict(team=t["team"],type="key_player",phrase=t["kp"][0][0],source=did),
                  dict(team=t["team"],type="set_piece",phrase=p,source=did)]
    for tm,extra_wk in EXTRA.items():
        n += 1; did=f"RPT-{n:02d}"; t=next(x for x in T if x["team"]==tm); docmap[tm].append(did)
        k,p,d=t["sp"]
        write(did,[f"Scouting report {did} - match observed: earlier season fixture", f"Team: {tm}",
                   f"Formation: {t['form'][0]} | same shape as later matches", f"Strength: {t['st'][0]}.",
                   f"Weakness: {extra_wk}.", f"Set piece: {k} | {p} | again used: {d}."])
    json.dump(truth,open(f"{root}/data/ground_truth.json","w"),indent=1)
    json.dump(docmap,open(f"{root}/data/team_docs.json","w"),indent=1)
    json.dump(stats,open(f"{root}/data/stats.json","w"),indent=1)
    print(f"built {n} docs, {len(truth)} seeded facts")
if __name__=="__main__": build()
