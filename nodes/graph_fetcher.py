import os

import httpx

from gen.axiom_official_axiom_agent_messages_messages_pb2 import FlowSpec
from gen.axiom_logger import AxiomLogger, AxiomSecrets



def graph_fetcher(log: AxiomLogger, secrets: AxiomSecrets, input: FlowSpec) -> FlowSpec:
    """Fetch the current flow graph JSON from the BFF blobstore."""

    if not input.artifact_id:
        log.warning("No artifact_id provided; skipping graph fetch")
        return input

    bff_url = os.environ.get("BFF_URL", "http://axiom-bff:8083")
    axiom_api_key = os.environ.get("AXIOM_API_KEY", "")

    try:
        resp = httpx.get(
            f"{bff_url}/app/graphs/{input.artifact_id}",
            headers={"Authorization": f"Bearer {axiom_api_key}"},
            timeout=15.0,
        )
        if resp.status_code == 200:
            data = resp.json()
            import json
            input.graph_json = json.dumps(data.get("graph", data))
        else:
            log.warning(f"Graph fetch returned {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        log.warning(f"Failed to fetch graph: {e}")

    return input
