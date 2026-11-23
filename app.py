"""Streamlit Web Application for Interactive Hill Cipher Exploration & Cryptanalysis.

Features (original):
- Encrypt & Decrypt with live key validity analysis and matrix inversion
- Random valid key generator for 2x2 and 3x3 matrices
- Block-by-block step-by-step mathematical breakdown
- Known-plaintext attack demonstration with automatic key recovery
- Caesar vs. Hill cipher letter frequency comparison
- Persistent session history and exportable results
- Letter-to-number reference guide and mathematical explanations

Features (Round 1 additions):
- Animated Walkthrough: slider/Previous/Next/Auto-play through blocks
- Live encryption mode: output updates as user types
- Alice, Bob & Eve Secure Chat Simulator with KPA attack
- Key Space Explorer: brute-force metrics, interactive heatmap, inverse table

Features (Round 2 additions):
- Practice Quiz mode with score and streak tracking
- Preset example loader dropdown
- Shareable state via st.query_params
- Image encryption tab (mod 256) with ECB-weakness explanation
"""

import time
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from hill_cipher import (
    caesar_encrypt,
    check_quiz_answer,
    clean_text,
    count_valid_2x2_keys,
    decrypt,
    decrypt_image_pixels,
    encrypt,
    encrypt_image_pixels,
    generate_quiz_question,
    generate_valid_key,
    generate_valid_key_mod256,
    get_step_breakdown,
    is_valid_key,
    is_valid_key_mod256,
    key_validity_grid,
    letter_frequencies,
    matrix_mod_inverse,
    mod_inverse_table,
    recover_key_from_pair,
)

