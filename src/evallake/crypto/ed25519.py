"""
Cryptographic Signing and Verification Engine.
Implements Ed25519 (RFC 8032) using PyCA Cryptography when available,
with a self-contained, pure-Python RFC 8032 Ed25519 implementation as zero-dependency fallback.
"""

import os
import hashlib
import base64
from typing import Tuple

# ============================================================================
# Pure-Python RFC 8032 Ed25519 Implementation (Zero External Dependencies)
# ============================================================================

q = 2**255 - 19
l = 2**252 + 27742317777372353535851937790883648493


def expmod(b: int, e: int, m: int) -> int:
    return pow(b, e, m)


def inv(x: int) -> int:
    return expmod(x, q - 2, q)


d = -121665 * inv(121666) % q
I = expmod(2, (q - 1) // 4, q)


def xrecover(y: int) -> int:
    xx = (y * y - 1) * inv(d * y * y + 1)
    x = expmod(xx, (q + 3) // 8, q)
    if (x * x - xx) % q != 0:
        x = (x * I) % q
    if x % 2 != 0:
        x = q - x
    return x


By = 4 * inv(5) % q
Bx = xrecover(By)
B = (Bx, By)


def edwards_add(P: Tuple[int, int], Q: Tuple[int, int]) -> Tuple[int, int]:
    x1, y1 = P
    x2, y2 = Q
    x3 = (x1 * y2 + x2 * y1) * inv(1 + d * x1 * x2 * y1 * y2) % q
    y3 = (y1 * y2 + x1 * x2) * inv(1 - d * x1 * x2 * y1 * y2) % q
    return (x3, y3)


def scalarmult(P: Tuple[int, int], e: int) -> Tuple[int, int]:
    if e == 0:
        return (0, 1)
    Q = scalarmult(P, e // 2)
    Q = edwards_add(Q, Q)
    if e & 1:
        Q = edwards_add(Q, P)
    return Q


def encodepoint(P: Tuple[int, int]) -> bytes:
    x, y = P
    bits = [(y >> i) & 1 for i in range(255)] + [x & 1]
    return bytes([sum([bits[i * 8 + j] << j for j in range(8)]) for i in range(32)])


def decodepoint(s: bytes) -> Tuple[int, int]:
    y = sum([s[i] << (i * 8) for i in range(32)]) & ((1 << 255) - 1)
    x = xrecover(y)
    if (x & 1) != ((s[31] >> 7) & 1):
        x = q - x
    P = (x, y)
    if not isoncurve(P):
        raise ValueError("Decoding point that is not on Edwards curve")
    return P


def isoncurve(P: Tuple[int, int]) -> bool:
    x, y = P
    return (-x * x + y * y - 1 - d * x * x * y * y) % q == 0


def H(m: bytes) -> bytes:
    return hashlib.sha512(m).digest()


def rfc8032_publickey(sk: bytes) -> bytes:
    h = H(sk)
    a = 2**254 + sum([h[i] << (i * 8) for i in range(3, 32)])
    a &= ~7
    A = scalarmult(B, a)
    return encodepoint(A)


def rfc8032_signature(m: bytes, sk: bytes, pk: bytes) -> bytes:
    h = H(sk)
    a = 2**254 + sum([h[i] << (i * 8) for i in range(3, 32)])
    a &= ~7
    prefix = h[32:]
    r = sum([H(prefix + m)[i] << (i * 8) for i in range(64)]) % l
    R = scalarmult(B, r)
    k = sum([H(encodepoint(R) + pk + m)[i] << (i * 8) for i in range(64)]) % l
    S = (r + k * a) % l
    return encodepoint(R) + bytes([(S >> (i * 8)) & 0xff for i in range(32)])


def rfc8032_checkvalid(s: bytes, m: bytes, pk: bytes) -> bool:
    if len(s) != 64 or len(pk) != 32:
        return False
    try:
        R = decodepoint(s[:32])
        A = decodepoint(pk)
        S = sum([s[32 + i] << (i * 8) for i in range(32)])
        if S >= l:
            return False
        k = sum([H(s[:32] + pk + m)[i] << (i * 8) for i in range(64)]) % l
        v1 = scalarmult(B, S)
        v2 = edwards_add(R, scalarmult(A, k))
        return v1 == v2
    except Exception:
        return False


# ============================================================================
# CryptoSigner Interface
# ============================================================================

class CryptoSigner:
    """Provides cryptographic signing and verification for evaluation receipts."""

    _has_pyca = False
    try:
        from cryptography.hazmat.primitives.asymmetric import ed25519 as pyca_ed25519  # type: ignore
        from cryptography.hazmat.primitives import serialization  # type: ignore
        _has_pyca = True
    except ImportError:
        _has_pyca = False

    @classmethod
    def generate_keypair(cls) -> Tuple[str, str]:
        """Generates (private_key_b64, public_key_b64)."""
        if cls._has_pyca:
            from cryptography.hazmat.primitives.asymmetric import ed25519  # type: ignore
            from cryptography.hazmat.primitives import serialization  # type: ignore
            priv = ed25519.Ed25519PrivateKey.generate()
            pub = priv.public_key()
            priv_bytes = priv.private_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PrivateFormat.Raw,
                encryption_algorithm=serialization.NoEncryption()
            )
            pub_bytes = pub.public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw
            )
            return base64.b64encode(priv_bytes).decode("utf-8"), base64.b64encode(pub_bytes).decode("utf-8")
        else:
            seed = os.urandom(32)
            pk = rfc8032_publickey(seed)
            return base64.b64encode(seed).decode("utf-8"), base64.b64encode(pk).decode("utf-8")

    @classmethod
    def sign(cls, message: bytes, private_key_b64: str) -> str:
        """Signs message bytes and returns base64 signature."""
        priv_bytes = base64.b64decode(private_key_b64.strip())
        if cls._has_pyca:
            from cryptography.hazmat.primitives.asymmetric import ed25519  # type: ignore
            priv = ed25519.Ed25519PrivateKey.from_private_bytes(priv_bytes)
            sig = priv.sign(message)
            return base64.b64encode(sig).decode("utf-8")
        else:
            pk = rfc8032_publickey(priv_bytes)
            sig = rfc8032_signature(message, priv_bytes, pk)
            return base64.b64encode(sig).decode("utf-8")

    @classmethod
    def verify(cls, message: bytes, signature_b64: str, public_key_b64: str) -> bool:
        """Verifies signature over message bytes using public key."""
        try:
            pub_bytes = base64.b64decode(public_key_b64.strip())
            sig_bytes = base64.b64decode(signature_b64.strip())
            if cls._has_pyca:
                from cryptography.hazmat.primitives.asymmetric import ed25519  # type: ignore
                from cryptography.exceptions import InvalidSignature  # type: ignore
                pub = ed25519.Ed25519PublicKey.from_public_bytes(pub_bytes)
                pub.verify(sig_bytes, message)
                return True
            else:
                return rfc8032_checkvalid(sig_bytes, message, pub_bytes)
        except Exception:
            return False
