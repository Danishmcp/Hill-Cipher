# Hill Cipher Cryptosystem & Interactive Lab

An interactive Python implementation and educational cryptanalysis lab for the **Hill Cipher**, a classical polygraphic substitution cipher based on modular linear algebra over $\mathbb{Z}_{26}$.

Built for cybersecurity education with both a full-featured **Streamlit web application** and a lightweight **CLI**.

---

## Features

### 🖥️ Streamlit Web App (`app.py`)
- **Live Key Matrix Validator:** Computes $\det(K)$, $\det(K) \pmod{26}$, and $\gcd(\det(K), 26)$ dynamically as you edit matrix values. Shows a live "Valid" or "Invalid" badge and automatically disables the Run button when the matrix has no modular inverse.
- **Random Valid Key Generator:** Instantly generates a mathematically valid, invertible $2 \times 2$ or $3 \times 3$ key matrix at the click of a button.
- **Inverse Matrix Preview:** Displays $K$ and its modular inverse $K^{-1} \pmod{26}$ side-by-side using LaTeX notation.
- **Live Mode Toggle:** Type plaintext or ciphertext and see real-time updates without clicking a button.
- **Preset Examples Loader:** Quickly load preset keys (Valid 2x2, Invalid 2x2 with gcd=2, Valid 3x3, Known-Plaintext Attack example) to auto-fill inputs.
- **Shareable State via URL:** Key, text, and operation mode are synced to `st.query_params`, allowing shareable URLs that restore cipher state on reload.
- **Step-by-Step Visualization Tab:** Inspects the encryption or decryption pipeline block-by-block with overview tables and expandable matrix equations.
- **Animated Walkthrough Tab:** Step through blocks one-by-one with Previous/Next buttons or a slider, view highlighted cell-by-cell matrix multiplication, or use the 1-second auto-play mode with pause/stop controls.
- **Known-Plaintext Attack (KPA) Demo Tab:** Demonstrates why the Hill Cipher is cryptographically weak. Automatically recovers the key matrix from known plaintext/ciphertext pairs using modular matrix inversion:
  $$K \equiv C \cdot P^{-1} \pmod{26}$$
- **Caesar vs. Hill Comparison Tab:** Side-by-side letter frequency bar charts and standard deviation statistics contrasting monoalphabetic shift ciphers with polygraphic linear diffusion.
- **Secure Chat Simulator Tab (Alice, Bob & Eve):** Interactive 3-column chat simulation where Alice sends encrypted messages to Bob, Eve eavesdrops on the ciphertext, and Eve can mount a known-plaintext attack to recover the key and decrypt all intercepted messages.
- **Key Space Explorer Tab:** Brute-forces all $26^4 = 456{,}976$ possible $2\times 2$ keys (cached), displays key counts (157,248 valid keys / 34.4%), renders an interactive Plotly heatmap over $(a, d)$ pairs with $b$ and $c$ sliders, and includes a full $1 \dots 25 \pmod{26}$ modular inverse table.
- **Practice Quiz Tab:** Interactive quiz mode with 2x2 and 3x3 difficulty levels, Encrypt and Decrypt question types, live score and streak tracking, and full step-by-step solutions upon answering.
- **Image Encryption Tab (mod 256):** Encrypts and decrypts grayscale images using Hill Cipher arithmetic modulo 256 (where odd determinants ensure invertibility), demonstrating the ECB-style pattern leakage weakness.
- **Session History Log:** Keeps an auditable log of past operations with timestamps, keys, inputs, and outputs, with a one-click "Clear History" button.
- **Result Actions:** Export results directly as `.txt` files and perform one-click "Verify Round Trip" tests.
- **Reference Table & Educational Guides:** Interactive $A=0 \dots Z=25$ lookup table, mathematical derivations, and cryptanalysis explainers.

### ⚙️ Core Engine (`hill_cipher.py`)
- Classical Hill Cipher encryption & decryption with automatic sanitization and padding.
- Strict input cleaning and validation in `decrypt()` to catch invalid block lengths.
- Clean separation between cryptographic logic and UI components.
- Exact integer determinants for $2\times 2$ and $3\times 3$ matrices.
- Key space analysis (`count_valid_2x2_keys`, `key_validity_grid`, `mod_inverse_table`).
- Quiz question generator and answer validator.
- Mod-256 grayscale image encryption and decryption engine.
- Compatible with Python $\ge$ 3.11 and managed with `uv`.

---

## Project Structure

```
hill_cipher/
├── app.py                     # Interactive Streamlit Web Application
├── hill_cipher.py             # Core mathematical & cryptanalytic engine
├── main.py                    # Standalone CLI application
├── tests/
│   └── test_hill_cipher.py    # Automated unit tests (pytest)
├── pyproject.toml             # Project metadata, dependencies & pytest config
└── README.md                  # Project documentation
```

---

## Getting Started

### Prerequisites
Make sure [uv](https://github.com/astral-sh/uv) or Python 3.11+ is installed.

### Installation
Dependencies are automatically managed by `uv`. To sync the environment:
```bash
uv sync
```

---

## How to Run

### 1. Launch the Streamlit Interactive Web App (Recommended)
```bash
uv run streamlit run app.py
```
Open your browser at the displayed local URL (typically `http://localhost:8501`).

### 2. Run the CLI Version
```bash
uv run python main.py
```

### 3. Run Automated Tests
```bash
uv run pytest -v
```

---

## Known-Good Test Example

- **Key Matrix (2x2):**
  $$\begin{bmatrix} 3 & 3 \\ 2 & 5 \end{bmatrix}$$
- **Plaintext:** `CIPHERS`
- **Encrypted Ciphertext:** `ESONLPTV`
- **Decrypted Plaintext:** `CIPHERSX` (padded with `X` to complete the 2-letter block).

---

## Cryptographic Considerations

1. **Coprime Condition:** A matrix $K$ is a valid Hill Cipher key if and only if $\gcd(\det(K) \pmod{26}, 26) = 1$. Since $26 = 2 \times 13$, the determinant must be coprime with both 2 and 13.
2. **Linear Vulnerability:** Because the cipher is linear ($C \equiv K \cdot P \pmod{26}$), an adversary possessing only $n$ known plaintext blocks can solve for $K$ via $K \equiv C \cdot P^{-1} \pmod{26}$.
3. **Diffusion:** The Hill Cipher provides polygraphic diffusion across each block of size $n$, effectively flattening individual letter frequency spikes that plague simple substitution ciphers like Caesar.

---

## Author

Danish