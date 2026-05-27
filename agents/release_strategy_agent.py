import json
import time

from models.release_state import ReleaseState

from services.groq_service import GroqService
from services.event_service import EventService


class ReleaseStrategyAgent:
    def run(self, state: ReleaseState) -> ReleaseState:
        start_time = time.time()

        diff_analysis = state.findings.get(
            "diff_analysis",
            {}
        )

        dependency_analysis = state.findings.get(
            "dependency_analysis",
            {}
        )

        simulation_analysis = state.findings.get(
            "simulation_analysis",
            {}
        )

        risk_assessment = state.findings.get(
            "risk_assessment",
            {}
        )

        with open(
            "mock_data/repository_context.txt",
            "r"
        ) as file:
            repository_context = file.read()

        prompt = f"""
You are an AI release strategy agent.

Your role:
Generate operational deployment strategy for
a production AI system.

You must synthesize intelligence from:

1. Diff Analysis Agent
2. Dependency Graph Agent
3. Runtime Simulation Agent
4. Risk Assessment Agent

You are responsible for:
- deployment planning
- rollback strategy
- mitigation sequencing
- release stabilization
- operational recovery planning
- deployment execution guidance

You are the final deployment authority.

IMPORTANT:
Return ONLY valid JSON.

Required JSON schema:

{{
    "recommended_strategy": "rollback_release",

    "deployment_status": "blocked",

    "deployment_confidence": 0.93,

    "rollback_probability": 0.88,

    "rollback_plan": [
        {{
            "step": 1,
            "action": "Restore search_tool v2.1"
        }}
    ],

    "mitigation_steps": [
        {{
            "priority": "high",
            "action": "Add backward compatibility shim"
        }}
    ],

    "release_recommendations": [
        "Validate downstream orchestration agents",
        "Run staged canary deployment"
    ],

    "deployment_strategy_graph": {{
        "nodes": [
            {{
                "id": "rollback_release",
                "type": "strategy",
                "status": "recommended"
            }}
        ],

        "edges": [
            {{
                "source": "critical_risk",
                "target": "rollback_release",
                "relationship": "triggers"
            }}
        ]
    }},

    "operational_summary": {{
        "system_stability": "unstable",
        "release_safety": "unsafe",
        "production_readiness": "blocked"
    }},

    "summary": "..."
}}

Graph Requirements:

Strategy graph nodes MUST contain:
- id
- type
- status

Strategy graph edges MUST contain:
- source
- target
- relationship

Allowed deployment statuses:
- approved
- manual_review
- blocked

Allowed strategies:
- approve_release
- canary_release
- rollback_release
- staged_deployment

Guidelines:
- Think like a senior release engineer
- Prioritize production stability
- Focus on operational safety
- Generate realistic mitigation plans
- Reason about deployment recovery
- Be concise
- Return ONLY JSON
- Build frontend-compatible graph outputs

Diff Analysis Context:

{json.dumps(diff_analysis, indent=2)}

Dependency Analysis Context:

{json.dumps(dependency_analysis, indent=2)}

Simulation Analysis Context:

{json.dumps(simulation_analysis, indent=2)}

Risk Assessment Context:

{json.dumps(risk_assessment, indent=2)}

Repository Context:

{repository_context}
"""

        client = GroqService.get_client()

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a senior AI "
                        "release strategy agent."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.3,

            response_format={
                "type": "json_object"
            }
        )

        content = (
            response
            .choices[0]
            .message
            .content
        )

        findings = json.loads(content)

        state.findings[
            "release_strategy"
        ] = findings

        duration_ms = int(
            (time.time() - start_time) * 1000
        )

        state.events.append(
            EventService.create_event(
                agent="ReleaseStrategyAgent",

                event="release_strategy_generated",

                status="success",

                event_type="release_strategy",

                severity="critical",

                message=findings.get(
                    "summary",
                    "Release strategy generated"
                ),

                duration_ms=duration_ms
            )
        )

        return state