import json
import os

import anthropic

from gen.axiom_official_axiom_agent_messages_messages_pb2 import FlowBuildContext
from gen.axiom_logger import AxiomLogger, AxiomSecrets


SYSTEM_PROMPT = """You are an expert at modifying Axiom React Flow graph JSON.
Apply the requested changes while preserving valid graph structure.
Only modify what is requested — adding/removing nodes, updating edge adapters, reordering."""


def graph_reassembler(log: AxiomLogger, secrets: AxiomSecrets, input: FlowBuildContext) -> FlowBuildContext:
    """Apply LLM-driven changes to the graph JSON."""

    api_key, _ = secrets.get("ANTHROPIC_API_KEY")
    client = anthropic.Anthropic(api_key=api_key)

    current_graph = input.graph_json or "{}"
    fix_instructions = input.fix_instructions or input.description or "improve the graph"

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
        input.graph_json = json.dumps(graph)
    except json.JSONDecodeError:
        log.warn("LLM returned invalid JSON for reassembled graph; keeping original")

    input.fix_instructions = ""
    return input
