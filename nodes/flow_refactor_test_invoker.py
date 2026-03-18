import os
import uuid

import httpx

from gen.axiom_official_axiom_agent_messages_messages_pb2 import FlowBuildContext
from gen.axiom_logger import AxiomLogger, AxiomSecrets


def flow_refactor_test_invoker(log: AxiomLogger, secrets: AxiomSecrets, input: FlowBuildContext) -> FlowBuildContext:
    """Test the refactored flow with synthetic input."""

    if not input.compile_success:
        input.test_success = False
        input.test_error = f"Compile failed: {input.compile_error}"
        return input

    bff_url = os.environ.get("BFF_URL", "http://axiom-bff.default.svc.cluster.local:8083")
    axiom_api_key, _ = secrets.get("AXIOM_API_KEY")
    session_id = str(uuid.uuid4()).replace("-", "")

    try:
        resp = httpx.post(
            f"{bff_url}/app/run",
            json={"artifact_id": input.artifact_id, "input": {}},
            headers={
                "Authorization": f"Bearer {axiom_api_key}",
                "X-Debug-Session-Id": session_id,
            },
            timeout=60.0,
        )

        input.session_id = session_id

        if resp.status_code == 200:
            input.test_success = True
            input.execution_id = resp.json().get("execution_id", "")
            input.output_json = resp.text
        else:
            input.test_success = False
            input.test_error = f"Run returned {resp.status_code}: {resp.text[:300]}"
    except Exception as e:
        input.test_success = False
        input.test_error = str(e)
        input.session_id = session_id

    return input
