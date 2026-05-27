from models.release_state import ReleaseState

from agents.diff_analysis_agent import DiffAnalysisAgent
from agents.dependency_graph_agent import DependencyGraphAgent
from agents.simulation_agent import SimulationAgent
from agents.risk_assessment_agent import RiskAssessmentAgent
from agents.release_strategy_agent import ReleaseStrategyAgent
from services.event_service import EventService


class ReleaseOrchestrator:
    def run(self):
        state = ReleaseState()

        state.events.append(
            EventService.create_event(
                agent="Orchestrator",
                event="release_analysis_started",
                status="running",
                event_type="orchestration",
                severity="info",
                message=(
                    "Release analysis pipeline initiated"
                ),
                duration_ms=0
            )
        )

        state = DiffAnalysisAgent().run(state)
        state = DependencyGraphAgent().run(state)   
        state = SimulationAgent().run(state)
        state = RiskAssessmentAgent().run(state)
        state = ReleaseStrategyAgent().run(state)

        state.events.append(
            EventService.create_event(
                agent="Orchestrator",
                event="release_analysis_completed",
                status="success",
                event_type="orchestration",
                severity="info",
                message=(
                    "Release analysis pipeline completed"
                ),duration_ms=850
            )
        )

        return state