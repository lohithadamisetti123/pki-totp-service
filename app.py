from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import base64
import pyotp
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
import os
import time
import binascii

app = FastAPI()

SEED_PATH = "data/seed.txt"
PRIVATE_KEY_PATH = "keys/student_private.pem"


class EncryptedSeed(BaseModel):
    encrypted_seed: str


class VerifyCode(BaseModel):
    code: str


@app.get("/")
def home():
    return {"message": "PKI-TOTP Service is running!"}


@app.post("/decrypt-seed")
def decrypt_seed(data: EncryptedSeed):
    try:
        # Load private key
        with open(PRIVATE_KEY_PATH, "rb") as key_file:
            private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None
            )

        # Decrypt encrypted seed
        cipher = base64.b64decode(data.encrypted_seed)
        seed_hex = private_key.decrypt(
            cipher,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        ).decode()

        # Validate hex length
        if len(seed_hex) != 64:
            raise ValueError("Invalid seed format")

        # Convert hex seed to base32 (required by pyotp)
        seed_bytes = binascii.unhexlify(seed_hex)
        seed_base32 = base64.b32encode(seed_bytes).decode()

        # Save base32 seed
        os.makedirs(os.path.dirname(SEED_PATH), exist_ok=True)
        with open(SEED_PATH, "w") as f:
            f.write(seed_base32)

        return {"status": "ok"}

    except Exception:
        raise HTTPException(status_code=500, detail="Decryption failed")


@app.get("/generate-2fa")
def generate_2fa():
    if not os.path.exists(SEED_PATH):
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

    with open(SEED_PATH, "r") as f:
        seed_base32 = f.read().strip()

    totp = pyotp.TOTP(seed_base32)
    code = totp.now()
    valid_for = 30 - (int(time.time()) % 30)

    return {"code": code, "valid_for": valid_for}


@app.post("/verify-2fa")
def verify_2fa(data: VerifyCode):
    if not data.code:
        raise HTTPException(status_code=400, detail="Missing code")

    if not os.path.exists(SEED_PATH):
        raise HTTPException(status_code=500, detail="Seed not decrypted yet")

    with open(SEED_PATH, "r") as f:
        seed_base32 = f.read().strip()

    totp = pyotp.TOTP(seed_base32)
    valid = totp.verify(data.code, valid_window=1)

    return {"valid": valid}
@app.get("/latest-2fa")
def latest_2fa():
    path = "/cron/last_code.txt"   # cron volume location

    if not os.path.exists(path):
        raise HTTPException(status_code=500, detail="last_code.txt not found")

    try:
        with open(path, "r") as f:
            lines = f.readlines()
            last_line = lines[-1].strip()
            code = last_line.split(":")[-1].strip()  # extract 6-digit OTP
            return {"latest_otp": code}
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to read last OTP")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

