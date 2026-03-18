import json
import os

import anthropic
import httpx

from gen.axiom_official_axiom_agent_messages_messages_pb2 import FlowBuildContext
from gen.axiom_logger import AxiomLogger, AxiomSecrets


SYSTEM_PROMPT = """You are an expert at validating refactored Axiom flow graphs.
Check if the flow ran correctly and identify any remaining issues."""


def flow_refactor_analyser(log: AxiomLogger, secrets: AxiomSecrets, input: FlowBuildContext) -> FlowBuildContext:
    if input.test_success:
        input.has_error = False
        input.error_summary = "Refactored flow validated successfully"
        return input

    api_key, _ = secrets.get("ANTHROPIC_API_KEY")
    debug_trace = ""
    if input.session_id:
        ingress_url = os.environ.get("INGRESS_URL", "http://axiom-ingress.default.svc.cluster.local:80")
        axiom_api_key, _ = secrets.get("AXIOM_API_KEY")
        try:
            resp = httpx.get(
                f"{ingress_url}/v1/debug-events",
                params={"session_id": input.session_id, "limit": "50"},
                headers={"Authorization": f"Bearer {axiom_api_key}"},
                timeout=10.0,
            )
            if resp.status_code == 200:
                debug_trace = json.dumps(resp.json(), indent=2)[:3000]
        except Exception as e:
            log.warn(f"Failed to fetch debug events: {e}")

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"""Refactored flow test failed:
{input.test_error}

Debug trace:
{debug_trace or "(none)"}

What graph changes are still needed?"""
        }]
    )

    input.has_error = True
    input.fix_instructions = message.content[0].text
    input.error_summary = (input.test_error or "Unknown error")[:200]
    input.iteration = input.iteration + 1

    return input
