from hill_cipher import encrypt, decrypt
import numpy as np

def main():
    print("=== Hill Cipher Implementation ===")
    
    n = int(input("Key matrix size (2 or 3): "))
    print(f"Enter {n}x{n} key matrix row by row (space-separated):")
    key = []
    for i in range(n):
        row = list(map(int, input().split()))
        key.append(row)
    key_matrix = np.array(key)

    choice = input("Encrypt (E) or Decrypt (D)? ").upper()
    text = input("Enter text: ")

    if choice == 'E':
        result = encrypt(text, key_matrix)
        print("Encrypted Text:", result)
    else:
        result = decrypt(text, key_matrix)
        print("Decrypted Text:", result)

if __name__ == "__main__":
    main()
