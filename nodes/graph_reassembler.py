import json
import logging
import os

import anthropic

from gen.axiom_official_axiom_agent_messages_messages_pb2 import FlowSpec

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert at modifying Axiom React Flow graph JSON.
Apply the requested changes while preserving valid graph structure.
Only modify what is requested — adding/removing nodes, updating edge adapters, reordering."""


def handle(spec: FlowSpec, context) -> FlowSpec:
    """Apply LLM-driven changes to the graph JSON."""

    api_key = context.secrets.get("ANTHROPIC_API_KEY") if hasattr(context, 'secrets') else os.environ.get("ANTHROPIC_API_KEY", "")
    client = anthropic.Anthropic(api_key=api_key)

    current_graph = spec.graph_json or "{}"
    fix_instructions = spec.fix_instructions or spec.description or "improve the graph"

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"""Apply this refactoring to the flow graph:

Refactoring goal: {fix_instructions}

Current graph JSON:
```json
{current_graph[:3000]}
```

Return ONLY the updated graph JSON object."""
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
        graph = json.loads(content)
        spec.graph_json = json.dumps(graph)
    except json.JSONDecodeError:
        logger.warning("LLM returned invalid JSON for reassembled graph; keeping original")

    spec.fix_instructions = ""
    return spec
