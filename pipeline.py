from concurrent.futures import ThreadPoolExecutor
from board import StrategyBoard
from agents.retrieval import OppositionRetrievalAgent
from agents.parser import ReportParserAgent
from agents.parser_llm import LLMReportParserAgent
from agents.matchup import MatchupAnalystAgent
from agents.setpiece import SetPieceAgent
from agents.coach import HeadCoachAgent
def run_panel(team, retriever=None, llm=False, corpus_dir="data/corpus"):
    retriever = retriever or OppositionRetrievalAgent(corpus_dir); board = StrategyBoard(team)
    retriever.run(board)                                  # 1. RAG
    if not board.docs:                                    # guard: nothing retrieved -> refuse
        raise LookupError(f"No scouting reports found for '{team}'")
    Parser = LLMReportParserAgent if llm else ReportParserAgent
    Parser(retriever.docs).run(board)                     # 2. structure reports (LLM or rules)
    with ThreadPoolExecutor() as ex:                      # 3. panel specialists in parallel
        list(ex.map(lambda a: a.run(board), [MatchupAnalystAgent(), SetPieceAgent()]))
    return HeadCoachAgent().run(board), board             # 4. coach synthesises
