import os
import base64
import pyotp
from datetime import datetime

HEX_SEED = os.getenv("HEX_SEED", "")

def hex_to_base32(hex_seed: str) -> str:
    if not hex_seed or hex_seed.strip() == "":
        return pyotp.random_base32()
    bytes_seed = bytes.fromhex(hex_seed)
    return base64.b32encode(bytes_seed).decode("utf-8")

def main():
    base32_seed = hex_to_base32(HEX_SEED)
    totp = pyotp.TOTP(base32_seed)
    current_otp = totp.now()

    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    log = f"{timestamp} - OTP: {current_otp}\n"

    with open("/app/logs/2fa.log", "a") as f:
        f.write(log)

if __name__ == "__main__":
    main()
