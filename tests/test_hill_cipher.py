import numpy as np
import pytest
from hill_cipher import (
    clean_text,
    text_to_numbers,
    numbers_to_text,
    mod_inverse,
    matrix_mod_inverse,
    is_valid_key,
    generate_valid_key,
    encrypt,
    decrypt,
    get_step_breakdown,
    recover_key_from_pair,
    caesar_encrypt,
    letter_frequencies,
)


def test_clean_text():
    assert clean_text("Hello, World!") == "HELLOWORLD"
    assert clean_text("123 @#$ abc") == "ABC"
    assert clean_text("") == ""


def test_text_and_number_conversions():
    nums = text_to_numbers("ABCZ")
    assert nums == [0, 1, 2, 25]
    assert numbers_to_text([0, 1, 2, 25]) == "ABCZ"
    assert numbers_to_text([26, 27]) == "AB"


def test_mod_inverse():
    assert mod_inverse(3, 26) == 9
    assert mod_inverse(9, 26) == 3
    assert mod_inverse(7, 26) == 15
    with pytest.raises(ValueError, match="Modular inverse does not exist"):
        mod_inverse(2, 26)
    with pytest.raises(ValueError, match="Modular inverse does not exist"):
        mod_inverse(13, 26)


def test_known_good_2x2():
    key = np.array([[3, 3], [2, 5]])
    plaintext = "CIPHERS"
    ciphertext = encrypt(plaintext, key)
    assert ciphertext == "ESONLPTV"

    decrypted = decrypt(ciphertext, key)
    assert decrypted == "CIPHERSX"


def test_decrypt_bug_fix_cleaning_and_validation():
    key = np.array([[3, 3], [2, 5]])

    # Ciphertext with spaces, lowercase, and punctuation must be cleaned and decrypted
    dirty_ciphertext = "e s o n ! l p t v ."
    assert decrypt(dirty_ciphertext, key) == "CIPHERSX"

    # Odd length ciphertext for 2x2 should raise ValueError
    with pytest.raises(ValueError, match="multiple of the block size"):
        decrypt("ESONLPT", key)

    # Empty ciphertext should raise ValueError
    with pytest.raises(ValueError, match="cannot be empty"):
        decrypt("", key)
    with pytest.raises(ValueError, match="cannot be empty"):
        decrypt("   !@#  ", key)


def test_3x3_round_trip():
    # Valid 3x3 key: det = 1 or coprime with 26
    # Example key: [[6, 24, 1], [13, 16, 10], [20, 17, 15]]
    # Let's use a known invertible 3x3 key
    key = np.array([
        [6, 24, 1],
        [13, 16, 10],
        [20, 17, 15]
    ])
    valid, det, det_mod, g, _ = is_valid_key(key)
    assert valid, f"Expected valid key, got gcd={g}, det_mod={det_mod}"

    text = "ACTING"
    cipher = encrypt(text, key)
    dec = decrypt(cipher, key)
    assert dec == "ACTING"


def test_is_valid_key():
    # Valid 2x2
    valid_key = np.array([[3, 3], [2, 5]])
    valid, det, det_mod, g, _ = is_valid_key(valid_key)
    assert valid is True
    assert g == 1

    # Invalid: det % 26 has factor 2
    even_key = np.array([[2, 3], [4, 5]])  # det = -2 ≡ 24, gcd(24, 26) = 2
    valid, det, det_mod, g, _ = is_valid_key(even_key)
    assert valid is False
    assert g == 2

    # Invalid: singular matrix det = 0
    singular_key = np.array([[1, 2], [2, 4]])
    valid, det, det_mod, g, _ = is_valid_key(singular_key)
    assert valid is False


def test_generate_valid_key():
    for _ in range(5):
        k2 = generate_valid_key(2)
        valid2, _, _, g2, _ = is_valid_key(k2)
        assert valid2 and g2 == 1

        k3 = generate_valid_key(3)
        valid3, _, _, g3, _ = is_valid_key(k3)
        assert valid3 and g3 == 1


