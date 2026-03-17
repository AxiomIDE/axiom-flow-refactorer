import json
import os

import httpx

from gen.axiom_official_axiom_agent_messages_messages_pb2 import FlowSpec, CompileResult
from gen.axiom_logger import AxiomLogger, AxiomSecrets



def flow_refactor_compiler(log: AxiomLogger, secrets: AxiomSecrets, input: FlowSpec) -> CompileResult:
    """Compile the refactored flow graph."""

    bff_url = os.environ.get("BFF_URL", "http://axiom-bff:8083")
    axiom_api_key = os.environ.get("AXIOM_API_KEY", "")

    if not input.graph_json:
        return CompileResult(success=False, error="No graph_json to compile")

    try:
        graph = json.loads(input.graph_json)
    except json.JSONDecodeError as e:
        return CompileResult(success=False, error=f"Invalid graph_json: {e}")

    try:
        resp = httpx.post(
            f"{bff_url}/app/graphs/compile",
            json={"graph": graph, "description": input.description},
            headers={"Authorization": f"Bearer {axiom_api_key}"},
            timeout=60.0,
        )
        if resp.status_code == 200:
            data = resp.json()
            return CompileResult(
                success=True,
                artifact_id=data.get("artifact_id", ""),
                graph_json=input.graph_json,
            )
        else:
            return CompileResult(
                success=False,
                error=f"Compile returned {resp.status_code}: {resp.text[:300]}",
                graph_json=input.graph_json,
            )
    except Exception as e:
        log.exception("FlowRefactorCompiler failed")
        return CompileResult(success=False, error=str(e))
