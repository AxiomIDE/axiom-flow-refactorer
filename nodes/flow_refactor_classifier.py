import json
import os

import anthropic

from gen.axiom_official_axiom_agent_messages_messages_pb2 import AgentRequest, FlowSpec
from gen.axiom_logger import AxiomLogger, AxiomSecrets


SYSTEM_PROMPT = """You are an expert at understanding Axiom flow refactoring requests.
Extract the artifact_id (flow ID) and the refactoring goal from the user's message."""


def flow_refactor_classifier(log: AxiomLogger, secrets: AxiomSecrets, input: AgentRequest) -> FlowSpec:
    """Parse the refactoring goal and identify the target flow."""
    api_key = secrets.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_API_KEY", "")
    client = anthropic.Anthropic(api_key=api_key)

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"""Extract from: "{input.goal}"

Return JSON: {{"artifact_id": "<flow id or empty>", "description": "<what to change>", "candidate_nodes": []}}"""
        }]
    )

    content = message.content[0].text
    if "```json" in content:
        start = content.index("```json") + 7
        end = content.index("```", start)
        content = content[start:end].strip()
    elif "```" in content:
        start = content.index("```") + 3
        end = content.index("```", start)
        content = content[start:end].strip()

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        data = {"artifact_id": "", "description": input.goal, "candidate_nodes": []}

    return FlowSpec(
        artifact_id=data.get("artifact_id", ""),
        description=data.get("description", input.goal),
        candidate_nodes=data.get("candidate_nodes", []),
        fix_instructions=input.goal,
    )