def test_step_breakdown():
    key = np.array([[3, 3], [2, 5]])
    steps = get_step_breakdown("HI", key, mode="encrypt")
    assert len(steps) == 1
    # H=7, I=8 -> K * [7, 8]^T = [3*7 + 3*8, 2*7 + 5*8] = [45, 54] ≡ [19, 2] (mod 26) -> T=19, C=2
    assert steps[0]["input_chars"] == "HI"
    assert steps[0]["input_nums"] == [7, 8]
    assert steps[0]["raw_product"] == [45, 54]
    assert steps[0]["mod_nums"] == [19, 2]
    assert steps[0]["output_chars"] == "TC"

    # Decrypt step breakdown
    dec_steps = get_step_breakdown("TC", key, mode="decrypt")
    assert len(dec_steps) == 1
    assert dec_steps[0]["output_chars"] == "HI"


def test_known_plaintext_attack_recovery():
    key = np.array([[3, 3], [2, 5]])
    plaintext = "CIPHERSX"
    ciphertext = encrypt(plaintext, key)

    result = recover_key_from_pair(plaintext, ciphertext, n=2)
    assert result["success"] is True
    recovered = result["key_matrix"]
    assert np.array_equal(recovered % 26, key % 26)
    assert result["matches"] is True


def test_caesar_encrypt_and_frequencies():
    plain = "HELLO"
    cipher = caesar_encrypt(plain, shift=3)
    assert cipher == "KHOOR"

    freqs = letter_frequencies("AABBBCCCC")
    assert freqs["A"] == 2
    assert freqs["B"] == 3
    assert freqs["C"] == 4
    assert freqs["D"] == 0


def test_key_space_count():
    from hill_cipher import count_valid_2x2_keys, key_validity_grid, mod_inverse_table
    count = count_valid_2x2_keys(26)
    assert count == 157248

    # Grid check
    grid = key_validity_grid(3, 2, 26)
    assert grid.shape == (26, 26)
    assert grid.dtype == bool

    # Mod inverse table check (1..25 mod 26)
    table = mod_inverse_table(26)
    assert len(table) == 25
    entry3 = next(item for item in table if item["number"] == 3)
    assert entry3["inverse"] == 9
    assert entry3["has_inverse"] is True
    entry2 = next(item for item in table if item["number"] == 2)
    assert entry2["has_inverse"] is False


def test_quiz_helpers():
    from hill_cipher import generate_quiz_question, check_quiz_answer

    # 2x2 encrypt
    q2_enc = generate_quiz_question(2, mode="encrypt")
    assert q2_enc["key_matrix"].shape == (2, 2)
    assert len(q2_enc["input_text"]) == 4
    assert check_quiz_answer(q2_enc["expected_answer"], q2_enc["expected_answer"])
    assert check_quiz_answer(q2_enc["expected_answer"].lower(), q2_enc["expected_answer"])
    assert not check_quiz_answer("WRONG", q2_enc["expected_answer"])

    # 3x3 decrypt
    q3_dec = generate_quiz_question(3, mode="decrypt")
    assert q3_dec["key_matrix"].shape == (3, 3)
    assert len(q3_dec["input_text"]) == 6
    assert check_quiz_answer(q3_dec["expected_answer"], q3_dec["expected_answer"])


def test_image_mod256_encryption_round_trip():
    from hill_cipher import (
        generate_valid_key_mod256,
        is_valid_key_mod256,
        encrypt_image_pixels,
        decrypt_image_pixels,
    )
    key = generate_valid_key_mod256(2)
    valid, det_mod, _ = is_valid_key_mod256(key)
    assert valid is True
    assert det_mod % 2 == 1  # odd determinant required for mod 256

    # Test pixels (0-255)
    pixels = np.array([0, 15, 128, 200, 255, 42], dtype=np.uint8)
    enc = encrypt_image_pixels(pixels, key)
    dec = decrypt_image_pixels(enc, key)
    assert np.array_equal(pixels, dec)

    # Test 3x3 image key
    key3 = generate_valid_key_mod256(3)
    enc3 = encrypt_image_pixels(pixels, key3)
    dec3 = decrypt_image_pixels(enc3, key3)
    assert np.array_equal(pixels, dec3)

