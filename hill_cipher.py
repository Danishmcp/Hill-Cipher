

import itertools
import math
import numpy as np


def clean_text(text: str) -> str:
    
    if not text:
        return ""
    text = text.upper().replace(" ", "")
    return "".join(filter(str.isalpha, text))


def text_to_numbers(text: str) -> list[int]:
    
    return [ord(char) - ord("A") for char in text]


def numbers_to_text(numbers) -> str:
    
    return "".join(chr(int(num) % 26 + ord("A")) for num in numbers)


def mod_inverse(a: int, m: int = 26) -> int:
    
    a = a % m
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    raise ValueError(f"Modular inverse does not exist for {a} modulo {m} (gcd({a}, {m}) != 1)")


def integer_det(matrix: np.ndarray) -> int:
    
    mat = np.asarray(matrix, dtype=int)
    n = mat.shape[0]
    if n == 2:
        return int(mat[0, 0] * mat[1, 1] - mat[0, 1] * mat[1, 0])
    elif n == 3:
        return int(
            mat[0, 0] * (mat[1, 1] * mat[2, 2] - mat[1, 2] * mat[2, 1])
            - mat[0, 1] * (mat[1, 0] * mat[2, 2] - mat[1, 2] * mat[2, 0])
            + mat[0, 2] * (mat[1, 0] * mat[2, 1] - mat[1, 1] * mat[2, 0])
        )
    else:
        return int(round(float(np.linalg.det(mat))))


def is_valid_key(matrix: np.ndarray, mod: int = 26) -> tuple[bool, int, int, int, str]:
    
    mat = np.asarray(matrix)
    if mat.ndim != 2 or mat.shape[0] != mat.shape[1]:
        return False, 0, 0, 0, "Matrix must be square."

    n = mat.shape[0]
    if n not in (2, 3):
        return False, 0, 0, 0, f"Unsupported matrix size {n}x{n}. Only 2x2 and 3x3 are supported."

    det = integer_det(mat)
    det_mod = det % mod
    g = math.gcd(det_mod, mod)

    if g == 1:
        return True, det, det_mod, g, f"Valid key: det = {det} ≡ {det_mod} (mod {mod}), gcd({det_mod}, {mod}) = 1."

    if det_mod == 0:
        reason = f"Invalid key: det = {det} ≡ 0 (mod {mod}). The matrix is singular."
    elif g % 2 == 0:
        reason = f"Invalid key: det = {det} ≡ {det_mod} (mod {mod}) shares factor 2 with {mod} (gcd = {g})."
    elif g % 13 == 0:
        reason = f"Invalid key: det = {det} ≡ {det_mod} (mod {mod}) shares factor 13 with {mod} (gcd = {g})."
    else:
        reason = f"Invalid key: gcd({det_mod}, {mod}) = {g} != 1. Modular inverse does not exist."

    return False, det, det_mod, g, reason


def matrix_mod_inverse(matrix: np.ndarray, mod: int = 26) -> np.ndarray:
    
    mat = np.asarray(matrix, dtype=int)
    n = mat.shape[0]
    det = integer_det(mat)
    det_mod = det % mod

    det_inv = mod_inverse(det_mod, mod)

    
    matrix_minor = np.zeros(mat.shape, dtype=int)
    for i in range(n):
        for j in range(n):
            minor = np.delete(np.delete(mat, i, axis=0), j, axis=1)
            matrix_minor[i][j] = ((-1) ** (i + j)) * integer_det(minor)

    adjugate = matrix_minor.T
    inverse_matrix = (det_inv * adjugate) % mod
    return inverse_matrix.astype(int)


def generate_valid_key(n: int = 2, mod: int = 26) -> np.ndarray:
    
    if n not in (2, 3):
        raise ValueError("Only matrix sizes 2 and 3 are supported.")

    while True:
        candidate = np.random.randint(0, mod, size=(n, n))
        valid, _, _, _, _ = is_valid_key(candidate, mod)
        if valid:
            return candidate.astype(int)


def encrypt(plaintext: str, key_matrix: np.ndarray) -> str:
    
    key_matrix = np.asarray(key_matrix, dtype=int)
    n = key_matrix.shape[0]
    plaintext = clean_text(plaintext)

    if not plaintext:
        return ""

    
    while len(plaintext) % n != 0:
        plaintext += "X"

    numbers = text_to_numbers(plaintext)
    ciphertext = ""

    for i in range(0, len(numbers), n):
        block = np.array(numbers[i : i + n])
        encrypted_block = key_matrix.dot(block) % 26
        ciphertext += numbers_to_text(encrypted_block)

    return ciphertext


