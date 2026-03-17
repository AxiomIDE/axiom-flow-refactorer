import json
import logging
import os

import httpx

from gen.axiom_official_axiom_agent_messages_messages_pb2 import FlowSpec, CompileResult

logger = logging.getLogger(__name__)


def handle(spec: FlowSpec, context) -> CompileResult:
    """Compile the refactored flow graph."""

    bff_url = os.environ.get("BFF_URL", "http://axiom-bff:8083")
    axiom_api_key = os.environ.get("AXIOM_API_KEY", "")

    if not spec.graph_json:
        return CompileResult(success=False, error="No graph_json to compile")

    try:
        graph = json.loads(spec.graph_json)
    except json.JSONDecodeError as e:
        return CompileResult(success=False, error=f"Invalid graph_json: {e}")

    try:
        resp = httpx.post(
            f"{bff_url}/app/graphs/compile",
            json={"graph": graph, "description": spec.description},
            headers={"Authorization": f"Bearer {axiom_api_key}"},
            timeout=60.0,
        )
        if resp.status_code == 200:
            data = resp.json()
            return CompileResult(
                success=True,
                artifact_id=data.get("artifact_id", ""),
                graph_json=spec.graph_json,
            )
        else:
            return CompileResult(
                success=False,
                error=f"Compile returned {resp.status_code}: {resp.text[:300]}",
                graph_json=spec.graph_json,
            )
    except Exception as e:
        logger.exception("FlowRefactorCompiler failed")
        return CompileResult(success=False, error=str(e))
