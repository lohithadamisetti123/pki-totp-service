#!/usr/bin/env python3
import os
from datetime import datetime
import pyotp
import base64

SEED_PATH = "/data/seed.txt"

def hex_to_base32(hex_seed):
    seed_bytes = bytes.fromhex(hex_seed)
    return base64.b32encode(seed_bytes).decode('utf-8').rstrip('=')

try:
    with open(SEED_PATH, "r") as f:
        hex_seed = f.read().strip()
except FileNotFoundError:
    print("seed.txt not found")
    exit(1)

base32_seed = hex_to_base32(hex_seed)
totp = pyotp.TOTP(base32_seed)
code = totp.now()

timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
print(f"{timestamp} - 2FA Code: {code}")
