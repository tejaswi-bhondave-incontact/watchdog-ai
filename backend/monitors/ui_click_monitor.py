from typing import List, Dict
from datetime import datetime
from collections import defaultdict


class UIClickMonitor:
    def __init__(self):
        self.click_events: List[Dict] = []
        self.sessions: Dict[str, List[Dict]] = defaultdict(list)
        self.blindspots: List[Dict] = []

    def ingest(self, event: Dict):
        self.click_events.append(event)
        session_id = event.get("session_id", "unknown")
        self.sessions[session_id].append(event)
        self._analyze_session(session_id)

    def _analyze_session(self, session_id: str):
        session_events = self.sessions[session_id]

        for event in session_events:
            if event.get("error"):
                path = self._get_click_path(session_id, event)
                scenario = f"ui_error_path_{'_'.join(path[-3:])}"

                if not any(b["scenario"] == scenario for b in self.blindspots):
                    self.blindspots.append({
                        "source": "ui_clicks",
                        "category": "UI Click Paths",
                        "endpoint": f"{event['page']}/{event['element']}",
                        "scenario": scenario,
                        "details": (
                            f"User path {' → '.join(path)} leads to error: {event['error']}. "
                            f"No test covers this navigation sequence."
                        ),
                        "severity": "high",
                        "click_path": path,
                        "error": event["error"],
                        "detected_at": datetime.now().isoformat(),
                        "test_generated": False,
                    })

        if len(session_events) >= 3:
            last_3 = session_events[-3:]
            if self._is_rage_click(last_3):
                page = last_3[0].get("page", "unknown")
                element = last_3[0].get("element", "unknown")
                scenario = f"rage_click_{page}_{element}"

                if not any(b["scenario"] == scenario for b in self.blindspots):
                    self.blindspots.append({
                        "source": "ui_clicks",
                        "category": "UI Click Paths",
                        "endpoint": f"{page}/{element}",
                        "scenario": scenario,
                        "details": (
                            f"Rage click detected: user clicked '{element}' on '{page}' "
                            f"3+ times rapidly — element may be unresponsive or confusing."
                        ),
                        "severity": "medium",
                        "detected_at": datetime.now().isoformat(),
                        "test_generated": False,
                    })

    def _get_click_path(self, session_id: str, target_event: Dict) -> List[str]:
        session_events = self.sessions[session_id]
        path = []
        for event in session_events:
            path.append(f"{event['page']}/{event['element']}")
            if event == target_event:
                break
        return path[-5:]

    def _is_rage_click(self, events: List[Dict]) -> bool:
        if len(events) < 3:
            return False
        same_element = all(
            e.get("element") == events[0].get("element") and
            e.get("page") == events[0].get("page")
            for e in events
        )
        return same_element

    def get_blindspots(self) -> List[Dict]:
        return self.blindspots

    def get_sessions(self) -> Dict:
        return dict(self.sessions)
