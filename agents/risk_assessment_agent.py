import json
import time

from models.release_state import ReleaseState

from services.groq_service import GroqService
from services.event_service import EventService


class RiskAssessmentAgent:
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

        with open(
            "mock_data/repository_context.txt",
            "r"
        ) as file:
            repository_context = file.read()

        prompt = f"""
You are an AI release risk assessment agent.

Your role:
Assess deployment risk for a production AI system.

You must synthesize intelligence from:

1. Diff Analysis Agent
2. Dependency Graph Agent
3. Runtime Simulation Agent

You are the final operational risk authority.

Your task:
- estimate deployment risk
- identify operational instability
- evaluate production safety
- assess rollback likelihood
- determine deployment readiness
- reason about cascading failures
- analyze architectural fragility

IMPORTANT:
Return ONLY valid JSON.

Required JSON schema:

{{
    "risk_score": 87,

    "risk_level": "critical",

    "deployment_recommendation": "block_release",

    "rollback_probability": 0.84,

    "confidence_score": 0.92,

    "risk_factors": [
        "Breaking API contract detected",
        "High downstream dependency propagation"
    ],

    "affected_systems": [
        "router_agent",
        "memory_agent"
    ],

    "operational_risks": [
        {{
            "risk": "workflow_instability",
            "severity": "critical",
            "reason": "..."
        }}
    ],

    "deployment_decision_graph": {{
        "nodes": [
            {{
                "id": "deployment_risk",
                "type": "risk",
                "status": "critical"
            }}
        ],

        "edges": [
            {{
                "source": "runtime_failure",
                "target": "deployment_risk",
                "relationship": "increases_risk"
            }}
        ]
    }},

    "summary": "..."
}}

Graph Requirements:

Decision graph nodes MUST contain:
- id
- type
- status

Decision graph edges MUST contain:
- source
- target
- relationship

Allowed deployment recommendations:
- approve_release
- canary_release
- manual_review
- block_release

Allowed risk levels:
- low
- medium
- high
- critical

Guidelines:
- Think like a senior production release engineer
- Prioritize operational safety
- Reason about deployment reliability
- Infer cascading architectural risks
- Synthesize intelligence across agents
- Focus on realistic operational consequences
- Build graph-friendly outputs
- Return ONLY JSON

Diff Analysis Context:

{json.dumps(diff_analysis, indent=2)}

Dependency Analysis Context:

{json.dumps(dependency_analysis, indent=2)}

Simulation Analysis Context:

{json.dumps(simulation_analysis, indent=2)}

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
                        "release risk assessment agent."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.25,

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
            "risk_assessment"
        ] = findings

        state.risk_score = findings.get(
            "risk_score",
            0
        )

        state.deployment_recommendation = (
            findings.get(
                "deployment_recommendation",
                "manual_review"
            )
        )

        duration_ms = int(
            (time.time() - start_time) * 1000
        )

        state.events.append(
            EventService.create_event(
                agent="RiskAssessmentAgent",

                event="risk_assessment_completed",

                status="success",

                event_type="risk_analysis",

                severity=findings.get(
                    "risk_level",
                    "high"
                ),

                message=findings.get(
                    "summary",
                    "Risk assessment completed"
                ),

                duration_ms=duration_ms
            )
        )

        return state