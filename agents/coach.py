class HeadCoachAgent:
    """Synthesises every panel view into one ranked plan; each point carries its source report(s)."""
    name = "HeadCoachAgent"
    def run(self, board):
        items = []
        for e in board.read():
            if e.section == "set_piece":   items.append((3.0 + e.meta.get("repeated", False), "Defend", e))
            elif e.section == "weakness":  items.append((2.5, "Exploit", e))
            elif e.section == "matchup":
                edge = e.meta["edge"]
                if edge >= 5: items.append((2.0 + min(edge, 20)/10, "Priority matchup (give cover)", e))
                else:         items.append((1.8, "Matchup (we hold the edge)", e))
            elif e.section == "strength":  items.append((1.5, "Neutralise", e))
            elif e.section == "formation": items.append((1.2, "Set shape against", e))
        items.sort(key=lambda x: -x[0])
        plan = [dict(rank=i+1, action=a, text=f"{a}: {e.claim}", sources=e.sources, score=round(s,2))
                for i, (s, a, e) in enumerate(items)]
        board.post("plan", f"{len(plan)} points", [], self.name)
        return dict(team=board.team,
                    strengths=[(e.claim, e.sources) for e in board.read("strength")],
                    weaknesses=[(e.claim, e.sources) for e in board.read("weakness")],
                    key_matchups=[(e.claim, e.sources) for e in board.read("matchup")], plan=plan)
