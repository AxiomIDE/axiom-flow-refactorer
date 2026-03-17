import json
import logging
import os

import anthropic

from gen.axiom_official_axiom_agent_messages_messages_pb2 import AgentRequest, FlowSpec

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert at understanding Axiom flow refactoring requests.
Extract the artifact_id (flow ID) and the refactoring goal from the user's message."""


def handle(req: AgentRequest, context) -> FlowSpec:
    """Parse the refactoring goal and identify the target flow."""
    api_key = context.secrets.get("ANTHROPIC_API_KEY") if hasattr(context, 'secrets') else os.environ.get("ANTHROPIC_API_KEY", "")
    client = anthropic.Anthropic(api_key=api_key)

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"""Extract from: "{req.goal}"

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
        data = {"artifact_id": "", "description": req.goal, "candidate_nodes": []}

    return FlowSpec(
        artifact_id=data.get("artifact_id", ""),
        description=data.get("description", req.goal),
        candidate_nodes=data.get("candidate_nodes", []),
        fix_instructions=req.goal,
    )
