import json
import time

from models.release_state import ReleaseState

from services.groq_service import GroqService
from services.event_service import EventService


class DependencyGraphAgent:
    def run(self, state: ReleaseState) -> ReleaseState:
        start_time = time.time()

        diff_analysis = state.findings.get(
            "diff_analysis",
            {}
        )

        with open(
            "mock_data/repository_context.txt",
            "r"
        ) as file:
            repository_context = file.read()

        prompt = f"""
You are an AI dependency mapping agent.

Your role:
Analyze repository architecture and infer:

- downstream dependencies
- affected orchestration agents
- impacted workflows
- blast radius
- architectural propagation paths

You are building dependency topology for a
release engineering platform.

IMPORTANT:
Return ONLY valid JSON.

Required JSON schema:

{{
    "affected_components": [
        "router_agent",
        "memory_agent"
    ],

    "affected_workflows": [
        "customer_support_resolution"
    ],

    "blast_radius": "high",

    "nodes": [
        {{
            "id": "search_tool",
            "type": "tool",
            "status": "affected"
        }}
    ],

    "edges": [
        {{
            "source": "search_tool",
            "target": "router_agent",
            "relationship": "dependency"
        }}
    ]
}}

Graph Requirements:
- Nodes MUST have:
    - id
    - type
    - status

- Edges MUST have:
    - source
    - target
    - relationship

Allowed node types:
- tool
- agent
- workflow
- service
- model
- database

Allowed statuses:
- healthy
- affected
- degraded
- failed

Guidelines:
- Infer architectural relationships
- Think operationally
- Focus on dependency propagation
- Build graph-friendly topology
- Be concise
- Do NOT explain outside JSON

Diff Analysis Context:

{json.dumps(diff_analysis, indent=2)}

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
                        "dependency analysis agent."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.2,

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
            "dependency_analysis"
        ] = findings

        duration_ms = int(
            (time.time() - start_time) * 1000
        )

        state.events.append(
            EventService.create_event(
                agent="DependencyGraphAgent",

                event="dependency_analysis_completed",

                status="success",

                event_type="dependency_mapping",

                severity=findings.get(
                    "blast_radius",
                    "medium"
                ),

                message=(
                    "Architectural dependency graph "
                    "generated successfully"
                ),

                duration_ms=duration_ms
            )
        )

        return state