# Page configuration
st.set_page_config(
    page_title="Hill Cipher Suite",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ===========================================================================
# Helper: LaTeX matrix formatter
# ===========================================================================
def matrix_to_latex(mat: np.ndarray) -> str:
    """Format a numpy 2D array as a LaTeX bmatrix."""
    mat = np.asarray(mat, dtype=int)
    rows_str = [" & ".join(map(str, row)) for row in mat]
    return r"\begin{bmatrix} " + r" \\ ".join(rows_str) + r" \end{bmatrix}"


# ===========================================================================
# Session State Initialization
# ===========================================================================
DEFAULT_2X2 = [[3, 3], [2, 5]]
DEFAULT_3X3 = [[6, 24, 1], [13, 16, 10], [20, 17, 15]]

if "matrix_size" not in st.session_state:
    st.session_state["matrix_size"] = 2

for _i in range(3):
    for _j in range(3):
        _k = f"k_{_i}_{_j}"
        if _k not in st.session_state:
            if _i < 2 and _j < 2:
                st.session_state[_k] = DEFAULT_2X2[_i][_j]
            else:
                st.session_state[_k] = DEFAULT_3X3[_i][_j]

if "history" not in st.session_state:
    st.session_state["history"] = []
if "last_op" not in st.session_state:
    st.session_state["last_op"] = None

# Chat simulator state
if "chat_log" not in st.session_state:
    st.session_state["chat_log"] = []
if "chat_key" not in st.session_state:
    st.session_state["chat_key"] = None
if "chat_n" not in st.session_state:
    st.session_state["chat_n"] = 2

# Animated walkthrough state
if "anim_block" not in st.session_state:
    st.session_state["anim_block"] = 0
if "anim_playing" not in st.session_state:
    st.session_state["anim_playing"] = False

# Quiz state
if "quiz_question" not in st.session_state:
    st.session_state["quiz_question"] = None
if "quiz_score" not in st.session_state:
    st.session_state["quiz_score"] = 0
if "quiz_streak" not in st.session_state:
    st.session_state["quiz_streak"] = 0
if "quiz_total" not in st.session_state:
    st.session_state["quiz_total"] = 0
if "quiz_answered" not in st.session_state:
    st.session_state["quiz_answered"] = False

# ===========================================================================
# Shareable state via query_params (Round 2, Feature 7)
# ===========================================================================
qp = st.query_params
if "qp_loaded" not in st.session_state:
    st.session_state["qp_loaded"] = True
    if "key" in qp:
        try:
            import json
            key_list = json.loads(qp["key"])
            sz = len(key_list)
            st.session_state["matrix_size"] = sz
            for ri, row in enumerate(key_list):
                for ci, val in enumerate(row):
                    st.session_state[f"k_{ri}_{ci}"] = int(val)
        except Exception:
            pass
    if "text" in qp:
        st.session_state["preset_text"] = qp["text"]
        st.session_state["enc_text_input"] = qp["text"]
    if "mode" in qp:
        st.session_state["enc_mode"] = qp["mode"]

# ===========================================================================
# Sidebar: Key Matrix Configuration
# ===========================================================================
st.sidebar.title("🔐 Key Configuration")

# --- Preset Examples (Round 2, Feature 6) ---
PRESETS = {
    "(Select a preset)": None,
    "Valid 2x2 — [[3,3],[2,5]]": {"size": 2, "key": [[3, 3], [2, 5]], "text": "CIPHERS", "mode": "Encrypt"},
    "Invalid 2x2 — gcd=2": {"size": 2, "key": [[2, 3], [4, 5]], "text": "HELLO", "mode": "Encrypt"},
    "Valid 3x3 — [[6,24,1],[13,16,10],[20,17,15]]": {"size": 3, "key": DEFAULT_3X3, "text": "ACTING", "mode": "Encrypt"},
    "KPA Attack Example": {"size": 2, "key": [[3, 3], [2, 5]], "text": "CIPHERSX", "mode": "Encrypt"},
}

preset_choice = st.sidebar.selectbox("📦 Load Preset Example", list(PRESETS.keys()))
if preset_choice != "(Select a preset)" and PRESETS[preset_choice]:
    preset = PRESETS[preset_choice]
    st.session_state["matrix_size"] = preset["size"]
    for ri in range(preset["size"]):
        for ci in range(preset["size"]):
            st.session_state[f"k_{ri}_{ci}"] = preset["key"][ri][ci]
    st.session_state["preset_text"] = preset.get("text", "")
    st.session_state["enc_text_input"] = preset.get("text", "")
    st.session_state["enc_mode"] = preset.get("mode", "Encrypt")
    st.rerun()

st.sidebar.markdown("---")

selected_n = st.sidebar.selectbox(
    "Matrix Size (n × n)",
    [2, 3],
    index=0 if st.session_state["matrix_size"] == 2 else 1,
    help="Select whether to use a 2x2 or 3x3 key matrix.",
)

if selected_n != st.session_state["matrix_size"]:
    st.session_state["matrix_size"] = selected_n
    st.rerun()

n = st.session_state["matrix_size"]

st.sidebar.markdown(f"**Enter {n}×{n} Matrix Elements (mod 26):**")
key_grid = []
for i in range(n):
    cols = st.sidebar.columns(n)
    row = []
    for j in range(n):
        k_name = f"k_{i}_{j}"
        val = cols[j].number_input(
            f"K[{i}][{j}]",
            value=int(st.session_state[k_name]),
            step=1,
            key=k_name,
            label_visibility="collapsed",
        )
        row.append(int(val))
    key_grid.append(row)

key_matrix = np.array(key_grid, dtype=int)

# Random Valid Key Generator
if st.sidebar.button("🎲 Generate Random Valid Key", use_container_width=True):
    random_key = generate_valid_key(n)
    for i in range(n):
        for j in range(n):
            st.session_state[f"k_{i}_{j}"] = int(random_key[i, j])
    st.toast("Generated new random invertible key!", icon="🎲")
    st.rerun()

# Live Key Validity Analysis
is_valid, det_val, det_mod, gcd_val, validity_msg = is_valid_key(key_matrix)

st.sidebar.markdown("---")
st.sidebar.subheader("Key Matrix Analysis")

col_m1, col_m2, col_m3 = st.sidebar.columns(3)
col_m1.metric("det(K)", det_val)
col_m2.metric("det mod 26", det_mod)
col_m3.metric("gcd(det, 26)", gcd_val)

if is_valid:
    st.sidebar.success("Status: **VALID KEY**", icon="✅")
    st.sidebar.caption(validity_msg)
    inv_key = matrix_mod_inverse(key_matrix, 26)
    st.sidebar.markdown("**Matrix Representations:**")
    m_col1, m_col2 = st.sidebar.columns(2)
    with m_col1:
        st.caption("Key Matrix $K$:")
        st.latex(r"K = " + matrix_to_latex(key_matrix))
    with m_col2:
        st.caption("Inverse Matrix $K^{-1}$:")
        st.latex(r"K^{-1} = " + matrix_to_latex(inv_key))
else:
    st.sidebar.error("Status: **INVALID KEY**", icon="❌")
    st.sidebar.caption(validity_msg)
    st.sidebar.info("💡 A valid key requires $\\gcd(\\det(K) \\pmod{26}, 26) = 1$ so that $K^{-1}$ exists.")

# Update query params for shareable state
import json as _json
st.query_params["key"] = _json.dumps(key_matrix.tolist())


# ===========================================================================
# Main Header
# ===========================================================================
st.title("🛡️ Interactive Hill Cipher Cryptosystem")
st.markdown(
    "Explore classical polygraphic substitution using linear algebra modulo 26, "
    "step-by-step vector arithmetic, known-plaintext cryptanalysis, and frequency diffusion."
)

# ===========================================================================
# Navigation Tabs
# ===========================================================================
(
    tab_enc, tab_step, tab_anim, tab_attack, tab_caesar,
    tab_chat, tab_keyspace, tab_quiz, tab_image,
    tab_history, tab_about,
) = st.tabs([
    "🔐 Encrypt / Decrypt",
    "🔍 Step-by-Step",
    "🎬 Animated Walkthrough",
    "⚡ Attack Demo",
    "📊 Caesar vs Hill",
    "💬 Secure Chat Simulator",
    "🔑 Key Space",
    "📝 Practice Quiz",
    "🖼️ Image Encryption",
    "📜 History",
    "ℹ️ About",
])


# ==========================================
# TAB: ENCRYPT / DECRYPT  (with Live Mode)
# ==========================================
with tab_enc:
    st.subheader("Text Transformation")

    mode_options = ["Encrypt", "Decrypt"]
    saved_mode = st.session_state.get("enc_mode", "Encrypt")
    mode_idx = mode_options.index(saved_mode) if saved_mode in mode_options else 0

    col_ctrl1, col_ctrl2 = st.columns([1, 2])
    with col_ctrl1:
        mode = st.radio(
            "Choose Operation:",
            mode_options,
            index=mode_idx,
            horizontal=True,
            key="enc_mode_radio",
            help="Encrypt multiplies plaintext blocks by K. Decrypt multiplies ciphertext blocks by K⁻¹.",
        )
        st.session_state["enc_mode"] = mode

    # Live mode toggle (Feature 2)
    live_mode = st.toggle("⚡ Live Mode", value=False, help="When on, the output updates as you type — no Run button needed.")

    with col_ctrl2:
        default_sample = st.session_state.get("preset_text", "CIPHERS" if mode == "Encrypt" else "ESONLPTV")
        user_text = st.text_input(
            "Enter Text:",
            value=default_sample,
            placeholder="e.g. CIPHERS",
            help="Non-alphabetic characters (spaces, punctuation, digits) are automatically stripped.",
            key="enc_text_input",
        )

    # Sync query parameters for shareable state (key, text, mode)
    try:
        st.query_params["text"] = user_text
        st.query_params["mode"] = mode
    except Exception:
        pass

    cleaned_preview = clean_text(user_text)
    if cleaned_preview:
        clean_len = len(cleaned_preview)
        rem = clean_len % n
        pad_info = ""
        if mode == "Encrypt":
            if rem != 0:
                pad_info = f" • Will add {n - rem} 'X' padding letter(s) to match block size {n}."
            st.caption(f"Cleaned: `{cleaned_preview}` ({clean_len} letters){pad_info}")
        else:
            if rem != 0:
                st.caption(f"Cleaned: `{cleaned_preview}` ({clean_len} letters) • ⚠️ Length is not a multiple of {n}!")
            else:
                st.caption(f"Cleaned: `{cleaned_preview}` ({clean_len} letters) • Valid block size.")

    # --- Live mode output ---
    if live_mode:
        if not is_valid:
            st.warning("⚠️ Key matrix is invalid. Fix it in the sidebar to see live results.")
        elif cleaned_preview:
            try:
                if mode == "Encrypt":
                    live_result = encrypt(user_text, key_matrix)
                    st.success(f"**Live Encrypted Ciphertext:** `{live_result}`")
                else:
                    live_result = decrypt(user_text, key_matrix)
                    st.success(f"**Live Decrypted Plaintext:** `{live_result}`")
            except Exception as e:
                st.error(f"Live mode error: {e}")
        else:
            st.info("Type some text above to see live results.")

    # --- Button mode ---
    run_disabled = not is_valid
    if not live_mode:
        if run_disabled:
            st.warning("⚠️ The Run button is disabled because the key matrix in the sidebar is invalid.")

        if st.button("🚀 Run Operation", type="primary", disabled=run_disabled):
            if not user_text.strip():
                st.warning("Please enter some text before running the operation.")
            else:
                try:
                    if mode == "Encrypt":
                        result = encrypt(user_text, key_matrix)
                        st.success(f"**Encrypted Ciphertext:** `{result}`")
                        st.toast("Encryption completed successfully!", icon="🔐")
                    else:
                        result = decrypt(user_text, key_matrix)
                        st.success(f"**Decrypted Plaintext:** `{result}`")
                        st.toast("Decryption completed successfully!", icon="🔓")

                    st.session_state["last_op"] = {
                        "mode": mode,
                        "input": user_text,
                        "cleaned_input": cleaned_preview,
                        "key": key_matrix.copy(),
                        "output": result,
                        "block_size": n,
                    }
                    st.session_state["history"].append({
                        "Timestamp": datetime.now().strftime("%H:%M:%S"),
                        "Operation": mode,
                        "Block Size": f"{n}x{n}",
                        "Input": user_text,
                        "Key Matrix": key_matrix.tolist(),
                        "Result": result,
                    })
                except Exception as e:
                    st.error(f"Execution Error: {e}")

    # Result Actions Section
    last_op = st.session_state.get("last_op")
    if last_op and last_op.get("output"):
        st.markdown("---")
        st.markdown("### Result Actions")
        act_col1, act_col2 = st.columns(2)
        with act_col1:
            st.download_button(
                label="📥 Download Result as .txt",
                data=f"Hill Cipher Result\nOperation: {last_op['mode']}\nKey Matrix:\n{last_op['key']}\nInput: {last_op['input']}\nOutput: {last_op['output']}\n",
                file_name=f"hill_cipher_{last_op['mode'].lower()}_result.txt",
                mime="text/plain",
                use_container_width=True,
            )
        with act_col2:
            if st.button("🔄 Verify Round Trip", use_container_width=True):
                try:
                    if last_op["mode"] == "Encrypt":
                        round_trip = decrypt(last_op["output"], last_op["key"])
                        st.info(f"Decrypted Result: `{round_trip}`")
                        cleaned_in = last_op["cleaned_input"]
                        if round_trip.startswith(cleaned_in):
                            padding = round_trip[len(cleaned_in):]
                            st.success(f"✅ Round-trip verified! Padding: `{padding or '(none)'}`.")
                        else:
                            st.warning("Round trip mismatch occurred.")
                    else:
                        round_trip = encrypt(last_op["output"], last_op["key"])
                        st.info(f"Re-encrypted Result: `{round_trip}`")
                        if round_trip == last_op["cleaned_input"]:
                            st.success("✅ Round-trip verified!")
                        else:
                            st.warning("Round trip mismatch occurred.")
                except Exception as ex:
                    st.error(f"Round trip verification failed: {ex}")


# ==========================================
# TAB: STEP-BY-STEP VISUALIZATION
# ==========================================
with tab_step:
    st.subheader("Block-by-Block Linear Algebra Breakdown")
    st.markdown(
        "Inspect how each character block is converted to numerical coordinates, "
        "multiplied by the matrix, reduced modulo 26, and converted back to letters."
    )
    if not is_valid:
        st.error("Please configure a valid key matrix in the sidebar to view step breakdowns.")
    else:
        vis_col1, vis_col2 = st.columns([1, 2])
        with vis_col1:
            vis_mode = st.radio("Step Mode:", ["Encrypt", "Decrypt"], horizontal=True, key="vis_mode")
        with vis_col2:
            default_vis = "CIPHERS" if vis_mode == "Encrypt" else "ESONLPTV"
            vis_text = st.text_input("Text to Break Down:", value=default_vis, key="vis_text")
        try:
            steps = get_step_breakdown(vis_text, key_matrix, mode=vis_mode)
            if not steps:
                st.info("Please enter alphabetic text to see the step breakdown.")
            else:
                active_mat = key_matrix if vis_mode == "Encrypt" else matrix_mod_inverse(key_matrix, 26)
                st.markdown(f"**Active Transformation Matrix ({'K' if vis_mode == 'Encrypt' else 'K⁻¹'}):**")
                st.latex(r"M = " + matrix_to_latex(active_mat))
                summary_data = []
                for s in steps:
                    summary_data.append({
                        "Block #": s["block_index"],
                        "Input Chars": s["input_chars"],
                        "Vector P": str(s["input_nums"]),
                        "Raw Product (M × P)": str(s["raw_product"]),
                        "Modulo 26": str(s["mod_nums"]),
                        "Output Chars": s["output_chars"],
                    })
                st.dataframe(pd.DataFrame(summary_data), use_container_width=True)
                st.markdown("#### Detailed Block Calculations")
                for s in steps:
                    with st.expander(
                        f"Block {s['block_index']}: `{s['input_chars']}` ({s['input_nums']}) ➔ `{s['output_chars']}` ({s['mod_nums']})"
                    ):
                        in_vec = np.array(s["input_nums"]).reshape(-1, 1)
                        raw_vec = np.array(s["raw_product"]).reshape(-1, 1)
                        mod_vec = np.array(s["mod_nums"]).reshape(-1, 1)
                        latex_eq = (
                            matrix_to_latex(active_mat) + r" \cdot " + matrix_to_latex(in_vec) + r" = "
                            + matrix_to_latex(raw_vec) + r" \equiv " + matrix_to_latex(mod_vec) + r" \pmod{26}"
                        )
                        st.latex(latex_eq)
                        st.write(f"**Result for Block {s['block_index']}:** Characters `{s['output_chars']}`")
        except Exception as e:
            st.error(f"Cannot generate breakdown: {e}")


# ==========================================
# TAB: ANIMATED WALKTHROUGH (Feature 1)
# ==========================================
with tab_anim:
    st.subheader("🎬 Animated Block-by-Block Walkthrough")
    st.markdown("Step through each block of the encryption or decryption process one at a time, with highlighted matrix multiplication.")

    if not is_valid:
        st.error("Please configure a valid key matrix in the sidebar first.")
    else:
        anim_col1, anim_col2 = st.columns([1, 2])
        with anim_col1:
            anim_mode = st.radio("Mode:", ["Encrypt", "Decrypt"], horizontal=True, key="anim_mode_radio")
        with anim_col2:
            anim_text = st.text_input("Text:", value="CIPHERS" if anim_mode == "Encrypt" else "ESONLPTV", key="anim_text_input")

        try:
            anim_steps = get_step_breakdown(anim_text, key_matrix, mode=anim_mode)
        except Exception as e:
            anim_steps = []
            st.error(f"Error: {e}")

        if anim_steps:
            num_blocks = len(anim_steps)
            active_mat = key_matrix if anim_mode == "Encrypt" else matrix_mod_inverse(key_matrix, 26)
            mat_label = "K" if anim_mode == "Encrypt" else "K⁻¹"

            # Navigation controls
            nav_col1, nav_col2, nav_col3, nav_col4 = st.columns([1, 1, 1, 1])
            with nav_col1:
                if st.button("⬅️ Previous", use_container_width=True, disabled=st.session_state["anim_block"] <= 0):
                    st.session_state["anim_block"] = max(0, st.session_state["anim_block"] - 1)
                    st.rerun()
            with nav_col2:
                if st.button("➡️ Next", use_container_width=True, disabled=st.session_state["anim_block"] >= num_blocks - 1):
                    st.session_state["anim_block"] = min(num_blocks - 1, st.session_state["anim_block"] + 1)
                    st.rerun()
            with nav_col3:
                auto_play = st.button("▶️ Auto-play", use_container_width=True)
            with nav_col4:
                stop_btn = st.button("⏹️ Stop", use_container_width=True)

            if stop_btn:
                auto_play = False
                st.session_state["anim_playing"] = False
                st.toast("Auto-play stopped.", icon="⏹️")

            # Clamp block index
            if st.session_state["anim_block"] >= num_blocks:
                st.session_state["anim_block"] = 0

            # Slider
            block_idx = st.slider("Block", 0, num_blocks - 1, st.session_state["anim_block"], key="anim_slider")
            st.session_state["anim_block"] = block_idx

            # Auto-play logic
            if auto_play:
                placeholder = st.empty()
                for bi in range(num_blocks):
                    st.session_state["anim_block"] = bi
                    step = anim_steps[bi]
                    with placeholder.container():
                        st.info(f"▶️ Auto-playing block {bi + 1} / {num_blocks} (1s per block)...")
                        _render_animated_block(step, active_mat, mat_label, n)
                    time.sleep(1.0)
                placeholder.success("✅ Auto-play complete!")

            # Render current block
            if not auto_play:
                step = anim_steps[block_idx]
                _render_animated_block_static = True  # flag for rendering below

        else:
            st.info("Enter some text above to see the animated walkthrough.")
            _render_animated_block_static = False


# Helper function rendered inline to avoid forward-reference issues
def _render_animated_block(step: dict, active_mat: np.ndarray, mat_label: str, block_size: int):
    """Render one animated block with highlighted matrix multiplication."""
    input_vec = np.array(step["input_nums"])
    raw_prod = np.array(step["raw_product"])
    mod_result = np.array(step["mod_nums"])

    st.markdown(f"### Block {step['block_index']}: `{step['input_chars']}` → `{step['output_chars']}`")

    # Step 1: Letters to Numbers
    letter_nums = " → ".join(f"**{c}**={v}" for c, v in zip(step["input_chars"], step["input_nums"]))
    st.markdown(f"**Step 1 — Letters to Numbers:** {letter_nums}")

    # Step 2: Matrix multiplication with highlighted cells
    st.markdown(f"**Step 2 — Matrix × Vector ({mat_label} × P):**")

    # Build HTML table showing multiplication
    rows_html = []
    for i in range(block_size):
        cells = []
        for j in range(block_size):
            product = int(active_mat[i, j]) * int(input_vec[j])
            cells.append(
                f'<td style="background:#e8f4e8;border:1px solid #999;padding:6px;text-align:center;">'
                f'{int(active_mat[i, j])}×{int(input_vec[j])}={product}</td>'
            )
        row_sum = int(raw_prod[i])
        cells.append(f'<td style="background:#d4edda;border:1px solid #999;padding:6px;text-align:center;font-weight:bold;">= {row_sum}</td>')
        rows_html.append("<tr>" + "".join(cells) + "</tr>")

    header_cells = "".join(
        f'<th style="background:#f0f0f0;border:1px solid #999;padding:6px;text-align:center;">P[{j}]={int(input_vec[j])}</th>'
        for j in range(block_size)
    )
    header_cells += '<th style="background:#f0f0f0;border:1px solid #999;padding:6px;">Sum</th>'

    html_table = f'<table style="border-collapse:collapse;margin:10px 0;"><tr>{header_cells}</tr>{"".join(rows_html)}</table>'
    st.markdown(html_table, unsafe_allow_html=True)

    # Step 3: Mod 26
    mod_str = ", ".join(f"{int(raw_prod[i])} mod 26 = **{int(mod_result[i])}**" for i in range(block_size))
    st.markdown(f"**Step 3 — Modulo 26:** {mod_str}")

    # Step 4: Numbers to Letters
    num_letters = " → ".join(f"{int(mod_result[i])}=**{step['output_chars'][i]}**" for i in range(block_size))
    st.markdown(f"**Step 4 — Numbers to Letters:** {num_letters}")


# Render current block for non-autoplay
with tab_anim:
    if is_valid and anim_steps and not auto_play:
        step = anim_steps[st.session_state["anim_block"]]
        active_mat_for_render = key_matrix if anim_mode == "Encrypt" else matrix_mod_inverse(key_matrix, 26)
        _render_animated_block(step, active_mat_for_render, "K" if anim_mode == "Encrypt" else "K⁻¹", n)


# ==========================================
# TAB: ATTACK DEMO (KNOWN-PLAINTEXT)
# ==========================================
with tab_attack:
    st.subheader("⚡ Known-Plaintext Attack (KPA) Demonstration")
    st.markdown(
        """
        The Hill Cipher is **strictly linear**, making it completely vulnerable to a **Known-Plaintext Attack**.
        If an attacker discovers or guesses just $n$ blocks of plaintext and their corresponding ciphertext blocks:

        $$C = K \\cdot P \\pmod{26} \\implies K = C \\cdot P^{-1} \\pmod{26}$$

        No brute-force search is needed — the key matrix $K$ is directly recovered using modular matrix inversion!
        """
    )
    attack_n = st.selectbox("Attack Matrix Size (n):", [2, 3], index=0, key="attack_n_select")

    col_btn1, col_btn2, col_btn3 = st.columns(3)
    with col_btn1:
        if st.button("Load 2x2 Test Pair (CIPHERS)", use_container_width=True):
            st.session_state["attack_p"] = "CIPHERSX"
            st.session_state["attack_c"] = "ESONLPTV"
            st.session_state["attack_n_select"] = 2
            st.rerun()
    with col_btn2:
        if st.button("Load 3x3 Test Pair (ACTING)", use_container_width=True):
            st.session_state["attack_p"] = "ACTING"
            k3 = np.array(DEFAULT_3X3)
            st.session_state["attack_c"] = encrypt("ACTING", k3)
            st.session_state["attack_n_select"] = 3
            st.rerun()
    with col_btn3:
        if st.button("Generate Pair from Sidebar Key", use_container_width=True):
            if is_valid:
                sample_p = "HILLCIPHERWEAKNESS" if n == 2 else "SECURITYFLAWSFOUND"
                st.session_state["attack_p"] = sample_p
                st.session_state["attack_c"] = encrypt(sample_p, key_matrix)
                st.session_state["attack_n_select"] = n
                st.rerun()
            else:
                st.warning("Configure a valid key in the sidebar first.")

    col_atk1, col_atk2 = st.columns(2)
    with col_atk1:
        attack_p = st.text_input("Known Plaintext:", value=st.session_state.get("attack_p", "CIPHERSX"), key="input_attack_p")
    with col_atk2:
        attack_c = st.text_input("Matching Ciphertext:", value=st.session_state.get("attack_c", "ESONLPTV"), key="input_attack_c")

    if st.button("🔓 Recover Key Matrix", type="primary"):
        recovery = recover_key_from_pair(attack_p, attack_c, n=attack_n)
        if recovery["success"]:
            st.success("🎉 Key Matrix Successfully Recovered!", icon="🔑")
            rec_k = recovery["key_matrix"]
            rec_col1, rec_col2 = st.columns(2)
            with rec_col1:
                st.markdown("**Recovered Key Matrix $K$:**")
                st.latex(r"K_{recovered} = " + matrix_to_latex(rec_k))
                if np.array_equal(rec_k % 26, key_matrix % 26) and attack_n == n:
                    st.success("✅ Recovered key matches your sidebar key!")
            with rec_col2:
                st.markdown("**Selected Plaintext Matrix $P$ & Inverse $P^{-1}$:**")
                st.latex(
                    r"P = " + matrix_to_latex(recovery["p_matrix"])
                    + r",\quad P^{-1} \equiv " + matrix_to_latex(recovery["p_inv_matrix"]) + r" \pmod{26}"
                )
                st.caption(f"Used Blocks {recovery['selected_blocks']}. $\\det(P) = {recovery['p_det']} \\equiv {recovery['p_det_mod26']} \\pmod{{26}}$.")

            st.markdown("#### Mathematical Derivation")
            st.latex(
                r"K \equiv C \cdot P^{-1} = " + matrix_to_latex(recovery["c_matrix"])
                + r" \cdot " + matrix_to_latex(recovery["p_inv_matrix"])
                + r" \equiv " + matrix_to_latex(rec_k) + r" \pmod{26}"
            )
            if st.button("📥 Apply Recovered Key to Sidebar"):
                st.session_state["matrix_size"] = attack_n
                for i in range(attack_n):
                    for j in range(attack_n):
                        st.session_state[f"k_{i}_{j}"] = int(rec_k[i, j])
                st.toast("Recovered key loaded into sidebar!", icon="✅")
                st.rerun()
        else:
            st.error(f"Recovery Failed: {recovery['error']}")


# ==========================================
# TAB: CAESAR VS HILL COMPARISON
# ==========================================
with tab_caesar:
    st.subheader("📊 Caesar Cipher vs. Hill Cipher Frequency Analysis")
    st.markdown("""
    **Monoalphabetic vs. Polygraphic Substitution:**
    - **Caesar Cipher** substitutes one letter at a time with a fixed shift — frequency distribution is merely shifted.
    - **Hill Cipher** encrypts blocks simultaneously, diffusing individual letter frequencies into a flatter distribution.
    """)
    default_analysis_text = (
        "THE HILL CIPHER IS A POLYGRAPHIC SUBSTITUTION CIPHER BASED ON LINEAR ALGEBRA "
        "INVENTED BY LESTER S HILL IN NINETEEN TWENTY NINE. EACH LETTER IS REPRESENTED BY A NUMBER "
        "MODULO TWENTY SIX. TO ENCRYPT A MESSAGE EACH BLOCK OF N LETTERS IS MULTIPLIED BY AN "
        "INVERTIBLE N BY N MATRIX OVER THE INTEGERS MODULO TWENTY SIX."
    )
    cmp_text = st.text_area("Input Sample Text for Analysis:", value=default_analysis_text, height=110)
    shift_val = st.slider("Caesar Cipher Shift:", min_value=1, max_value=25, value=3)

    if not is_valid:
        st.warning("⚠️ The Hill Cipher comparison uses your active sidebar key. Please set a valid key in the sidebar.")
    else:
        clean_input = clean_text(cmp_text)
        caesar_res = caesar_encrypt(clean_input, shift=shift_val)
        hill_res = encrypt(clean_input, key_matrix)
        freq_orig = letter_frequencies(clean_input)
        freq_caesar = letter_frequencies(caesar_res)
        freq_hill = letter_frequencies(hill_res)

        df_freq = pd.DataFrame({
            "Letter": [chr(ord("A") + i) for i in range(26)],
            "Original Text": [freq_orig[chr(ord("A") + i)] for i in range(26)],
            "Caesar Cipher": [freq_caesar[chr(ord("A") + i)] for i in range(26)],
            "Hill Cipher": [freq_hill[chr(ord("A") + i)] for i in range(26)],
        }).set_index("Letter")

        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            st.markdown(f"**Original vs. Caesar Cipher (Shift = {shift_val})**")
            st.bar_chart(df_freq[["Original Text", "Caesar Cipher"]])
        with chart_col2:
            st.markdown(f"**Original vs. Hill Cipher ({n}×{n} Matrix)**")
            st.bar_chart(df_freq[["Original Text", "Hill Cipher"]])

        st.markdown("#### Variance & Frequency Flattening Metric")
        orig_std = float(np.std(list(freq_orig.values())))
        caesar_std = float(np.std(list(freq_caesar.values())))
        hill_std = float(np.std(list(freq_hill.values())))
        stat_col1, stat_col2, stat_col3 = st.columns(3)
        stat_col1.metric("Original Freq Std Dev", f"{orig_std:.2f}")
        stat_col2.metric("Caesar Freq Std Dev", f"{caesar_std:.2f}", delta="0 (No Flattening)")
        stat_col3.metric("Hill Cipher Std Dev", f"{hill_std:.2f}", delta=f"{hill_std - orig_std:.2f} (Smoothed)", delta_color="inverse")


# ==========================================
# TAB: SECURE CHAT SIMULATOR (Feature 3)
# ==========================================
with tab_chat:
    st.subheader("💬 Alice, Bob & Eve — Secure Chat Simulator")
    st.markdown(
        "Alice sends encrypted messages to Bob. Eve intercepts the ciphertext but cannot read it — "
        "unless she mounts a **known-plaintext attack**."
    )

    # Chat key setup
    chat_key_col1, chat_key_col2 = st.columns([2, 1])
    with chat_key_col1:
        chat_size = st.selectbox("Key Size for Chat:", [2, 3], index=0, key="chat_size_select")
        if st.session_state["chat_key"] is not None:
            ck = st.session_state["chat_key"]
            st.markdown(f"**Shared Key ({ck.shape[0]}×{ck.shape[0]}):**")
            st.latex(r"K_{chat} = " + matrix_to_latex(ck))
        else:
            st.info("No chat key set yet. Generate one below.")
    with chat_key_col2:
        if st.button("🔑 Generate Chat Key", use_container_width=True):
            st.session_state["chat_key"] = generate_valid_key(chat_size)
            st.session_state["chat_n"] = chat_size
            st.toast("New chat key generated!", icon="🔑")
            st.rerun()
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state["chat_log"] = []
            st.toast("Chat cleared!", icon="🗑️")
            st.rerun()

    # Alice sends a message
    if st.session_state["chat_key"] is not None:
        chat_key = st.session_state["chat_key"]
        chat_n_val = st.session_state["chat_n"]

        alice_msg = st.text_input("✉️ Alice — Type a message to send to Bob:", key="alice_msg_input")
        if st.button("📤 Send Message", type="primary"):
            if alice_msg.strip():
                cleaned_msg = clean_text(alice_msg)
                if cleaned_msg:
                    cipher_msg = encrypt(cleaned_msg, chat_key)
                    decrypted_msg = decrypt(cipher_msg, chat_key)
                    st.session_state["chat_log"].append({
                        "plaintext": cleaned_msg,
                        "ciphertext": cipher_msg,
                        "decrypted": decrypted_msg,
                        "time": datetime.now().strftime("%H:%M:%S"),
                    })
                    st.toast("Message sent!", icon="📤")
                    st.rerun()

        # Display chat in 3 columns
        if st.session_state["chat_log"]:
            st.markdown("---")
            alice_col, bob_col, eve_col = st.columns(3)
            with alice_col:
                st.markdown("### 👩 Alice (Sender)")
                for msg in st.session_state["chat_log"]:
                    st.markdown(f'<div style="background:#d4edda;padding:8px;border-radius:8px;margin:4px 0;">📤 <b>{msg["plaintext"]}</b> <small>({msg["time"]})</small></div>', unsafe_allow_html=True)

            with bob_col:
                st.markdown("### 👨 Bob (Receiver)")
                for msg in st.session_state["chat_log"]:
                    st.markdown(f'<div style="background:#cce5ff;padding:8px;border-radius:8px;margin:4px 0;">🔓 <b>{msg["decrypted"]}</b> <small>({msg["time"]})</small></div>', unsafe_allow_html=True)

            with eve_col:
                st.markdown("### 🕵️ Eve (Eavesdropper)")
                for msg in st.session_state["chat_log"]:
                    st.markdown(f'<div style="background:#f8d7da;padding:8px;border-radius:8px;margin:4px 0;">🔒 <code>{msg["ciphertext"]}</code> <small>({msg["time"]})</small></div>', unsafe_allow_html=True)

            # Eve's attack section
            st.markdown("---")
            st.markdown("### 🕵️ Eve's Known-Plaintext Attack")
            st.markdown("Eve intercepted the ciphertext above. If she can guess the plaintext for one message, she can recover the key and decrypt everything.")

            if len(st.session_state["chat_log"]) >= 1:
                eve_target_idx = st.selectbox(
                    "Select an intercepted message to attack:",
                    range(len(st.session_state["chat_log"])),
                    format_func=lambda i: f"Message {i+1}: {st.session_state['chat_log'][i]['ciphertext'][:20]}...",
                    key="eve_target",
                )
                eve_guess = st.text_input("Eve's guessed plaintext for this message:", key="eve_guess_input")

                if st.button("🔓 Attempt Attack", type="primary"):
                    target = st.session_state["chat_log"][eve_target_idx]
                    recovery = recover_key_from_pair(eve_guess, target["ciphertext"], n=chat_n_val)
                    if recovery["success"]:
                        rec_key = recovery["key_matrix"]
                        st.success("🎉 Eve recovered the key!")
                        st.latex(r"K_{recovered} = " + matrix_to_latex(rec_key))

                        if np.array_equal(rec_key % 26, chat_key % 26):
                            st.success("✅ The recovered key matches the actual chat key!")

                        st.markdown("**Eve can now decrypt all intercepted messages:**")
                        for i, msg in enumerate(st.session_state["chat_log"]):
                            try:
                                eve_dec = decrypt(msg["ciphertext"], rec_key)
                                st.write(f"Message {i+1}: `{msg['ciphertext']}` → **{eve_dec}**")
                            except Exception:
                                st.write(f"Message {i+1}: `{msg['ciphertext']}` → *(decryption failed)*")

                        st.warning(
                            "⚠️ **This is why the Hill Cipher is weak!** "
                            "Just one known plaintext-ciphertext pair was enough to recover the entire key. "
                            "The linearity of the cipher (C = K·P mod 26) means the key can be computed directly "
                            "via K = C·P⁻¹ mod 26 without any brute force."
                        )
                    else:
                        st.error(f"Attack failed: {recovery['error']}")
                        st.info("Try a different guess or ensure it has enough letters for the block size.")


# ==========================================
# TAB: KEY SPACE EXPLORER (Feature 4)
# ==========================================
with tab_keyspace:
    st.subheader("🔑 Key Space Explorer (2×2 Matrices)")
    st.markdown(
        "Explore all $26^4 = 456{,}976$ possible 2×2 key matrices and see which ones are valid. "
        "A key $\\begin{bmatrix} a & b \\\\ c & d \\end{bmatrix}$ is valid when "
        "$\\gcd(ad - bc \\pmod{26}, 26) = 1$, i.e. the determinant is odd and not divisible by 13."
    )

    # Cached brute-force count
    @st.cache_data(show_spinner="Counting all 456,976 possible 2×2 keys...")
    def _cached_key_count():
        return count_valid_2x2_keys(26)

    valid_count = _cached_key_count()
    total = 26 ** 4
    invalid_count = total - valid_count
    pct = valid_count / total * 100

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total 2×2 Keys", f"{total:,}")
    m2.metric("Valid Keys", f"{valid_count:,}")
    m3.metric("Invalid Keys", f"{invalid_count:,}")
    m4.metric("Valid %", f"{pct:.1f}%")

    st.markdown("---")

    # Interactive heatmap
    st.markdown("### Interactive Validity Heatmap")
    st.markdown(
        "Fix values of **b** and **c**, then see which **(a, d)** pairs yield a valid key. "
        "Green = valid, red = invalid."
    )
    hm_col1, hm_col2 = st.columns(2)
    with hm_col1:
        hm_b = st.slider("b value:", 0, 25, 3, key="hm_b")
    with hm_col2:
        hm_c = st.slider("c value:", 0, 25, 2, key="hm_c")

    grid = key_validity_grid(hm_b, hm_c)
    valid_in_grid = int(grid.sum())

    # Create plotly heatmap
    z_data = grid.astype(int)
    fig = go.Figure(data=go.Heatmap(
        z=z_data,
        x=list(range(26)),
        y=list(range(26)),
        colorscale=[[0, "rgb(255,100,100)"], [1, "rgb(100,200,100)"]],
        showscale=False,
        hovertemplate="a=%{y}, d=%{x}<br>det=(a·d - b·c) mod 26<br>Valid: %{z}<extra></extra>",
    ))
    fig.update_layout(
        title=f"Key Validity for b={hm_b}, c={hm_c} ({valid_in_grid}/676 valid)",
        xaxis_title="d",
        yaxis_title="a",
        width=600,
        height=550,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Modular inverse table
    st.markdown("### Modular Inverse Table (mod 26)")
    st.markdown("Numbers that have no inverse (even or divisible by 13) make the determinant invalid.")
    inv_table = mod_inverse_table(26)
    inv_df = pd.DataFrame(inv_table)
    inv_df["inverse"] = inv_df["inverse"].apply(lambda x: str(x) if x is not None else "—")
    inv_df["status"] = inv_df["has_inverse"].apply(lambda x: "✅ Has inverse" if x else "❌ No inverse")
    st.dataframe(inv_df[["number", "inverse", "status"]].rename(columns={"number": "x", "inverse": "x⁻¹ mod 26"}), use_container_width=True)


# ==========================================
# TAB: PRACTICE QUIZ (Round 2, Feature 5)
# ==========================================
with tab_quiz:
    st.subheader("📝 Practice Quiz — Test Your Hill Cipher Skills")

    quiz_col1, quiz_col2 = st.columns([2, 1])
    with quiz_col2:
        st.metric("Score", f"{st.session_state['quiz_score']} / {st.session_state['quiz_total']}")
        st.metric("Current Streak", f"🔥 {st.session_state['quiz_streak']}")

    with quiz_col1:
        q_diff = st.selectbox("Difficulty:", ["2×2 (beginner)", "3×3 (advanced)"], key="quiz_diff")
        q_mode = st.selectbox("Question Type:", ["Encrypt", "Decrypt"], key="quiz_mode_select")
        q_n = 2 if "2×2" in q_diff else 3

    if st.button("🎲 Generate New Question", type="primary"):
        st.session_state["quiz_question"] = generate_quiz_question(q_n, mode=q_mode.lower())
        st.session_state["quiz_answered"] = False
        st.rerun()

    qq = st.session_state.get("quiz_question")
    if qq:
        st.markdown("---")
        st.markdown(f"**Mode:** {'Encrypt ✏️' if qq['mode'] == 'encrypt' else 'Decrypt 🔓'}")
        st.latex(r"K = " + matrix_to_latex(qq["key_matrix"]))
        st.markdown(f"**{'Plaintext' if qq['mode'] == 'encrypt' else 'Ciphertext'}:** `{qq['input_text']}`")

        if qq["mode"] == "encrypt":
            st.markdown("**What is the ciphertext?**")
        else:
            st.markdown("**What is the plaintext?**")

        user_ans = st.text_input("Your answer:", key="quiz_user_answer")

        if st.button("✅ Submit Answer") and not st.session_state["quiz_answered"]:
            st.session_state["quiz_answered"] = True
            st.session_state["quiz_total"] += 1
            correct = check_quiz_answer(user_ans, qq["expected_answer"])
            if correct:
                st.session_state["quiz_score"] += 1
                st.session_state["quiz_streak"] += 1
                st.success(f"🎉 Correct! The answer is `{qq['expected_answer']}`.")
                st.balloons()
            else:
                st.session_state["quiz_streak"] = 0
                st.error(f"❌ Incorrect. The correct answer is `{qq['expected_answer']}`.")
                st.markdown("**Here is the step-by-step working:**")
                for s in qq["steps"]:
                    st.markdown(f"- Block {s['block_index']}: `{s['input_chars']}` ({s['input_nums']}) → {s['formula']} → `{s['output_chars']}`")
            st.rerun()

        if st.session_state["quiz_answered"]:
            correct = check_quiz_answer(st.session_state.get("quiz_user_answer", ""), qq["expected_answer"])
            if correct:
                st.success(f"🎉 Correct! The answer is `{qq['expected_answer']}`.")
            else:
                st.error(f"❌ Incorrect. The correct answer is `{qq['expected_answer']}`.")
                st.markdown("**Step-by-step working:**")
                for s in qq["steps"]:
                    st.markdown(f"- Block {s['block_index']}: `{s['input_chars']}` ({s['input_nums']}) → {s['formula']} → `{s['output_chars']}`")


# ==========================================
# TAB: IMAGE ENCRYPTION (Round 2, Feature 8)
# ==========================================
with tab_image:
    st.subheader("🖼️ Hill Cipher Image Encryption (mod 256)")
    st.markdown(
        """
        Apply the Hill Cipher to **grayscale pixel values** (0–255) using arithmetic modulo 256.
        A key is valid when its determinant is **odd** (coprime with $256 = 2^8$).

        > **ECB-mode weakness:** Identical pixel blocks produce identical ciphertext blocks,
        > so patterns in the original image can leak through. This is the same weakness as
        > AES-ECB and why block ciphers use chaining modes (CBC, CTR, etc.) in practice.
        """
    )

    img_file = st.file_uploader("Upload a grayscale PNG or JPG image:", type=["png", "jpg", "jpeg"], key="img_upload")

    img_key_col1, img_key_col2 = st.columns(2)
    with img_key_col1:
        img_n = st.selectbox("Image Key Size:", [2, 3], index=0, key="img_key_size")
    with img_key_col2:
        if st.button("🎲 Generate Image Key (mod 256)", use_container_width=True):
            img_key = generate_valid_key_mod256(img_n)
            st.session_state["img_key"] = img_key.tolist()
            st.toast("Generated new image encryption key!", icon="🔑")
            st.rerun()

    if "img_key" not in st.session_state:
        st.session_state["img_key"] = generate_valid_key_mod256(2).tolist()

    img_key_matrix = np.array(st.session_state["img_key"], dtype=int)
    img_valid, img_det, img_msg = is_valid_key_mod256(img_key_matrix)

    st.markdown(f"**Image Key Matrix ({img_key_matrix.shape[0]}×{img_key_matrix.shape[0]}):**")
    st.latex(r"K_{img} = " + matrix_to_latex(img_key_matrix))
    if img_valid:
        st.success(f"✅ {img_msg}")
    else:
        st.error(f"❌ {img_msg}")

    if img_file is not None and img_valid:
        try:
            from PIL import Image
            img = Image.open(img_file).convert("L")  # Convert to grayscale
            img_array = np.array(img)
            original_shape = img_array.shape
            pixels_flat = img_array.flatten()

            # Encrypt
            enc_pixels = encrypt_image_pixels(pixels_flat, img_key_matrix)
            enc_img = enc_pixels[:pixels_flat.shape[0]].reshape(original_shape).astype(np.uint8)

            # Decrypt
            dec_pixels = decrypt_image_pixels(enc_pixels, img_key_matrix)
            dec_img = dec_pixels[:pixels_flat.shape[0]].reshape(original_shape).astype(np.uint8)

            img_col1, img_col2, img_col3 = st.columns(3)
            with img_col1:
                st.markdown("**Original**")
                st.image(img_array, use_container_width=True, caption="Original Grayscale")
            with img_col2:
                st.markdown("**Encrypted**")
                st.image(enc_img, use_container_width=True, caption="Encrypted (mod 256)")
            with img_col3:
                st.markdown("**Decrypted**")
                st.image(dec_img, use_container_width=True, caption="Decrypted (round-trip)")

            if np.array_equal(img_array, dec_img):
                st.success("✅ Perfect round-trip: decrypted image matches original!")
            else:
                st.warning("⚠️ Minor differences detected (possible padding artifact at the edge).")

        except ImportError:
            st.error("Pillow (PIL) is required for image encryption. Run: `uv add Pillow`")
        except Exception as e:
            st.error(f"Image processing error: {e}")
    elif img_file is not None and not img_valid:
        st.warning("Please generate a valid image key first.")


# ==========================================
# TAB: HISTORY
# ==========================================
with tab_history:
    st.subheader("📜 Session Operations Log")
    hist_list = st.session_state.get("history", [])
    st.metric("Total Operations Logged", len(hist_list))
    if not hist_list:
        st.info("No operations have been run in this session yet.")
    else:
        df_hist = pd.DataFrame(hist_list)
        st.dataframe(df_hist, use_container_width=True)
        if st.button("🗑️ Clear History"):
            st.session_state["history"] = []
            st.toast("History log cleared!", icon="🗑️")
            st.rerun()


# ==========================================
# TAB: ABOUT & REFERENCE
# ==========================================
with tab_about:
    st.subheader("ℹ️ Hill Cipher Reference & Mathematical Principles")

    with st.expander("📖 Letter to Number Reference Table (A=0 ... Z=25)", expanded=True):
        ref_letters_1 = [chr(ord("A") + i) for i in range(13)]
        ref_numbers_1 = [str(i) for i in range(13)]
        ref_letters_2 = [chr(ord("A") + i) for i in range(13, 26)]
        ref_numbers_2 = [str(i) for i in range(13, 26)]
        table_md = "| " + " | ".join(ref_letters_1) + " |\n|" + "---|" * 13 + "\n| " + " | ".join(ref_numbers_1) + " |\n\n"
        table_md += "| " + " | ".join(ref_letters_2) + " |\n|" + "---|" * 13 + "\n| " + " | ".join(ref_numbers_2) + " |"
        st.markdown(table_md)

    with st.expander("📐 Mathematical Formulation"):
        st.markdown("""
        ### Encryption
        Plaintext is split into blocks of $n$ letters, represented as column vectors $P$:
        $$C = K \\cdot P \\pmod{26}$$

        ### Decryption
        Ciphertext blocks are multiplied by the modular inverse of the key matrix:
        $$P = K^{-1} \\cdot C \\pmod{26}$$

        ### Modular Matrix Inversion Formula
        Using the adjugate matrix $\\text{adj}(K)$:
        $$K^{-1} = \\det(K)^{-1} \\cdot \\text{adj}(K) \\pmod{26}$$

        ### Key Validity Condition
        For $K^{-1}$ to exist modulo 26, $\\det(K)$ must have a multiplicative inverse in $\\mathbb{Z}_{26}$.
        Since $26 = 2 \\times 13$, this requires:
        $$\\gcd(\\det(K), 26) = 1$$
        """)

    with st.expander("⚠️ Cryptographic Weaknesses"):
        st.markdown("""
        1. **Known-Plaintext Attack (KPA):** Because the cipher is purely linear, knowing $n$ plaintext-ciphertext block pairs solves $K = C \\cdot P^{-1} \\pmod{26}$ with zero brute force.
        2. **Chosen-Plaintext Attack (CPA):** An attacker can choose standard basis vectors to read key columns directly.
        3. **Padding Leaks:** Fixed padding characters reveal block boundaries and the cipher block size.
        4. **ECB-style Weakness:** Identical plaintext blocks always produce identical ciphertext blocks, leaking patterns.
        """)

