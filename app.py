"""Streamlit interface for the Sports Scouting & Match Strategy Analyst Panel.
Run:  python -m streamlit run app.py   (from the project folder)"""
import html, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import streamlit as st
import ui_logic as L

st.set_page_config(page_title="Scouting Panel", page_icon="⚽", layout="wide")
st.markdown("""<style>
.card{border:1px solid #d9dee7;border-left:6px solid #1F3864;border-radius:8px;padding:10px 14px;margin:8px 0;background:rgba(127,127,127,.06)}
.card .rank{font-weight:700;font-size:1.15rem;margin-right:10px}
.badge{display:inline-block;padding:2px 9px;border-radius:12px;font-size:.78rem;font-weight:600;color:#fff;background:#1F3864}
.b-def{background:#b3261e}.b-exp{background:#1b7f3b}.b-pri{background:#c55a11}.b-mat{background:#2e5597}.b-neu{background:#6b6b6b}.b-sh{background:#7a5ea8}
.card .txt{margin:6px 0 4px 0}.chip{display:inline-block;border:1px solid #888;border-radius:10px;padding:0 8px;margin-right:5px;font-size:.75rem;font-family:monospace}
</style>""", unsafe_allow_html=True)
L.ensure_data()
CLS = {"Defend": "b-def", "Exploit": "b-exp", "Priority matchup (give cover)": "b-pri", "Matchup (we hold the edge)": "b-mat",
       "Neutralise": "b-neu", "Set shape against": "b-sh"}

with st.sidebar:
    st.title("⚽ Scouting Panel")
    st.caption("Multi-agent match strategy analyst")
    team = st.selectbox("Opposition team", L.teams())
    mode = st.radio("Report parser", ["Rule-based (fixed-format reports)", "LLM: Gemini (free-text reports)"])
    use_llm = mode.startswith("LLM")
    if use_llm:
        key = st.text_input("Gemini API key (only needed if reports are not cached)", type="password")
        if key: os.environ["GEMINI_API_KEY"] = key
    run = st.button("Run analyst panel", type="primary")
    st.divider()
    st.caption("Agents: Retrieval, Report Parser, Matchup Analyst, Set-Piece, Head Coach. They share one strategy board.")


if run:
    try:
        with st.spinner("Panel at work..."):
            st.session_state["res"] = L.run_team(team, use_llm)
    except L.MissingKey as e: st.error(str(e) + " Enter a key in the sidebar.")
    except LookupError as e: st.error(str(e))
    except Exception as e: st.error(f"{type(e).__name__}: {e}")

res = st.session_state.get("res")
if not res or res["team"] != team or res["llm"] != use_llm:
    st.title("Match strategy analyst panel")
    st.write("Pick an opponent in the sidebar and click **Run analyst panel**. Five agents read the scouting reports, "
             "post their findings to a shared board, and the Head Coach turns them into a ranked, source-cited plan.")
    st.info("Tip: in LLM mode, reports that were parsed before are cached, so no API key or internet is needed for them.")
    st.stop()

out, board = res["out"], res["board"]
st.header(f"Match plan vs {res['team']}")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Reports retrieved", len(res["docs"])); c2.metric("Plan points", len(out["plan"]))
c3.metric("Repeated set pieces", sum(1 for e in board.read("set_piece") if e.meta.get("repeated")))
c4.metric("Priority matchups", sum(1 for e in board.read("matchup") if e.meta["edge"] >= 5))
t_plan, t_prof, t_board, t_src, t_eval = st.tabs(["Game plan", "Opposition profile", "Strategy board", "Source reports", "Evaluation"])

with t_plan:
    for p in out["plan"]:
        body = html.escape(p["text"].split(": ", 1)[1]); chips = "".join(f"<span class='chip'>{s}</span>" for s in p["sources"])
        st.markdown(f"<div class='card'><span class='rank'>{p['rank']}</span><span class='badge {CLS.get(p['action'], '')}'>"
                    f"{html.escape(p['action'])}</span><div class='txt'>{body}</div><div>{chips}</div></div>", unsafe_allow_html=True)
    st.download_button("Download plan (.txt)", L.plan_text(res), file_name=f"plan_{res['team']}.txt")

with t_prof:

    a, b = st.columns(2)
    with a:
        st.subheader("Strengths")
        for c, s in out["strengths"]: st.markdown(f"- {c}  `{', '.join(s)}`")
    with b:
        st.subheader("Weaknesses")
        for c, s in out["weaknesses"]: st.markdown(f"- {c}  `{', '.join(s)}`")
    st.subheader("Key matchups")
    st.dataframe([{"Matchup": e.claim, "Edge (+ = opponent ahead)": e.meta["edge"], "Source": ", ".join(e.sources)}
                  for e in board.read("matchup")])

with t_board:
    st.caption("Every agent writes here. Each note keeps its section, claim, sources and author.")
    st.dataframe([{"Agent": e.agent, "Section": e.section, "Claim": e.claim, "Sources": ", ".join(e.sources)} for e in board.read()])
    with st.expander("Board log (who did what, in order)"):
        st.code("\n".join(board.log))

with t_src:
    for d, score, text in res["docs"]:
        with st.expander(f"{d}   (retrieval score {score})"): st.text(text)

with t_eval:
    st.write("Runs the full pipeline for all 8 teams and checks the 32 seeded facts against the answer key.")
    if st.button("Run evaluation on all 8 teams"):
        try:
            with st.spinner("Evaluating..."): st.session_state["ev"] = (use_llm, L.evaluate(use_llm))
        except L.MissingKey as e: st.error(str(e) + " Enter a key in the sidebar.")
        except Exception as e: st.error(f"{type(e).__name__}: {e}")
    ev = st.session_state.get("ev")
    if ev and ev[0] == use_llm:
        r = ev[1]; m1, m2, m3 = st.columns(3)
        m1.metric("Facts found in plan", f"{r['found']}/{r['n']}"); m2.metric("Correct source cited", f"{r['correct']}/{r['n']}")

        m3.metric("Wrong-team citations", f"{r['leak']}/{r['cites']}")
        st.dataframe(r["rows"])