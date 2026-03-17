import json
import os

import httpx

from gen.axiom_official_axiom_agent_messages_messages_pb2 import FlowBuildContext
from gen.axiom_logger import AxiomLogger, AxiomSecrets


def graph_fetcher(log: AxiomLogger, secrets: AxiomSecrets, input: FlowBuildContext) -> FlowBuildContext:
    """Fetch the current flow graph JSON from the BFF blobstore."""

    if not input.existing_graph_id:
        log.warn("No existing_graph_id provided; skipping graph fetch")
        return input

    bff_url = os.environ.get("BFF_URL", "http://axiom-bff:8083")
    axiom_api_key = os.environ.get("AXIOM_API_KEY", "")

    try:
        resp = httpx.get(
            f"{bff_url}/app/graphs/{input.existing_graph_id}",
            headers={"Authorization": f"Bearer {axiom_api_key}"},
            timeout=15.0,
        )
        if resp.status_code == 200:
            data = resp.json()
            input.graph_json = json.dumps(data.get("graph", data))
        else:
            log.warn(f"Graph fetch returned {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        log.warn(f"Failed to fetch graph: {e}")

    return input
