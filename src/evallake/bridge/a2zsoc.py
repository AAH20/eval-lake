"""
Bridge Client for A2Z SOC Integration (https://a2zsoc.com).
Uploads signed OAX evidence envelopes into centralized GRC and Trust Vaults.
"""

import json
import urllib.request
import urllib.error
from typing import Dict, Any, Tuple
from evallake.crypto.oax import OAXEnvelope


class A2ZSOCBridge:
    """Synchronizes evaluation evidence with A2Z SOC enterprise platform."""

    DEFAULT_ENDPOINT = "https://api.a2zsoc.com/v1/compliance/evidence"

    def __init__(self, api_key: str = "", endpoint: str = ""):
        self.api_key = api_key
        self.endpoint = endpoint or self.DEFAULT_ENDPOINT

    def sync_envelope(self, envelope: OAXEnvelope) -> Tuple[bool, Dict[str, Any]]:
        """Sends signed OAX envelope to A2Z SOC endpoint."""
        payload_data = json.loads(envelope.to_canonical_json())
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "eval-lake-client/1.0.0"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        req = urllib.request.Request(
            self.endpoint,
            data=json.dumps(payload_data).encode("utf-8"),
            headers=headers,
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                status_code = resp.getcode()
                response_text = resp.read().decode("utf-8")
                try:
                    res_json = json.loads(response_text)
                except Exception:
                    res_json = {"raw": response_text}
                return (status_code == 200 or status_code == 201), res_json
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            return False, {"error": f"HTTP {e.code}", "details": err_body}
        except Exception as ex:
            return False, {"error": str(ex)}

    @staticmethod
    def export_offline_bundle(envelope: OAXEnvelope, output_path: str) -> str:
        """Exports an offline, air-gapped evidence bundle for auditor handoff."""
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(envelope.to_canonical_json())
        return output_path