def decrypt(ciphertext: str, key_matrix: np.ndarray) -> str:
    
    key_matrix = np.asarray(key_matrix, dtype=int)
    n = key_matrix.shape[0]

    ciphertext = clean_text(ciphertext)
    if not ciphertext:
        raise ValueError("Ciphertext cannot be empty.")

    if len(ciphertext) % n != 0:
        raise ValueError(
            f"Ciphertext length ({len(ciphertext)}) must be a multiple of the block size ({n})."
        )

    inverse_key = matrix_mod_inverse(key_matrix, 26)
    numbers = text_to_numbers(ciphertext)
    plaintext = ""

    for i in range(0, len(numbers), n):
        block = np.array(numbers[i : i + n])
        decrypted_block = inverse_key.dot(block) % 26
        plaintext += numbers_to_text(decrypted_block)

    return plaintext


def get_step_breakdown(text: str, key_matrix: np.ndarray, mode: str = "encrypt") -> list[dict]:
    
    key_matrix = np.asarray(key_matrix, dtype=int)
    n = key_matrix.shape[0]
    is_encrypt = mode.lower() == "encrypt"

    cleaned = clean_text(text)
    if not cleaned:
        return []

    if is_encrypt:
        active_matrix = key_matrix
        matrix_label = "K"
        while len(cleaned) % n != 0:
            cleaned += "X"
    else:
        active_matrix = matrix_mod_inverse(key_matrix, 26)
        matrix_label = "K⁻¹"
        if len(cleaned) % n != 0:
            raise ValueError(
                f"Ciphertext length ({len(cleaned)}) must be a multiple of the block size ({n})."
            )

    numbers = text_to_numbers(cleaned)
    steps = []

    for idx, i in enumerate(range(0, len(numbers), n), start=1):
        block_chars = cleaned[i : i + n]
        block_vec = np.array(numbers[i : i + n])
        raw_product = active_matrix.dot(block_vec)
        mod_vec = raw_product % 26
        out_chars = numbers_to_text(mod_vec)

        in_vec_str = "[" + ", ".join(map(str, block_vec)) + "]"
        raw_vec_str = "[" + ", ".join(map(str, raw_product)) + "]"
        mod_vec_str = "[" + ", ".join(map(str, mod_vec)) + "]"

        formula = f"{matrix_label} × {in_vec_str}ᵀ = {raw_vec_str} ≡ {mod_vec_str} (mod 26)"

        steps.append(
            {
                "block_index": idx,
                "input_chars": block_chars,
                "input_nums": block_vec.tolist(),
                "raw_product": raw_product.tolist(),
                "mod_nums": mod_vec.tolist(),
                "output_chars": out_chars,
                "formula": formula,
            }
        )

    return steps


def recover_key_from_pair(plaintext: str, ciphertext: str, n: int = 2) -> dict:
    
    clean_p = clean_text(plaintext)
    clean_c = clean_text(ciphertext)

    if len(clean_p) != len(clean_c):
        return {
            "success": False,
            "error": f"Plaintext length ({len(clean_p)}) and ciphertext length ({len(clean_c)}) must be equal.",
        }

    if len(clean_p) < n * n:
        return {
            "success": False,
            "error": f"At least {n * n} characters ({n} blocks of size {n}) are required to recover a {n}x{n} key.",
        }

    
    total_blocks = len(clean_p) // n
    p_nums = text_to_numbers(clean_p[: total_blocks * n])
    c_nums = text_to_numbers(clean_c[: total_blocks * n])

    p_vectors = [np.array(p_nums[i : i + n]) for i in range(0, len(p_nums), n)]
    c_vectors = [np.array(c_nums[i : i + n]) for i in range(0, len(c_nums), n)]

    
    found_combo = None
    p_sub = None
    c_sub = None
    p_det = 0
    p_det_mod = 0

    for combo in itertools.combinations(range(total_blocks), n):
        candidate_p = np.column_stack([p_vectors[idx] for idx in combo])
        det = integer_det(candidate_p)
        det_mod = det % 26
        if math.gcd(det_mod, 26) == 1:
            found_combo = combo
            p_sub = candidate_p
            c_sub = np.column_stack([c_vectors[idx] for idx in combo])
            p_det = det
            p_det_mod = det_mod
            break

    if found_combo is None:
        return {
            "success": False,
            "error": (
                f"None of the block combinations formed an invertible plaintext matrix modulo 26. "
                f"All tested {n}x{n} submatrices have gcd(det(P), 26) != 1."
            ),
        }

    
    p_inv = matrix_mod_inverse(p_sub, 26)

    
    recovered_key = (c_sub.dot(p_inv)) % 26
    recovered_key = recovered_key.astype(int)

    
    test_cipher = encrypt(clean_p, recovered_key)
    matches = test_cipher.startswith(clean_c)

    return {
        "success": True,
        "key_matrix": recovered_key,
        "selected_blocks": [int(idx + 1) for idx in found_combo],
        "p_matrix": p_sub,
        "c_matrix": c_sub,
        "p_det": p_det,
        "p_det_mod26": p_det_mod,
        "p_inv_matrix": p_inv,
        "matches": matches,
    }


