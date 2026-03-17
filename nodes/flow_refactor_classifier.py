import json
import os

import anthropic

from gen.axiom_official_axiom_agent_messages_messages_pb2 import AgentRequest, FlowBuildContext
from gen.axiom_logger import AxiomLogger, AxiomSecrets


SYSTEM_PROMPT = """You are an expert at understanding Axiom flow refactoring requests.
Extract the existing_graph_id (flow artifact ID) and the refactoring goal from the user's message."""


def flow_refactor_classifier(log: AxiomLogger, secrets: AxiomSecrets, input: AgentRequest) -> FlowBuildContext:
    """Parse the refactoring goal and identify the target flow."""
    api_key, _ = secrets.get("ANTHROPIC_API_KEY")
    client = anthropic.Anthropic(api_key=api_key)

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"""Extract from: "{input.prompt}"

Return JSON: {{"existing_graph_id": "<artifact id or empty>", "description": "<what to change>"}}"""
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
        data = {"existing_graph_id": "", "description": input.prompt}

    return FlowBuildContext(
        existing_graph_id=data.get("existing_graph_id", ""),
        description=data.get("description", input.prompt),
        fix_instructions=input.prompt,
    )
