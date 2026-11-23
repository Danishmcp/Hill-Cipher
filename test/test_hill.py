import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
from hill_cipher import encrypt, decrypt

# 2x2 key matrix example
key = np.array([[3, 3], [2, 5]])

plaintext = "HELLO"
ciphertext = encrypt(plaintext, key)
print("Encrypted:", ciphertext)

decrypted = decrypt(ciphertext, key)
print("Decrypted:", decrypted)