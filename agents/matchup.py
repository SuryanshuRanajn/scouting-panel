import tools
class MatchupAnalystAgent:
    name = "MatchupAnalystAgent"
    def run(self, board):
        for doc_id, p in board.parsed.items():
            for kp in p["key_players"]:
                try:
                    m = tools.get_matchup(tools.COUNTER[kp["pos"]], kp["name"], kp["attr"])
                except KeyError:   # e.g. LLM misspelled a name / unknown position
                    board.log.append(f"[{self.name}] skipped unknown player/position: {kp}"); continue
                claim = (f"{kp['name']} ({kp['pos']}, {kp['attr']} {kp['rating']}) - {kp['note']}; "
                         f"faces {m['home_player']} ({m['home_attr']} {m['home_rating']}), edge {m['edge']:+d}")
                board.post("matchup", claim, [doc_id], self.name, edge=m["edge"])
