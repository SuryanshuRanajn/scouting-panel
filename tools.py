"""Mock statistics tool (reads a local JSON file)."""
import json
_S = json.load(open("data/stats.json"))
COUNTER = {"LW":"RB","RW":"LB","LWB":"RB","RWB":"LB","ST":"CB","CB":"ST","CAM":"DM","CM":"DM","DM":"CAM","LB":"RW","RB":"LW"}
ATTR_COUNTER = {"pace":"pace","aerial":"aerial","dribbling":"tackling","passing":"tackling","finishing":"tackling","tackling":"dribbling"}
def get_matchup(home_pos, opp_player, attr):
    h = _S["home"][home_pos]; o = _S["opp"][opp_player]; ha = ATTR_COUNTER[attr]
    return {"home_player":h["name"],"home_attr":ha,"home_rating":h[ha],"opp_rating":o["rating"],
            "edge":o["rating"]-h[ha]}   # >0 means the opponent is better
