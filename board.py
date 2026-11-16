"""Shared strategy board: every agent reads and writes here."""
from dataclasses import dataclass, field
@dataclass
class Entry:
    section: str; claim: str; sources: list; agent: str; meta: dict = field(default_factory=dict)
class StrategyBoard:
    def __init__(self, team):
        self.team, self.entries, self.log = team, [], []
        self.docs, self.parsed = [], {}      # retrieved doc ids; doc_id -> structured report
    def post(self, section, claim, sources, agent, **meta):
        e = Entry(section, claim, list(sources), agent, meta); self.entries.append(e)
        self.log.append(f"[{agent}] {section}: {claim[:70]}"); return e
    def read(self, section=None):
        return [e for e in self.entries if section is None or e.section == section]
