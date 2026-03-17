import os
import uuid

import httpx

from gen.axiom_official_axiom_agent_messages_messages_pb2 import CompileResult, TestResult
from gen.axiom_logger import AxiomLogger, AxiomSecrets



def flow_refactor_test_invoker(log: AxiomLogger, secrets: AxiomSecrets, input: CompileResult) -> TestResult:
    """Test the refactored flow with synthetic input."""

    if not input.success:
        return TestResult(success=False, error=f"Compile failed: {input.error}")

    bff_url = os.environ.get("BFF_URL", "http://axiom-bff:8083")
    axiom_api_key = os.environ.get("AXIOM_API_KEY", "")
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
        if resp.status_code == 200:
            return TestResult(
                success=True,
                session_id=session_id,
                execution_id=resp.json().get("execution_id", ""),
                output_json=resp.text,
            )
        else:
            return TestResult(
                success=False,
                session_id=session_id,
                error=f"Run returned {resp.status_code}: {resp.text[:300]}",
            )
    except Exception as e:
        return TestResult(success=False, session_id=session_id, error=str(e))
