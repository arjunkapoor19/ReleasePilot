import json
import time

from models.release_state import ReleaseState

from services.groq_service import GroqService
from services.event_service import EventService


class SimulationAgent:
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

        with open(
            "mock_data/repository_context.txt",
            "r"
        ) as file:
            repository_context = file.read()

        prompt = f"""
You are an AI runtime simulation agent.

Your role:
Simulate the operational impact of deploying
this pull request into production.

You must reason about:

- cascading runtime failures
- orchestration instability
- dependency propagation
- degraded workflows
- operational regressions
- deployment reliability risks

You are analyzing a production multi-agent AI system.

IMPORTANT:
Return ONLY valid JSON.

Required JSON schema:

{{
    "simulation_status": "failed",

    "failure_confidence": 0.91,

    "failed_components": [
        "router_agent",
        "memory_agent"
    ],

    "runtime_errors": [
        "unexpected keyword argument 'limit'"
    ],

    "execution_trace": [
        {{
            "component": "router_agent",
            "status": "failed",
            "reason": "..."
        }}
    ],

    "execution_nodes": [
        {{
            "id": "search_tool",
            "type": "tool",
            "execution_status": "failed"
        }}
    ],

    "execution_edges": [
        {{
            "source": "search_tool",
            "target": "router_agent",
            "status": "failure_propagation"
        }}
    ],

    "operational_impact": "high",

    "summary": "..."
}}

Graph Requirements:

Execution Nodes MUST contain:
- id
- type
- execution_status

Execution Edges MUST contain:
- source
- target
- status

Allowed execution statuses:
- healthy
- affected
- degraded
- failed

Allowed edge statuses:
- normal
- failure_propagation
- degraded_execution
- blocked

Guidelines:
- Think like a production release engineer
- Infer cascading failures
- Simulate realistic runtime instability
- Focus on operational reliability
- Be concise
- Return ONLY JSON
- Build frontend-compatible graph outputs

Diff Analysis Context:

{json.dumps(diff_analysis, indent=2)}

Dependency Analysis Context:

{json.dumps(dependency_analysis, indent=2)}

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
                        "runtime simulation agent."
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
            "simulation_analysis"
        ] = findings

        duration_ms = int(
            (time.time() - start_time) * 1000
        )

        state.events.append(
            EventService.create_event(
                agent="SimulationAgent",

                event="workflow_simulation_completed",

                status="success",

                event_type="simulation",

                severity=findings.get(
                    "operational_impact",
                    "high"
                ),

                message=findings.get(
                    "summary",
                    "Workflow simulation completed"
                ),

                duration_ms=duration_ms
            )
        )

        return state