def caesar_encrypt(text: str, shift: int = 3) -> str:
    
    cleaned = clean_text(text)
    if not cleaned:
        return ""
    return "".join(chr((ord(char) - ord("A") + shift) % 26 + ord("A")) for char in cleaned)


def letter_frequencies(text: str) -> dict[str, int]:
    
    cleaned = clean_text(text)
    counts = {chr(ord("A") + i): 0 for i in range(26)}
    for char in cleaned:
        counts[char] += 1
    return counts






def count_valid_2x2_keys(mod: int = 26) -> int:
    
    count = 0
    for a in range(mod):
        for b in range(mod):
            for c in range(mod):
                for d in range(mod):
                    det = (a * d - b * c) % mod
                    if math.gcd(det, mod) == 1:
                        count += 1
    return count


def key_validity_grid(b: int, c: int, mod: int = 26) -> np.ndarray:
    
    grid = np.zeros((mod, mod), dtype=bool)
    for a in range(mod):
        for d in range(mod):
            det = (a * d - b * c) % mod
            if math.gcd(det, mod) == 1:
                grid[a, d] = True
    return grid


def mod_inverse_table(mod: int = 26) -> list[dict]:
    
    table = []
    for x in range(1, mod):
        try:
            inv = mod_inverse(x, mod)
            table.append({"number": x, "inverse": inv, "has_inverse": True})
        except ValueError:
            table.append({"number": x, "inverse": None, "has_inverse": False})
    return table






_QUIZ_WORDS = [
    "MATH", "CODE", "HILL", "KEYS", "TEXT", "LOCK", "BYTE", "DATA",
    "FLAG", "HACK", "NODE", "BITS", "SAFE", "AXIS", "CUBE", "FROG",
    "JUMP", "LAMP", "QUIZ", "RUST", "WAVE", "ZERO", "GRID", "LION",
    "MASK", "RING", "SILK", "VOID", "WREN", "YAWN",
    
    "ACTING", "BRIDGE", "CRYPTO", "DESIGN", "ENABLE", "FALCON",
    "GLOBAL", "MATRIX", "KNIGHT", "CASTLE", "PLAINS", "REVOLT",
]


def generate_quiz_question(n: int = 2, mode: str = "encrypt") -> dict:
    
    key = generate_valid_key(n)
    word_len = 2 * n  

    
    candidates = [w for w in _QUIZ_WORDS if len(w) == word_len]
    if not candidates:
        
        word = "".join(chr(np.random.randint(0, 26) + ord("A")) for _ in range(word_len))
    else:
        word = candidates[np.random.randint(0, len(candidates))]

    if mode.lower() == "encrypt":
        answer = encrypt(word, key)
        steps = get_step_breakdown(word, key, mode="encrypt")
        return {
            "key_matrix": key,
            "input_text": word,
            "expected_answer": answer,
            "mode": "encrypt",
            "steps": steps,
        }
    else:
        ct = encrypt(word, key)
        steps = get_step_breakdown(ct, key, mode="decrypt")
        return {
            "key_matrix": key,
            "input_text": ct,
            "expected_answer": word,
            "mode": "decrypt",
            "steps": steps,
        }


def check_quiz_answer(user_answer: str, expected: str) -> bool:
    
    return clean_text(user_answer) == clean_text(expected)






def is_valid_key_mod256(matrix: np.ndarray) -> tuple[bool, int, str]:
    
    mat = np.asarray(matrix, dtype=int)
    det = integer_det(mat)
    det_mod = det % 256
    if det_mod % 2 == 0:
        return False, det_mod, f"Invalid: det = {det_mod} (mod 256) is even - not coprime with 256."
    return True, det_mod, f"Valid: det = {det_mod} (mod 256) is odd - coprime with 256."


def generate_valid_key_mod256(n: int = 2) -> np.ndarray:
    
    while True:
        candidate = np.random.randint(0, 256, size=(n, n))
        valid, _, _ = is_valid_key_mod256(candidate)
        if valid:
            return candidate.astype(int)


def encrypt_image_pixels(pixels: np.ndarray, key_matrix: np.ndarray) -> np.ndarray:
    
    key_matrix = np.asarray(key_matrix, dtype=int)
    n = key_matrix.shape[0]
    px = pixels.copy().astype(int)

    
    remainder = len(px) % n
    if remainder != 0:
        px = np.concatenate([px, np.zeros(n - remainder, dtype=int)])

    result = np.zeros_like(px)
    for i in range(0, len(px), n):
        block = px[i : i + n]
        result[i : i + n] = key_matrix.dot(block) % 256

    return result


def decrypt_image_pixels(pixels: np.ndarray, key_matrix: np.ndarray) -> np.ndarray:
    
    key_matrix = np.asarray(key_matrix, dtype=int)
    inv_key = matrix_mod_inverse(key_matrix, 256)
    return encrypt_image_pixels(pixels, inv_key)

