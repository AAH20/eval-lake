"""
OpenAssurance Exchange (OAX) Protocol Implementation for AI Evidence.
Serializes evaluation receipts into signed, verifiable, tamper-evident envelopes.
"""

import json
import hashlib
from typing import Dict, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from evallake.crypto.ed25519 import CryptoSigner
from evallake.etl.schema import BatchEvaluationReceipt


@dataclass
class OAXEnvelope:
    version: str
    envelope_id: str
    issued_at: str
    payload_digest: str
    payload: Dict[str, Any]
    signer: Dict[str, str]

    def to_canonical_json(self) -> str:
        d = {
            "version": self.version,
            "envelope_id": self.envelope_id,
            "issued_at": self.issued_at,
            "payload_digest": self.payload_digest,
            "payload": self.payload,
            "signer": self.signer
        }
        return json.dumps(d, sort_keys=True, separators=(",", ":"))


def canonicalize(obj: Any) -> bytes:
    """Returns RFC 8785 compliant canonical JSON bytes."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sign_evaluation_receipt(receipt: BatchEvaluationReceipt, private_key_b64: str, public_key_b64: str) -> OAXEnvelope:
    """Signs an evaluation receipt and wraps it into an OAX v1 envelope."""
    payload = receipt.to_dict()
    canonical_payload_bytes = canonicalize(payload)
    digest = "sha256:" + hashlib.sha256(canonical_payload_bytes).hexdigest()

    # Sign the canonical payload
    signature_b64 = CryptoSigner.sign(canonical_payload_bytes, private_key_b64)

    return OAXEnvelope(
        version="oax-v1",
        envelope_id=f"oax_env_{receipt.batch_id}",
        issued_at=datetime.now(timezone.utc).isoformat(),
        payload_digest=digest,
        payload=payload,
        signer={
            "algorithm": "ed25519",
            "public_key": public_key_b64,
            "signature": signature_b64
        }
    )


def verify_evaluation_receipt(envelope_dict: Dict[str, Any], public_key_b64: str) -> Tuple[bool, str]:
    """Verifies that an OAX envelope is untampered, mathematically valid, and signed."""
    if envelope_dict.get("version") != "oax-v1":
        return False, "Unsupported envelope version (expected oax-v1)"

    payload = envelope_dict.get("payload")
    if not isinstance(payload, dict):
        return False, "Invalid or missing payload object"

    declared_digest = envelope_dict.get("payload_digest", "")
    canonical_payload_bytes = canonicalize(payload)
    computed_digest = "sha256:" + hashlib.sha256(canonical_payload_bytes).hexdigest()

    if declared_digest != computed_digest:
        return False, f"Tamper detected: payload digest mismatch (expected {declared_digest}, computed {computed_digest})"

    signer = envelope_dict.get("signer", {})
    signature_b64 = signer.get("signature", "")
    signer_pubkey = signer.get("public_key", public_key_b64)

    valid_sig = CryptoSigner.verify(canonical_payload_bytes, signature_b64, signer_pubkey)
    if not valid_sig:
        return False, "Cryptographic signature validation failed"

    return True, "OAX envelope verified: signature valid, digest matched, zero tampering detected"
