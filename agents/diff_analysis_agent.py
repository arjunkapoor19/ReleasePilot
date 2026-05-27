import json
import time

from models.release_state import ReleaseState

from services.groq_service import GroqService
from services.event_service import EventService


class DiffAnalysisAgent:
    def run(self, state: ReleaseState) -> ReleaseState:
        start_time = time.time()

        with open(
            "mock_data/sample_pr_diff.txt",
            "r"
        ) as file:
            diff_content = file.read()

        prompt = f"""
You are an AI release engineering agent.

Your role:
Analyze pull request diffs and detect:

- breaking changes
- architectural risks
- dependency instability
- workflow-impacting modifications
- operational concerns

You are analyzing a production AI system.

Return ONLY valid JSON.

Required JSON schema:

{{
    "breaking_change": true,
    "change_type": "tool_contract_change",
    "affected_component": "search_tool",
    "severity": "high",
    "architectural_impact": "high",
    "summary": "..."
}}

Guidelines:
- Be concise
- Think operationally
- Focus on deployment safety
- Infer architectural implications
- Detect API compatibility risks
- Detect workflow instability risks

Pull Request Diff:

{diff_content}
"""

        client = GroqService.get_client()

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a senior AI "
                        "release engineering agent."
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
            "diff_analysis"
        ] = findings

        duration_ms = int(
            (time.time() - start_time) * 1000
        )

        state.events.append(
            EventService.create_event(
                agent="DiffAnalysisAgent",
                event="diff_analysis_completed",
                status="success",
                event_type="analysis",
                severity=findings.get(
                    "severity",
                    "medium"
                ),
                message=findings.get(
                    "summary",
                    "Diff analysis completed"
                ),

                duration_ms=duration_ms
            )
        )

        return state