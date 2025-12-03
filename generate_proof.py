#!/usr/bin/env python3
"""
generate_proof.py

Signs the latest commit hash (ASCII) using student_private.pem (RSA-PSS SHA256, max salt),
then encrypts the signature using instructor_public.pem (RSA-OAEP SHA256).
Outputs:
 - Commit Hash: (printed)
 - Encrypted Signature (base64 single-line): printed
"""

import base64
import sys
from pathlib import Path
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

# Paths (adjust if your keys are in different paths)
PRIVATE_KEY_PATH = Path("student_private.pem")
INSTRUCTOR_PUB_PATH = Path("instructor_public.pem")

def load_private_key(path: Path):
    data = path.read_bytes()
    return serialization.load_pem_private_key(data, password=None)

def load_public_key(path: Path):
    data = path.read_bytes()
    return serialization.load_pem_public_key(data)

def sign_message(message: str, private_key) -> bytes:
    """
    Sign ASCII commit hash using RSA-PSS with SHA-256 and maximum salt length.
    """
    msg_bytes = message.encode("utf-8")  # ASCII/UTF-8
    signature = private_key.sign(
        msg_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature

def encrypt_with_public_key(data: bytes, public_key) -> bytes:
    """
    Encrypt data using RSA-OAEP with SHA-256 (MGF1 with SHA-256).
    """
    ciphertext = public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return ciphertext

def main(commit_hash: str):
    # Validate commit hash length
    if not isinstance(commit_hash, str) or len(commit_hash) != 40:
        print("ERROR: commit_hash must be a 40-character hex string.", file=sys.stderr)
        sys.exit(2)

    # Load keys
    if not PRIVATE_KEY_PATH.exists():
        print(f"ERROR: private key not found at {PRIVATE_KEY_PATH}", file=sys.stderr)
        sys.exit(2)
    if not INSTRUCTOR_PUB_PATH.exists():
        print(f"ERROR: instructor public key not found at {INSTRUCTOR_PUB_PATH}", file=sys.stderr)
        sys.exit(2)

    private_key = load_private_key(PRIVATE_KEY_PATH)
    instructor_pub = load_public_key(INSTRUCTOR_PUB_PATH)

    # Sign
    signature = sign_message(commit_hash, private_key)

    # Encrypt the signature with instructor public key
    encrypted = encrypt_with_public_key(signature, instructor_pub)

    # Base64 encode the encrypted signature to a single line
    encrypted_b64 = base64.b64encode(encrypted).decode("ascii")

    # Output
    print("Commit Hash:", commit_hash)
    print("Encrypted Signature (base64):")
    print(encrypted_b64)

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        commit = sys.argv[1]
    else:
        # try to read from git
        import subprocess
        try:
            commit = subprocess.check_output(["git", "log", "-1", "--format=%H"]).decode().strip()
        except Exception as e:
            print("ERROR: failed to read commit hash from git. Provide it as an argument.", file=sys.stderr)
            sys.exit(2)
    main(commit)
