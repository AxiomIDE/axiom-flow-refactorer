import json
import os

import httpx

from gen.axiom_official_axiom_agent_messages_messages_pb2 import FlowBuildContext
from gen.axiom_logger import AxiomLogger, AxiomSecrets


def flow_refactor_compiler(log: AxiomLogger, secrets: AxiomSecrets, input: FlowBuildContext) -> FlowBuildContext:
    """Compile the refactored flow graph and populate compile fields."""

    bff_url = os.environ.get("BFF_URL", "http://axiom-bff.default.svc.cluster.local:8083")
    axiom_api_key, _ = secrets.get("AXIOM_API_KEY")
    if not input.graph_json:
        input.compile_success = False
        input.compile_error = "No graph_json to compile"
        return input

    try:
        graph = json.loads(input.graph_json)
    except json.JSONDecodeError as e:
        input.compile_success = False
        input.compile_error = f"Invalid graph_json: {e}"
        return input

    try:
        resp = httpx.post(
            f"{bff_url}/app/graphs/compile",
            json={"graph": graph, "description": input.description},
            headers={"Authorization": f"Bearer {axiom_api_key}"},
            timeout=60.0,
        )
        if resp.status_code == 200:
            data = resp.json()
            input.compile_success = True
            input.artifact_id = data.get("artifact_id", "")
        else:
            input.compile_success = False
            input.compile_error = f"Compile returned {resp.status_code}: {resp.text[:300]}"
    except Exception as e:
        log.error(f"FlowRefactorCompiler failed: {e}")
        input.compile_success = False
        input.compile_error = str(e)

    return input
