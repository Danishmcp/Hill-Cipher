"""Generate an 80-page academic Word report for the Hill Cipher lab."""

from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor, Twips, Emu


OUTPUT = Path(__file__).with_name("Hill_Cipher_Project_Report_80_Pages.docx")
NAVY = RGBColor(0x1F, 0x34, 0x3D)
TEAL = RGBColor(0x00, 0x70, 0x73)
GRAY = RGBColor(0x5A, 0x64, 0x68)
BODY = RGBColor(0x22, 0x22, 0x22)
FONT = "Times New Roman"
HEAD_FONT = "Times New Roman"


def set_run_font(run, name=FONT, size=12, bold=False, italic=False, color=BODY):
    run.font.name = name
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if color is not None:
        run.font.color.rgb = color
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.get_or_add_rFonts()
    rfonts.set(qn("w:ascii"), name)
    rfonts.set(qn("w:hAnsi"), name)
    rfonts.set(qn("w:cs"), name)
    rfonts.set(qn("w:eastAsia"), name)


def shade_cell(cell, fill):
    props = cell._tc.get_or_add_tcPr()
    shading = OxmlElement("w:shd")
    shading.set(qn("w:fill"), fill)
    shading.set(qn("w:val"), "clear")
    props.append(shading)


def set_cell_border(cell, color="7A8A8E", sz="12"):
    tc = cell._tc
    tcpr = tc.get_or_add_tcPr()
    tcborders = OxmlElement("w:tcBorders")
    for edge in ("top", "left", "bottom", "right"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "dashed")
        el.set(qn("w:sz"), sz)
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), color)
        tcborders.append(el)
    tcpr.append(tcborders)


def set_row_height(row, inches):
    tr = row._tr
    trpr = tr.get_or_add_trPr()
    height = OxmlElement("w:trHeight")
    height.set(qn("w:val"), str(int(inches * 1440)))
    height.set(qn("w:hRule"), "atLeast")
    trpr.append(height)


def add_page_number(paragraph):
    run = paragraph.add_run()
    set_run_font(run, size=10, color=GRAY)
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instruction = OxmlElement("w:instrText")
    instruction.set(qn("xml:space"), "preserve")
    instruction.text = " PAGE "
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    text = OxmlElement("w:t")
    text.text = "1"
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    for element in (begin, instruction, separate, text, end):
        run._r.append(element)


def configure_styles(doc):
    normal = doc.styles["Normal"]
    normal.font.name = FONT
    normal.font.size = Pt(12)
    normal.font.color.rgb = BODY
    pf = normal.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    pf.space_after = Pt(10)
    pf.space_before = Pt(0)
    rpr = normal.element.get_or_add_rPr()
    rfonts = rpr.get_or_add_rFonts()
    rfonts.set(qn("w:ascii"), FONT)
    rfonts.set(qn("w:hAnsi"), FONT)

    for name, size, color, space_before, space_after in (
        ("Title", 26, NAVY, 0, 12),
        ("Heading 1", 16, NAVY, 18, 10),
        ("Heading 2", 14, TEAL, 14, 8),
        ("Heading 3", 12, NAVY, 10, 6),
    ):
        style = doc.styles[name]
        style.font.name = HEAD_FONT
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = color
        style.paragraph_format.space_before = Pt(space_before)
        style.paragraph_format.space_after = Pt(space_after)
        style.paragraph_format.line_spacing = 1.15


def p(doc, text, *, size=12, bold=False, italic=False, align="justify", space_after=10, first_line=True):
    para = doc.add_paragraph()
    if align == "justify":
        para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    elif align == "center":
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    elif align == "right":
        para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    else:
        para.alignment = WD_ALIGN_PARAGRAPH.LEFT
    para.paragraph_format.space_after = Pt(space_after)
    para.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    if first_line and align == "justify":
        para.paragraph_format.first_line_indent = Cm(1.0)
    run = para.add_run(text)
    set_run_font(run, size=size, bold=bold, italic=italic)
    return para


def heading(doc, text, level=1):
    h = doc.add_heading(text, level=level)
    for run in h.runs:
        set_run_font(run, name=HEAD_FONT, size={1: 16, 2: 14, 3: 12}[level], bold=True, color=NAVY if level != 2 else TEAL)
    return h


def bullet(doc, text):
    para = doc.add_paragraph(style="List Bullet")
    para.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    para.paragraph_format.space_after = Pt(4)
    para.clear()
    run = para.add_run(text)
    set_run_font(run, size=12)
    return para


def numbered(doc, text):
    para = doc.add_paragraph(style="List Number")
    para.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    para.paragraph_format.space_after = Pt(4)
    para.clear()
    run = para.add_run(text)
    set_run_font(run, size=12)
    return para


def caption(doc, text):
    para = doc.add_paragraph()
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    para.paragraph_format.space_before = Pt(4)
    para.paragraph_format.space_after = Pt(16)
    para.paragraph_format.line_spacing = 1.15
    run = para.add_run(text)
    set_run_font(run, size=11, italic=True, color=GRAY)
    return para


def ss(doc, fig, title, where, height=2.55):
    """Leave a dashed box for the student to paste a screenshot."""
    intro = doc.add_paragraph()
    intro.alignment = WD_ALIGN_PARAGRAPH.CENTER
    intro.paragraph_format.space_before = Pt(8)
    intro.paragraph_format.space_after = Pt(4)
    intro.paragraph_format.line_spacing = 1.0
    run = intro.add_run("SCREENSHOT SPACE  —  paste image inside the box below")
    set_run_font(run, size=10, bold=True, color=TEAL)

    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = True
    cell = table.cell(0, 0)
    shade_cell(cell, "F4F7F7")
    set_cell_border(cell)
    set_row_height(table.rows[0], height)
    cell.text = ""
    inner = cell.paragraphs[0]
    inner.alignment = WD_ALIGN_PARAGRAPH.CENTER
    inner.paragraph_format.space_before = Pt(18)
    r1 = inner.add_run("Paste screenshot here")
    set_run_font(r1, size=12, bold=True, color=GRAY)
    extra = cell.add_paragraph()
    extra.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r2 = extra.add_run(where)
    set_run_font(r2, size=11, italic=True, color=GRAY)
    extra2 = cell.add_paragraph()
    extra2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r3 = extra2.add_run("Leave a small margin around the image. Crop the browser chrome if it hides the feature.")
    set_run_font(r3, size=9, italic=True, color=GRAY)
    caption(doc, f"Figure {fig}: {title}")


def simple_table(doc, headers, rows, col_widths=None):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = ""
        para = cell.paragraphs[0]
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = para.add_run(h)
        set_run_font(run, size=11, bold=True, color=RGBColor(0xFF, 0xFF, 0xFF))
        shade_cell(cell, "1F343D")
    for r_i, row in enumerate(rows):
        for c_i, val in enumerate(row):
            cell = table.rows[r_i + 1].cells[c_i]
            cell.text = ""
            para = cell.paragraphs[0]
            run = para.add_run(str(val))
            set_run_font(run, size=11)
            if r_i % 2 == 1:
                shade_cell(cell, "EEF3F3")
    spacer = doc.add_paragraph()
    spacer.paragraph_format.space_after = Pt(8)
    return table


def code_block(doc, text):
    para = doc.add_paragraph()
    para.paragraph_format.left_indent = Cm(0.5)
    para.paragraph_format.space_before = Pt(6)
    para.paragraph_format.space_after = Pt(10)
    para.paragraph_format.line_spacing = 1.15
    run = para.add_run(text)
    set_run_font(run, name="Consolas", size=10, color=NAVY)
    return para


def page_break(doc):
    doc.add_page_break()


def setup_document():
    doc = Document()
    configure_styles(doc)
    section = doc.sections[0]
    section.page_width = Inches(8.27)
    section.page_height = Inches(11.69)
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.1)
    section.right_margin = Inches(1.0)
    header = section.header.paragraphs[0]
    header.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = header.add_run("Hill Cipher Cryptosystem and Interactive Lab  |  Project Report")
    set_run_font(run, size=9, italic=True, color=GRAY)
    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = footer.add_run("Educational project  •  Page ")
    set_run_font(run, size=10, color=GRAY)
    add_page_number(footer)
    return doc


def cover(doc):
    for _ in range(3):
        sp = doc.add_paragraph()
        sp.paragraph_format.space_after = Pt(0)
    t = doc.add_paragraph()
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = t.add_run("A PROJECT REPORT")
    set_run_font(r, size=16, bold=True, color=TEAL)
    t2 = doc.add_paragraph()
    t2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = t2.add_run("ON")
    set_run_font(r, size=13, color=GRAY)
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.paragraph_format.space_before = Pt(18)
    r = title.add_run("Hill Cipher Cryptosystem\nand Interactive Laboratory")
    set_run_font(r, size=26, bold=True, color=NAVY)
    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = sub.add_run(
        "An educational implementation of a classical polygraphic substitution\n"
        "cipher using modular linear algebra, Streamlit visualisation, and cryptanalysis"
    )
    set_run_font(r, size=13, italic=True, color=GRAY)
    meta = doc.add_paragraph()
    meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    meta.paragraph_format.space_before = Pt(36)
    r = meta.add_run(
        "Submitted in partial fulfilment of coursework in\nCyber Security / Cryptography Laboratory\n\n"
        "Prepared by\nDanish\n\nSource repository: hill_cipher\nDate: 1 November 2026"
    )
    set_run_font(r, size=13)
    note = doc.add_paragraph()
    note.alignment = WD_ALIGN_PARAGRAPH.CENTER
    note.paragraph_format.space_before = Pt(48)
    r = note.add_run(
        "IMPORTANT: This system is an educational demonstration.\n"
        "The Hill cipher is not suitable for protecting real communications."
    )
    set_run_font(r, size=11, italic=True, color=TEAL)
    page_break(doc)


def certificate_and_declaration(doc):
    heading(doc, "Certificate")
    p(
        doc,
        "This is to certify that the project titled “Hill Cipher Cryptosystem and Interactive "
        "Laboratory” has been completed as an educational software artefact. The work described "
        "in this report is based on the local source repository comprising app.py, hill_cipher.py, "
        "main.py, tests/test_hill_cipher.py, pyproject.toml, and README.md. The report documents "
        "design, implementation, testing, and security limitations of a classical cipher lab.",
    )
    p(
        doc,
        "The implementation provides a Streamlit web application and a command-line interface. "
        "Core modular arithmetic is isolated from presentation. Automated tests were executed "
        "with pytest. The project is intended for classroom demonstration of linear cryptanalysis "
        "ideas and must not be presented as a modern cryptographic product.",
    )
    p(doc, "Place: ________________________                    Date: 1 November 2026", align="left", first_line=False)
    p(doc, "Signature of student: ________________________", align="left", first_line=False)
    p(doc, "Signature of guide / examiner: ________________________", align="left", first_line=False)

    heading(doc, "Declaration")
    p(
        doc,
        "I declare that this report describes the Hill Cipher laboratory present in the project "
        "folder. Screenshots indicated by dashed boxes are to be inserted from a live run of "
        "the Streamlit application and the command-line tool. Mathematical claims that are "
        "supported by unit tests are identified as such. Recommendations about privacy and "
        "correctness are based on source review of the repository.",
    )
    p(
        doc,
        "I further declare that the Hill cipher is a historical algorithm. Nothing in this "
        "document should be read as advice to encrypt personal, organisational, or classified "
        "data with the software described here.",
    )
    p(doc, "Name: Danish", align="left", first_line=False)
    p(doc, "Signature: ________________________", align="left", first_line=False)
    page_break(doc)


def abstract_and_ack(doc):
    heading(doc, "Abstract")
    p(
        doc,
        "This report presents a complete educational laboratory for the Hill cipher, a polygraphic "
        "substitution system introduced by Lester S. Hill in 1929. Plaintext is mapped to integers "
        "in Z_26, grouped into column vectors of length n, and multiplied by an invertible n×n key "
        "matrix modulo 26. The laboratory implements n = 2 and n = 3, exact integer determinants, "
        "adjugate-based modular inversion, deterministic X-padding, known-plaintext key recovery, "
        "key-space enumeration for 2×2 matrices, a Caesar-versus-Hill frequency comparison, a "
        "practice quiz, a three-party chat simulation, and a grayscale image experiment modulo 256.",
    )
    p(
        doc,
        "The software is organised as a core engine (hill_cipher.py), a Streamlit interface (app.py), "
        "and a prompt-driven CLI (main.py). Packaging uses Python 3.11 or newer with NumPy, Plotly, "
        "and Streamlit declared in pyproject.toml. The configured pytest suite under tests/ contains "
        "fourteen tests covering cleaning, conversion, inversion, a known 2×2 example CIPHERS → "
        "ESONLPTV, a 3×3 round trip on ACTING, step breakdown of HI → TC, key-space count 157,248, "
        "quiz helpers, and image pixel round trips.",
    )
    p(
        doc,
        "The report emphasises that linearity is both the teaching strength and the cryptographic "
        "failure of the cipher. An adversary who obtains n independent plaintext blocks and matching "
        "ciphertext recovers K ≡ C · P⁻¹ (mod 26). The image mode demonstrates the same block-wise "
        "pattern leakage associated with electronic codebook behaviour. The interface currently "
        "writes the active key and text into URL query parameters; that behaviour is convenient for "
        "classroom sharing and inappropriate for any secret. Auto-play in the animated walkthrough "
        "calls a renderer that is defined later in the same module, which is a correctness risk on "
        "that path. The laboratory should remain clearly labelled as a demonstration.",
    )
    heading(doc, "Keywords")
    p(
        doc,
        "Hill cipher; modular arithmetic; matrix inversion; Streamlit; known-plaintext attack; "
        "key space; frequency analysis; educational cryptography; pytest.",
        first_line=False,
    )
    heading(doc, "Acknowledgements")
    p(
        doc,
        "Thanks are due to the course instructors who framed classical ciphers as objects of "
        "analysis rather than as security products, and to the open-source authors of NumPy, "
        "Streamlit, Plotly, and pytest. The laboratory follows the convention A = 0 … Z = 25 "
        "and the column-vector encryption model C = K · P (mod 26).",
    )
    page_break(doc)


def contents(doc):
    heading(doc, "Table of Contents")
    items = [
        "Certificate and Declaration",
        "Abstract and Acknowledgements",
        "List of Figures and Tables",
        "Chapter 1  Introduction and objectives",
        "Chapter 2  Background and literature of the Hill cipher",
        "Chapter 3  Mathematical model used in the laboratory",
        "Chapter 4  System requirements and project organisation",
        "Chapter 5  Core engine design (hill_cipher.py)",
        "Chapter 6  Streamlit application design (app.py)",
        "Chapter 7  Command-line interface",
        "Chapter 8  Encrypt / Decrypt workflow and screenshots",
        "Chapter 9  Step-by-step and animated walkthroughs",
        "Chapter 10 Known-plaintext attack and chat simulator",
        "Chapter 11 Frequency analysis, key space, and quiz",
        "Chapter 12 Image encryption modulo 256",
        "Chapter 13 Testing and verification",
        "Chapter 14 Security review, limitations, and ethics",
        "Chapter 15 Conclusion, future work, and references",
        "Appendix A  Worked numerical example (CIPHERS)",
        "Appendix B  Screenshot collection pages",
        "Appendix C  Test inventory and run log space",
    ]
    for item in items:
        para = doc.add_paragraph()
        para.paragraph_format.space_after = Pt(6)
        para.paragraph_format.line_spacing = 1.5
        run = para.add_run(item)
        set_run_font(run, size=12)

    heading(doc, "List of Figures")
    figs = [
        "1.1  Project folder structure in the file explorer",
        "1.2  README rendered in the editor or browser",
        "4.1  Terminal after uv sync / environment setup",
        "6.1  Streamlit home page with eleven tabs",
        "6.2  Sidebar key editor with 2×2 default matrix",
        "6.3  Valid-key metrics, determinant, and inverse LaTeX",
        "6.4  Invalid-key state with Run button disabled",
        "6.5  Preset example loader",
        "8.1  Encrypt of CIPHERS producing ESONLPTV",
        "8.2  Decrypt of ESONLPTV producing CIPHERSX",
        "8.3  Live mode updating while typing",
        "8.4  Round-trip verification and download action",
        "8.5  3×3 encryption of ACTING",
        "9.1  Step-by-step overview table",
        "9.2  Expanded block with matrix equation",
        "9.3  Animated walkthrough of one block",
        "10.1 Known-plaintext recovery of the sample key",
        "10.2 Failed recovery when P is not invertible",
        "10.3 Alice / Bob / Eve chat columns",
        "10.4 Eve recovering the chat key from a guess",
        "11.1 Caesar versus Hill frequency bar charts",
        "11.2 Key-space metrics 157,248 / 456,976",
        "11.3 Plotly heatmap for fixed b and c",
        "11.4 Modular inverse table modulo 26",
        "11.5 Practice quiz question and solution",
        "12.1 Original, encrypted, and decrypted grayscale images",
        "13.1 pytest -v terminal output (14 passed)",
        "13.2 CLI encrypt session",
        "13.3 Session history tab",
        "13.4 About tab reference table A=0…Z=25",
    ]
    for item in figs:
        para = doc.add_paragraph()
        para.paragraph_format.space_after = Pt(3)
        para.paragraph_format.line_spacing = 1.15
        run = para.add_run(item)
        set_run_font(run, size=11)
    heading(doc, "How to insert screenshots")
    p(
        doc,
        "Dashed boxes throughout this document are reserved for screenshots. Run the application "
        "with “uv run streamlit run app.py”, capture each named view, and paste the image into "
        "the matching box. Prefer PNG. Keep the figure caption already printed below the box. "
        "If a capture is wider than the page, crop to the control under discussion. Terminal "
        "screenshots belong in the CLI and testing chapters. Do not paste secrets from other "
        "systems; use only the laboratory’s synthetic examples such as CIPHERS and ACTING.",
        first_line=False,
    )
    page_break(doc)


def chapter1(doc):
    heading(doc, "Chapter 1  Introduction and Objectives")
    heading(doc, "1.1  Motivation", 2)
    p(
        doc,
        "Cybersecurity courses need artefacts that make abstract algebra visible. Students can "
        "memorise that a block cipher “mixes” letters, yet still fail to see a matrix multiply a "
        "vector. The Hill cipher is small enough to compute by hand and large enough to exhibit "
        "invertibility, padding, and a complete break under known plaintext. This project therefore "
        "implements the cipher twice: as a reusable Python engine and as an interactive laboratory "
        "in which every intermediate product is displayed.",
    )
    p(
        doc,
        "Modern algorithms such as AES are not suitable first examples of the same ideas. Their "
        "block sizes, round functions, and key schedules hide the linear algebra. A 2×2 Hill key "
        "with entries from 0 to 25 can be inspected, inverted, and attacked in a single laboratory "
        "session. The software keeps that session honest by refusing invalid keys in the sidebar, "
        "by showing gcd(det(K), 26), and by demonstrating why 157,248 of 456,976 possible 2×2 "
        "matrices are usable keys.",
    )
    heading(doc, "1.2  Problem statement", 2)
    p(
        doc,
        "Design and implement an educational cryptosystem laboratory that (a) encrypts and decrypts "
        "English letters with 2×2 or 3×3 Hill keys modulo 26, (b) visualises each block, (c) recovers "
        "a key from a known pair, (d) compares letter frequencies with Caesar cipher, (e) explores "
        "the 2×2 key space, (f) offers a practice quiz, (g) applies the same linear map to grayscale "
        "pixels modulo 256, and (h) remains testable independently of the user interface.",
    )
    heading(doc, "1.3  Objectives", 2)
    numbered(doc, "Separate mathematical operations from Streamlit widgets so tests can run headlessly.")
    numbered(doc, "Support only 2×2 and 3×3 keys at the public validator, matching the teaching scope.")
    numbered(doc, "Use exact integer determinants rather than floating-point values for 2×2 and 3×3.")
    numbered(doc, "Reject decryption of empty text and of lengths that are not multiples of the block size.")
    numbered(doc, "Show a worked known-plaintext attack K ≡ C · P⁻¹ (mod 26).")
    numbered(doc, "Enumerate valid 2×2 keys and visualise a slice of the space as a heatmap.")
    numbered(doc, "Label every “secure chat” control as a demonstration of weakness, not of safety.")
    numbered(doc, "Record fourteen automated tests that lock the known-good CIPHERS example.")
    heading(doc, "1.4  Scope and non-scope", 2)
    p(
        doc,
        "In scope: alphabetic Hill encryption modulo 26, educational visualisation, cryptanalysis "
        "demonstration, image-block experiment modulo 256, CLI, and unit tests. Out of scope: "
        "authenticated encryption, public-key algorithms, key distribution, password storage, "
        "network protocols, and any claim of confidentiality for real users. Unicode letters that "
        "pass str.isalpha are a recognised edge; the intended teaching alphabet is A–Z.",
    )
    heading(doc, "1.5  Organisation of the report", 2)
    p(
        doc,
        "Chapter 2 reviews the cipher’s history and why it failed as a field system. Chapter 3 "
        "fixes notation. Chapter 4 lists files and dependencies. Chapters 5–7 describe the engine, "
        "the web application, and the CLI. Chapters 8–12 are operational chapters with screenshot "
        "spaces. Chapter 13 reports tests. Chapter 14 is a security review of the laboratory itself. "
        "Chapter 15 concludes. Appendices hold the long CIPHERS calculation and extra paste pages.",
    )
    ss(doc, "1.1", "Project folder as seen in the file explorer", "Capture hill_cipher/ showing app.py, hill_cipher.py, main.py, tests/, pyproject.toml, README.md")
    ss(doc, "1.2", "Project README feature list", "Open README.md and capture the Streamlit feature list and known-good example")
    page_break(doc)


def chapter2(doc):
    heading(doc, "Chapter 2  Background and Literature")
    heading(doc, "2.1  Classical substitution before Hill", 2)
    p(
        doc,
        "Monoalphabetic ciphers replace each letter by one substitute. Frequency analysis, already "
        "practised in the ninth century on Arabic texts and later popularised in European cryptanalysis, "
        "recovers such systems because E, T, A, O remain visible as spikes. Polyalphabetic systems "
        "such as Vigenère delay the attack by cycling keys, but still operate letter-wise. Lester S. "
        "Hill’s contribution in 1929 was to encrypt several letters at once using linear algebra over "
        "the ring of integers modulo 26, the alphabet size of English as then encoded.",
    )
    p(
        doc,
        "The pedagogical value of that choice remains. Students who have seen matrices in a first "
        "linear algebra course can re-interpret encryption as a change of basis that must be invertible. "
        "They also see why 26 is an awkward modulus: it is not prime, so not every non-zero determinant "
        "has an inverse. The laboratory’s validity badge is a direct lesson in gcd(det, 26) = 1.",
    )
    heading(doc, "2.2  Why the Hill cipher is not used for secrecy", 2)
    p(
        doc,
        "Because encryption is C = K P (mod 26), knowledge of P and C yields K whenever P is "
        "invertible. Only n independent blocks are required for an n×n key. A chosen-plaintext "
        "attacker can send the standard basis and read the columns of K directly. Identical blocks "
        "always produce identical ciphertext, so repeated structure survives. Padding with a fixed "
        "letter X leaks length information. None of these properties is an implementation bug in "
        "this repository; they are properties of the mathematical object being taught.",
    )
    heading(doc, "2.3  Related educational tools", 2)
    p(
        doc,
        "Classroom tools often stop at a single encrypt/decrypt form. This laboratory adds an attack "
        "tab, a frequency comparison, a key-space explorer, a quiz, an image mode, and a chat narrative "
        "in which Eve is supposed to win. The narrative is deliberate. Naming the eavesdropper and "
        "showing a successful recovery is more honest than a green “encrypted” banner.",
    )
    heading(doc, "2.4  Linear algebra facts used without proof", 2)
    p(
        doc,
        "The report assumes: matrix multiplication is associative; a square matrix over a commutative "
        "ring is invertible if and only if its determinant is a unit of the ring; the inverse is "
        "(1/det) times the adjugate; the adjugate is the transpose of the cofactor matrix. For Z_26 "
        "the units are the residue classes coprime to 26, namely 1, 3, 5, 7, 9, 11, 15, 17, 19, 21, "
        "23, and 25. The engine’s modular inverse search simply tests these possibilities.",
    )
    heading(doc, "2.5  Mapping to the software", 2)
    p(
        doc,
        "integer_det implements the 2×2 and 3×3 expansion by minors. is_valid_key reports det, "
        "det mod 26, and gcd. matrix_mod_inverse builds cofactors, transposes them, and multiplies "
        "by the scalar inverse of the determinant. recover_key_from_pair searches combinations of "
        "plaintext blocks until an invertible P is found. count_valid_2x2_keys brute-forces the "
        "456,976 candidates. None of these functions depends on Streamlit.",
    )
    p(
        doc,
        "This separation is the main design decision of the project. A future maintainer can replace "
        "the web front end without rewriting modular arithmetic. Tests import hill_cipher directly. "
        "That is why Chapter 13 can report fourteen passing tests without launching a browser.",
    )
    page_break(doc)


def chapter3(doc):
    heading(doc, "Chapter 3  Mathematical Model Used in the Laboratory")
    heading(doc, "3.1  Alphabet and encoding", 2)
    p(
        doc,
        "Letters are encoded by A = 0, B = 1, …, Z = 25. The functions text_to_numbers and "
        "numbers_to_text implement this map. numbers_to_text reduces its arguments modulo 26 "
        "before converting, so a raw product such as 45 becomes 19, which is the letter T. The "
        "About tab of the application reprints the same table for students who are still learning "
        "the numbering.",
    )
    simple_table(
        doc,
        ["Letter", "Number", "Letter", "Number", "Letter", "Number"],
        [
            ["A", "0", "J", "9", "S", "18"],
            ["B", "1", "K", "10", "T", "19"],
            ["C", "2", "L", "11", "U", "20"],
            ["D", "3", "M", "12", "V", "21"],
            ["E", "4", "N", "13", "W", "22"],
            ["F", "5", "O", "14", "X", "23"],
            ["G", "6", "P", "15", "Y", "24"],
            ["H", "7", "Q", "16", "Z", "25"],
            ["I", "8", "R", "17", "", ""],
        ],
    )
    heading(doc, "3.2  Encryption and decryption equations", 2)
    p(
        doc,
        "Let n ∈ {2, 3} be the block size. A plaintext block is a column vector P in (Z_26)^n. "
        "A key is an n×n matrix K with entries in Z_26. Encryption is C ≡ K P (mod 26). Decryption "
        "is P ≡ K⁻¹ C (mod 26). The laboratory uses this column-vector convention consistently in "
        "code, in LaTeX, and in the step-breakdown formula strings. Mixing a row-vector convention "
        "from an external worksheet with this software will produce different ciphertext.",
    )
    heading(doc, "3.3  Invertibility condition", 2)
    p(
        doc,
        "K is a valid Hill key modulo 26 if and only if gcd(det(K) mod 26, 26) = 1. Because 26 = 2 × 13, "
        "the determinant class must be odd and not a multiple of 13. The sidebar explains failures in "
        "those terms: singular (det ≡ 0), shares factor 2, or shares factor 13. For image mode the "
        "modulus is 256 = 2^8, so an odd determinant is necessary and sufficient.",
    )
    heading(doc, "3.4  Padding convention", 2)
    p(
        doc,
        "encrypt appends the letter X until the cleaned length is a multiple of n. The known-good "
        "example CIPHERS has seven letters; with n = 2 it becomes CIPHERSX and encrypts to ESONLPTV. "
        "decrypt returns CIPHERSX. The original length is not stored, so a message that genuinely "
        "ended with X cannot be distinguished from padding. The report treats this as a teaching "
        "point rather than a defect to hide.",
    )
    heading(doc, "3.5  Cleaning convention", 2)
    p(
        doc,
        "clean_text uppercases, removes spaces, and keeps characters for which str.isalpha is true. "
        "Digits and punctuation disappear. Empty cleaned input makes encrypt return an empty string "
        "and makes decrypt raise ValueError. Tests lock HELLO, WORLD! → HELLOWORLD and the decryption "
        "of the dirty string “e s o n ! l p t v .” back to CIPHERSX.",
    )
    heading(doc, "3.6  Worked 2×2 fragment HI", 2)
    p(
        doc,
        "The sample key is [[3, 3], [2, 5]]. For HI one has P = [7, 8]^T. The product is "
        "[3·7 + 3·8, 2·7 + 5·8]^T = [45, 54]^T ≡ [19, 2]^T (mod 26), which is TC. "
        "get_step_breakdown records exactly these lists, and test_step_breakdown asserts them. "
        "Students should reproduce this fragment by hand before trusting the animated tab.",
    )
    heading(doc, "3.7  Known-plaintext recovery", 2)
    p(
        doc,
        "Given n plaintext columns that form invertible P and matching ciphertext columns C, "
        "K ≡ C P⁻¹ (mod 26). recover_key_from_pair searches combinations of blocks until such a P "
        "appears. Failure is returned as a structured error when lengths differ, when fewer than "
        "n² letters are present, or when every candidate P has gcd(det, 26) ≠ 1. Success includes "
        "the recovered key, selected block indices, and a check that encrypting the plaintext with "
        "the recovered key reproduces the ciphertext prefix.",
    )
    page_break(doc)


def chapter4(doc):
    heading(doc, "Chapter 4  System Requirements and Project Organisation")
    heading(doc, "4.1  Hardware and software", 2)
    p(
        doc,
        "Any recent Windows, macOS, or Linux machine with Python 3.11 or newer is sufficient. "
        "The laboratory is not computationally heavy except for the once-cached enumeration of "
        "456,976 keys. A browser is required for Streamlit, typically at http://localhost:8501. "
        "The CLI uses only the standard input stream and NumPy.",
    )
    heading(doc, "4.2  Dependencies", 2)
    simple_table(
        doc,
        ["Component", "Declared in", "Role"],
        [
            ["Python ≥ 3.11", "pyproject.toml requires-python", "Language runtime"],
            ["numpy ≥ 2.4.6", "dependencies", "Matrices and integer arrays"],
            ["streamlit ≥ 1.64.0", "dependencies", "Interactive web laboratory"],
            ["plotly ≥ 7.1.0", "dependencies", "Key-space heatmap"],
            ["pytest ≥ 9.2.0", "dependency-groups.dev", "Automated tests"],
            ["Pillow (optional)", "imported in image tab", "Grayscale image load"],
            ["uv", "README", "Environment and command runner"],
        ],
    )
    heading(doc, "4.3  File map", 2)
    simple_table(
        doc,
        ["File", "Responsibility"],
        [
            ["hill_cipher.py", "Engine: clean, encrypt, decrypt, invert, attack, quiz, image"],
            ["app.py", "Streamlit page, sidebar, eleven tabs, session state"],
            ["main.py", "Prompt-driven CLI encrypt/decrypt"],
            ["tests/test_hill_cipher.py", "Fourteen pytest cases"],
            ["test/test_hill.py", "Legacy print-based script, not in testpaths"],
            ["pyproject.toml", "Metadata, dependencies, pytest discovery"],
            ["README.md", "User documentation and known-good example"],
        ],
    )
    heading(doc, "4.4  How to run", 2)
    p(doc, "Synchronise the environment, then start the laboratory or the tests:", first_line=False)
    code_block(doc, "uv sync\nuv run streamlit run app.py\nuv run python main.py\nuv run pytest -v")
    p(
        doc,
        "The README states that the Streamlit URL is typically http://localhost:8501. Capture "
        "the terminal lines that print that URL as Figure 4.1. Keep this command sheet beside "
        "the screenshot pages in later chapters so an examiner can reproduce every figure.",
    )
    ss(doc, "4.1", "Terminal showing environment sync and Streamlit local URL", "Capture the shell after uv run streamlit run app.py, including the localhost link")
    heading(doc, "4.5  Session state overview", 2)
    p(
        doc,
        "app.py initialises matrix_size, nine key cells k_i_j, history, last_op, chat_log, chat_key, "
        "animation index, quiz score/streak, and a flag qp_loaded. Query parameters key, text, and "
        "mode restore a shared classroom example. The same parameters are written back as the user "
        "edits the sidebar and the encrypt box. Chapter 14 treats this as a privacy finding.",
    )
    page_break(doc)


def chapter5(doc):
    heading(doc, "Chapter 5  Core Engine Design")
    heading(doc, "5.1  Module contract", 2)
    p(
        doc,
        "hill_cipher.py documents its public surface in the module docstring: classical encryption "
        "and decryption, modular arithmetic, key validity, random valid keys, step breakdown, "
        "known-plaintext recovery, Caesar comparison helpers, key-space analysis, quiz generation, "
        "and mod-256 image helpers. The Streamlit file imports named functions from this module "
        "and does not reimplement matrix inversion.",
    )
    heading(doc, "5.2  Text helpers", 2)
    p(
        doc,
        "clean_text, text_to_numbers, and numbers_to_text form the alphabet boundary. Keeping them "
        "tiny is intentional. Every higher function that accepts English text calls clean_text, so "
        "a change in sanitisation policy has a single home. Tests cover punctuation stripping, "
        "empty strings, ABCZ ↔ [0,1,2,25], and wrap-around of 26 and 27 to A and B.",
    )
    heading(doc, "5.3  Determinants and inverses", 2)
    p(
        doc,
        "integer_det uses the closed 2×2 formula ad − bc and the 3×3 cofactor expansion. A "
        "floating-point fallback exists for other sizes via numpy.linalg.det rounded to int. "
        "Public validation refuses sizes other than 2 and 3, so the fallback is not on the "
        "supported teaching path. matrix_mod_inverse builds an integer cofactor matrix, transposes "
        "it, and multiplies by the scalar inverse of det modulo m. For 2×2 the cofactor of a single "
        "entry is a 1×1 determinant, which integer_det handles through the fallback; in practice "
        "the 1×1 case is a single integer.",
    )
    heading(doc, "5.4  encrypt and decrypt", 2)
    p(
        doc,
        "encrypt converts the key to integers, reads n from the first dimension, cleans text, "
        "returns empty on empty input, pads with X, then left-multiplies each block. It does not "
        "call is_valid_key. An invalid key therefore produces a string that cannot be inverted. "
        "The user interface compensates by disabling Run when the sidebar key is invalid. decrypt "
        "is stricter: it raises on empty cleaned text and on length not divisible by n, then "
        "inverts the key and multiplies. Invalid keys fail inside mod_inverse with a ValueError.",
    )
    heading(doc, "5.5  Step breakdown structure", 2)
    p(
        doc,
        "Each step dictionary contains block_index, input_chars, input_nums, raw_product, mod_nums, "
        "output_chars, and a formula string. mode is treated as encryption only when its lowercased "
        "value equals “encrypt”; any other string selects decryption. That permissive fallback is "
        "noted as a robustness issue: a typo becomes a decrypt attempt.",
    )
    heading(doc, "5.6  Attack, quiz, image, and counts", 2)
    p(
        doc,
        "recover_key_from_pair was summarised in Chapter 3. generate_quiz_question draws a valid "
        "key and a word of length 2n from a fixed vocabulary, then stores expected_answer and steps. "
        "check_quiz_answer compares clean_text of both sides. Image helpers generate keys with odd "
        "determinants, pad pixel vectors with zeros, and reuse matrix_mod_inverse with modulus 256. "
        "count_valid_2x2_keys is four nested loops; the test asserts the constant 157248.",
    )
    page_break(doc)


def chapter6(doc):
    heading(doc, "Chapter 6  Streamlit Application Design")
    heading(doc, "6.1  Page configuration", 2)
    p(
        doc,
        "The application title is Hill Cipher Suite, the layout is wide, and the sidebar starts "
        "expanded. The visible heading is “Interactive Hill Cipher Cryptosystem”. Eleven tabs "
        "are created in a single st.tabs call so that key state remains shared: Encrypt/Decrypt, "
        "Step-by-Step, Animated Walkthrough, Attack Demo, Caesar vs Hill, Secure Chat Simulator, "
        "Key Space, Practice Quiz, Image Encryption, History, and About.",
    )
    ss(doc, "6.1", "Full laboratory home page with tab strip", "Capture the title, intro sentence, and the row of eleven tabs")
    heading(doc, "6.2  Sidebar key editor", 2)
    p(
        doc,
        "The sidebar owns matrix size, a number_input grid, random valid key generation, determinant "
        "metrics, a validity badge, and LaTeX of K and K⁻¹. Changing size between 2 and 3 triggers "
        "st.rerun. The default 2×2 key is [[3, 3], [2, 5]] and the default 3×3 key is "
        "[[6, 24, 1], [13, 16, 10], [20, 17, 15]], matching the tests.",
    )
    ss(doc, "6.2", "Sidebar number grid for the default 2×2 key", "Capture Key Configuration with cells 3,3 / 2,5")
    ss(doc, "6.3", "Valid key analysis with inverse matrix", "Capture det, det mod 26, gcd = 1, VALID KEY, and both LaTeX matrices")
    ss(doc, "6.4", "Invalid key with Run disabled", "Load preset “Invalid 2×2 — gcd=2” and capture the error badge plus the encrypt tab warning")
    heading(doc, "6.3  Presets and sharing", 2)
    p(
        doc,
        "Presets include the valid 2×2 CIPHERS example, the invalid gcd=2 matrix, the valid 3×3 "
        "ACTING example, and a KPA pair. Selecting a preset writes session state and reruns. Query "
        "parameters serialise the current key as JSON and copy text and mode. This is convenient "
        "when an instructor wants every student on the same example. It is not a safe way to handle "
        "a real key, and the laboratory should not be described as sharing “secrets”.",
    )
    ss(doc, "6.5", "Preset example dropdown in the sidebar", "Capture the Load Preset Example select box with at least two named presets visible")
    heading(doc, "6.4  Helper rendering", 2)
    p(
        doc,
        "matrix_to_latex builds a bmatrix string for st.latex. The animated renderer builds a small "
        "HTML table of cell products. History stores timestamps and matrix lists in session_state "
        "and is discarded when the browser session ends. None of these helpers persist files except "
        "the explicit download button on the last encrypt/decrypt result.",
    )
    page_break(doc)


def chapter7(doc):
    heading(doc, "Chapter 7  Command-Line Interface")
    heading(doc, "7.1  Behaviour", 2)
    p(
        doc,
        "main.py prints a banner, reads n, reads n rows of integers, reads E or D, reads text, and "
        "calls encrypt or decrypt. It is intentionally small so that students who cannot run Streamlit "
        "can still complete the known-good example. It does not pre-validate invertibility or matrix "
        "shape beyond what NumPy and the engine do. A mistyped operation other than E is treated as "
        "decrypt.",
    )
    heading(doc, "7.2  Suggested demonstration script", 2)
    p(doc, "Use the following interaction for Figure 13.2 and for oral examination:", first_line=False)
    code_block(
        doc,
        "uv run python main.py\n"
        "Key matrix size (2 or 3): 2\n"
        "3 3\n"
        "2 5\n"
        "Encrypt (E) or Decrypt (D)? E\n"
        "Enter text: CIPHERS\n"
        "Encrypted Text: ESONLPTV",
    )
    p(
        doc,
        "A second run with D and ESONLPTV should print CIPHERSX. If the key is singular, decrypt "
        "raises from modular inversion. Capturing that traceback is useful in the testing chapter "
        "as evidence that invalid keys fail closed on the decrypt path.",
    )
    page_break(doc)


def chapter8(doc):
    heading(doc, "Chapter 8  Encrypt / Decrypt Workflow")
    heading(doc, "8.1  Controls", 2)
    p(
        doc,
        "The first tab offers Encrypt or Decrypt, an optional Live Mode toggle, a text field, a "
        "cleaned-text caption that announces X-padding, and a primary Run button that is disabled "
        "when the sidebar key is invalid. After a successful run, last_op is stored and the user "
        "may download a text file or verify a round trip.",
    )
    heading(doc, "8.2  Known-good 2×2 procedure", 2)
    numbered(doc, "Confirm sidebar size 2 and key [[3, 3], [2, 5]].")
    numbered(doc, "Choose Encrypt. Enter CIPHERS. Click Run.")
    numbered(doc, "Record ciphertext ESONLPTV. Note that one X was padded.")
    numbered(doc, "Switch to Decrypt, paste ESONLPTV, click Run, and record CIPHERSX.")
    numbered(doc, "Click Verify Round Trip on the encrypt result and capture the success message.")
    ss(doc, "8.1", "Encryption of CIPHERS to ESONLPTV", "Encrypt tab after Run; include cleaned caption and success banner")
    ss(doc, "8.2", "Decryption of ESONLPTV to CIPHERSX", "Decrypt tab showing padded plaintext")
    ss(doc, "8.3", "Live Mode producing output while typing", "Enable Live Mode and capture a partial word with live ciphertext")
    ss(doc, "8.4", "Result actions: download and round-trip", "Capture the Result Actions section after a successful encrypt")
    heading(doc, "8.3  3×3 procedure", 2)
    p(
        doc,
        "Load the valid 3×3 preset. The key [[6, 24, 1], [13, 16, 10], [20, 17, 15]] is accepted by "
        "is_valid_key. Encrypt ACTING. Because the length is already a multiple of 3, no padding is "
        "added and decrypt returns ACTING exactly, which is what test_3x3_round_trip asserts.",
    )
    ss(doc, "8.5", "3×3 encryption of ACTING", "After loading the Valid 3×3 preset, encrypt ACTING and capture key LaTeX plus output")
    heading(doc, "8.4  Operator notes", 2)
    p(
        doc,
        "Spaces and punctuation in the input disappear before encryption; students sometimes think "
        "the cipher “lost” letters. The caption showing the cleaned string is the explanation. "
        "Decrypting a string whose cleaned length is odd for n = 2 must fail with a block-size error. "
        "Capture that error once; it is the same message the unit test looks for.",
    )
    page_break(doc)


def chapter9(doc):
    heading(doc, "Chapter 9  Step-by-Step and Animated Walkthroughs")
    heading(doc, "9.1  Overview table", 2)
    p(
        doc,
        "The Step-by-Step tab calls get_step_breakdown and presents a dataframe of blocks. Each "
        "row shows input characters, numeric vector, raw product, reduced vector, and output "
        "letters. Expanders repeat the same data as a LaTeX matrix equation. This tab is the "
        "preferred figure for an examiner who wants to see mathematics rather than a chat story.",
    )
    ss(doc, "9.1", "Step-by-step overview table for CIPHERS", "Use Encrypt mode and CIPHERS; capture the dataframe of four blocks")
    ss(doc, "9.2", "Expanded block equation", "Open the expander for the first block (CI) and capture the LaTeX product")
    heading(doc, "9.2  Animation controls", 2)
    p(
        doc,
        "The animated tab adds Previous, Next, Auto-play, Stop, and a block slider. The renderer "
        "shows letter-to-number maps, a highlighted multiplication table, modulo reduction, and "
        "number-to-letter maps. Manual stepping is the reliable demonstration path. Auto-play "
        "sleeps one second per block and, in the current source order, calls _render_animated_block "
        "from a branch that runs before the function definition in the file. Capture manual "
        "stepping for the report; treat Auto-play as a known risk unless it has been repaired.",
    )
    ss(doc, "9.3", "Animated walkthrough of a single block", "Capture Block 1 with the HTML multiplication table visible")
    heading(doc, "9.3  Teaching script", 2)
    p(
        doc,
        "Ask the student to predict the first block of CIPHERS before revealing the expander. "
        "C = 2, I = 8. With K = [[3, 3], [2, 5]] the raw product is [30, 44] ≡ [4, 18] (mod 26) "
        "which is ES, matching the first two letters of ESONLPTV. Repeating this for HI (the unit "
        "test fragment) builds trust that the animation is not a separate, possibly wrong, engine.",
    )
    page_break(doc)


def chapter10(doc):
    heading(doc, "Chapter 10  Known-Plaintext Attack and Chat Simulator")
    heading(doc, "10.1  Attack tab", 2)
    p(
        doc,
        "The Attack Demo states that the cipher is strictly linear and shows K ≡ C P⁻¹ (mod 26). "
        "Buttons load the 2×2 CIPHERSX / ESONLPTV pair, a 3×3 ACTING pair, or a pair generated from "
        "the sidebar key. Recover Key Matrix calls recover_key_from_pair. On success the recovered "
        "matrix is typeset, compared with the sidebar, and optionally copied back into the sidebar.",
    )
    ss(doc, "10.1", "Successful recovery of the sample 2×2 key", "Load 2×2 test pair, click Recover, capture recovered K and the derivation line")
    ss(doc, "10.2", "Failed recovery message", "Enter a too-short or mismatched pair and capture the structured error")
    heading(doc, "10.2  Conditions that make the attack fail", 2)
    p(
        doc,
        "Equal cleaned lengths are required. At least n² letters are required. Some subset of n "
        "plaintext blocks must form an invertible matrix modulo 26. A student who types a guess "
        "that is linearly dependent, or far from the true message, should see failure. The chat "
        "tab can otherwise over-promise that “one guessed message always reveals the key”.",
    )
    heading(doc, "10.3  Alice, Bob, and Eve", 2)
    p(
        doc,
        "The simulator generates a session key, encrypts Alice’s messages, shows Bob the decrypt, "
        "and shows Eve only ciphertext. Eve selects a message, types a guessed plaintext, and "
        "attempts recovery. If she succeeds, every intercepted line is decrypted and a warning "
        "explains that linearity, not a coding mistake, caused the break. Keep that warning in "
        "the screenshot; it is the learning outcome of the tab.",
    )
    ss(doc, "10.3", "Three-column chat after at least two messages", "Generate a chat key, send two short messages, capture Alice, Bob, and Eve columns")
    ss(doc, "10.4", "Eve recovering the chat key", "Guess the true plaintext of message 1 and capture key recovery plus the weakness warning")
    page_break(doc)


def chapter11(doc):
    heading(doc, "Chapter 11  Frequency Analysis, Key Space, and Quiz")
    heading(doc, "11.1  Caesar versus Hill", 2)
    p(
        doc,
        "Caesar encryption is a uniform shift; its frequency histogram is a translation of the "
        "plaintext histogram, so the sample standard deviation of letter counts is unchanged. "
        "Hill encryption mixes letters inside a block, so spikes usually fall. The tab reports "
        "three standard deviations. The charts are demonstrations, not a proof of cryptographic "
        "diffusion in the modern sense, and they must not be captioned as evidence of security.",
    )
    ss(doc, "11.1", "Side-by-side frequency bar charts", "Use the default analysis paragraph and capture both charts plus the three std-dev metrics")
    heading(doc, "11.2  Key-space explorer", 2)
    p(
        doc,
        "All 26⁴ = 456,976 matrices with entries in 0…25 are examined. 157,248 are valid (34.4%). "
        "The count is cached. A Plotly heatmap fixes b and c and colours the (a, d) plane. A table "
        "lists inverses of 1…25 modulo 26, with even numbers and multiples of 13 marked as having "
        "no inverse. This tab is the right place to discuss why 26 is a poor modulus compared with "
        "a prime.",
    )
    ss(doc, "11.2", "Key-space metrics cards", "Capture Total / Valid / Invalid / Valid % showing 157,248 valid keys")
    ss(doc, "11.3", "Interactive validity heatmap", "Capture the Plotly heatmap for some b, c pair with the title showing valid/676")
    ss(doc, "11.4", "Modular inverse table modulo 26", "Capture the dataframe including 3 → 9 and 2 → no inverse")
    heading(doc, "11.3  Practice quiz", 2)
    p(
        doc,
        "Questions are generated for 2×2 or 3×3 and for encrypt or decrypt. Score and streak live "
        "in session state. Incorrect answers reveal block-wise formulae from get_step_breakdown. "
        "Answers are compared after clean_text, so spaces and case do not fail a correct letter "
        "sequence. The quiz is a check of arithmetic, not of operational security.",
    )
    ss(doc, "11.5", "Quiz item with key, prompt, and solution", "Generate a 2×2 encrypt question, submit a wrong answer once, and capture the step-by-step reveal")
    page_break(doc)


def chapter12(doc):
    heading(doc, "Chapter 12  Image Encryption Modulo 256")
    heading(doc, "12.1  Model", 2)
    p(
        doc,
        "Pixels are treated as bytes in 0…255. The same block-linear map is applied modulo 256. "
        "Because 256 is a power of two, invertibility reduces to an odd determinant. Padding uses "
        "zeros rather than the letter X. The user interface converts uploads to grayscale with "
        "PIL, flattens the array, encrypts, reshapes, and displays original, encrypted, and "
        "decrypted images in three columns.",
    )
    heading(doc, "12.2  What the encrypted image should show", 2)
    p(
        doc,
        "A photograph with large flat regions will often retain outlines after encryption because "
        "identical blocks map to identical blocks. That is the electronic-codebook lesson. The tab "
        "text already compares this behaviour with AES-ECB. The laboratory does not implement CBC "
        "or CTR; adding those modes would change the teaching topic from Hill’s linear map to "
        "modern block-cipher modes.",
    )
    heading(doc, "12.3  State caution", 2)
    p(
        doc,
        "The generated image key is stored in session_state independently of the size selector. "
        "Changing the size dropdown without pressing Generate can leave a key whose dimension "
        "does not match the selector. For the report, generate a key immediately after choosing "
        "2 or 3, then upload the image.",
    )
    ss(
        doc,
        "12.1",
        "Original, encrypted, and decrypted grayscale images",
        "Upload a simple high-contrast PNG, generate a valid mod-256 key, capture the three columns and the round-trip success message",
        height=3.2,
    )
    page_break(doc)


def chapter13(doc):
    heading(doc, "Chapter 13  Testing and Verification")
    heading(doc, "13.1  Configured suite", 2)
    p(
        doc,
        "pyproject.toml sets testpaths to tests and pythonpath to the project root. pytest therefore "
        "collects tests/test_hill_cipher.py and ignores the legacy print script under test/. The "
        "fourteen tests are listed in Appendix C. They are unit tests of the engine. They do not "
        "import Streamlit, click widgets, or open a browser.",
    )
    heading(doc, "13.2  Behaviours locked by tests", 2)
    bullet(doc, "Cleaning of mixed punctuation and empty strings.")
    bullet(doc, "A=0 encoding and wrap-around of numbers ≥ 26.")
    bullet(doc, "Inverses 3⁻¹ ≡ 9, 9⁻¹ ≡ 3, 7⁻¹ ≡ 15 (mod 26); 2 and 13 have no inverse.")
    bullet(doc, "CIPHERS with [[3,3],[2,5]] encrypts to ESONLPTV and decrypts to CIPHERSX.")
    bullet(doc, "Dirty ciphertext still decrypts; odd length and empty text raise ValueError.")
    bullet(doc, "3×3 ACTING round trip on the documented invertible key.")
    bullet(doc, "Valid, even-determinant, and singular keys.")
    bullet(doc, "HI step breakdown 7,8 → 45,54 → 19,2 → TC.")
    bullet(doc, "Known-plaintext recovery of the sample 2×2 key.")
    bullet(doc, "Caesar HELLO → KHOOR and frequency counts.")
    bullet(doc, "157,248 valid 2×2 keys; inverse table flags 2 as non-invertible.")
    bullet(doc, "Quiz generation shapes and image pixel round trips for 2×2 and 3×3.")
    ss(doc, "13.1", "pytest verbose run showing 14 passed", "Run uv run pytest -v in hill_cipher/ and capture the full summary")
    ss(doc, "13.2", "CLI encrypting CIPHERS", "Capture the complete CLI session with output ESONLPTV")
    ss(doc, "13.3", "History tab after several operations", "Run two encrypts and one decrypt, then capture the history dataframe")
    ss(doc, "13.4", "About tab letter-to-number table", "Open About and capture the A=0…Z=25 reference expander")
    heading(doc, "13.3  Gaps", 2)
    p(
        doc,
        "There are no automated tests for query-parameter parsing, preset rerun loops, autoplay, "
        "chat guesses, image uploads, accessibility, or performance of the heatmap. The fourteen "
        "passes are necessary evidence for the engine and insufficient evidence for the whole "
        "application. Chapter 14 recommendations should not be described as already tested.",
    )
    page_break(doc)


def chapter14(doc):
    heading(doc, "Chapter 14  Security Review, Limitations, and Ethics")
    heading(doc, "14.1  The cipher versus the laboratory", 2)
    p(
        doc,
        "Two different questions must not be mixed. The first is whether the Hill cipher provides "
        "modern confidentiality: it does not. The second is whether this laboratory mishandles data "
        "that a student types while learning: it can, if query parameters copy keys into URLs, if "
        "history is shown on a shared projector, or if a user uploads a sensitive photograph to the "
        "image tab. Educational software still has a duty not to train unsafe habits.",
    )
    heading(doc, "14.2  Findings from source review", 2)
    simple_table(
        doc,
        ["ID", "Finding", "Severity", "Treatment"],
        [
            ["F1", "Key and text written to st.query_params", "High for real secrets; acceptable if labelled demo", "Make sharing opt-in; warn in the UI"],
            ["F2", "Auto-play calls renderer before definition", "Functional", "Move helper above the tab or always define first"],
            ["F3", "encrypt does not validate invertibility", "Low; UI disables Run", "Keep UI guard; consider engine-level check"],
            ["F4", "str.isalpha may accept non-A–Z letters", "Low teaching mismatch", "Filter A–Z explicitly if alphabet is strict"],
            ["F5", "Padding X is ambiguous", "Inherent to the cipher", "Document; do not hide"],
            ["F6", "Chat naming may imply real security", "Medium pedagogical", "Keep Eve-wins copy adjacent to controls"],
            ["F7", "Image ECB leakage", "Inherent demonstration", "Keep the warning; do not add false “secure” labels"],
            ["F8", "CLI trusts input shape/operation", "Low", "Add validation messages for lab usability"],
        ],
    )
    heading(doc, "14.3  Ethics of demonstration attacks", 2)
    p(
        doc,
        "The known-plaintext tab is a demonstration against a toy cipher that the user controls. "
        "It is not a guide to attacking other people’s systems. The report therefore includes the "
        "attack mathematics that the laboratory already displays, and it does not add exploit "
        "instructions for networks, passwords, or third-party services. Students should practise "
        "the recovery on CIPHERSX / ESONLPTV only.",
    )
    heading(doc, "14.4  Accessibility and inclusion", 2)
    p(
        doc,
        "Validity is colour-coded (green/red heatmap, success/error banners). Colour should not be "
        "the only channel: the metrics, captions, and inverse table already provide text. Future "
        "work should keep hover text and status strings when restyling charts. Keyboard-only use "
        "of Streamlit widgets was not audited for this report.",
    )
    heading(doc, "14.5  Reproducibility", 2)
    p(
        doc,
        "Reproducible claims in this document are those backed by named functions and tests. UI "
        "screenshots will differ slightly with Streamlit versions and browser zoom. The known-good "
        "ciphertext ESONLPTV must not differ; if it does, the engine or the key was not the one "
        "documented.",
    )
    page_break(doc)


def chapter15(doc):
    heading(doc, "Chapter 15  Conclusion, Future Work, and References")
    heading(doc, "15.1  Conclusion", 2)
    p(
        doc,
        "The laboratory achieves its educational purpose. A student can form a key, see why it is "
        "valid, encrypt CIPHERS, inspect each block, invert the map, recover the key from a known "
        "pair, compare frequencies with Caesar, count the 2×2 key space, sit a short quiz, and watch "
        "an image leak patterns under block-linear encryption. The engine is covered by fourteen "
        "unit tests. The interface makes the weakness of linearity visible instead of concealing it.",
    )
    p(
        doc,
        "The same honesty should apply to operational details: URL sharing is not confidential, "
        "autoplay needs a definition-order fix, and no amount of Streamlit polish turns Hill into "
        "AES. Used with those caveats, the project is a complete coursework artefact in classical "
        "cryptography and software organisation.",
    )
    heading(doc, "15.2  Future work", 2)
    numbered(doc, "Validate mode ∈ {encrypt, decrypt} in get_step_breakdown.")
    numbered(doc, "Define the animation renderer before any autoplay call.")
    numbered(doc, "Make query-parameter sharing opt-in with a visible warning.")
    numbered(doc, "Restrict clean_text to A–Z if that is the documented alphabet.")
    numbered(doc, "Add Streamlit smoke tests for presets, invalid keys, and attack failure.")
    numbered(doc, "Synchronise image key dimension with the size selector.")
    numbered(doc, "Improve CLI error messages for shape and operation.")
    numbered(doc, "Optional: show determinant arithmetic as fractions of a page of longhand.")
    heading(doc, "15.3  References and sources", 2)
    p(doc, "The following sources informed the laboratory and this report. They are not copied verbatim.", first_line=False)
    numbered(doc, "Hill, L. S. Cryptography in an Algebraic Alphabet. American Mathematical Monthly, 1929.")
    numbered(doc, "Stallings, W. Cryptography and Network Security. Pearson. Chapters on classical encryption.")
    numbered(doc, "Stallings / course notes on modular inverses and gcd conditions for Hill keys.")
    numbered(doc, "NumPy documentation: ndarray, integer dtypes, matrix products.")
    numbered(doc, "Streamlit documentation: session_state, query_params, tabs, caching.")
    numbered(doc, "Plotly heatmap documentation used by the key-space tab.")
    numbered(doc, "pytest documentation: assertion rewriting and test discovery.")
    numbered(doc, "Project README.md, pyproject.toml, hill_cipher.py, app.py, main.py, tests/test_hill_cipher.py.")
    heading(doc, "15.4  Closing statement", 2)
    p(
        doc,
        "Insert remaining screenshots, attach the pytest log, and submit this file as the official "
        "project report. The empty boxes are intentional. They are the practical evidence that the "
        "laboratory runs on the author’s machine, which no generated paragraph can replace.",
    )
    page_break(doc)


def appendix_a(doc):
    heading(doc, "Appendix A  Worked Numerical Example (CIPHERS)")
    p(
        doc,
        "Key K = [[3, 3], [2, 5]]. det(K) = 15 − 6 = 9. 9 mod 26 = 9. gcd(9, 26) = 1, so the key "
        "is valid. The scalar inverse of 9 modulo 26 is 3 because 9 × 3 = 27 ≡ 1. The adjugate of "
        "a 2×2 matrix [[a, b], [c, d]] is [[d, −b], [−c, a]], so adj(K) = [[5, −3], [−2, 3]] ≡ "
        "[[5, 23], [24, 3]] (mod 26). Then K⁻¹ ≡ 3 · adj(K) ≡ [[15, 69], [72, 9]] ≡ [[15, 17], [20, 9]] "
        "(mod 26). Students should verify K K⁻¹ ≡ I (mod 26) before encrypting a long word.",
    )
    p(
        doc,
        "Plaintext CIPHERS cleans to CIPHERS and pads to CIPHERSX. Blocks: CI, PH, ER, SX.",
        first_line=False,
    )
    simple_table(
        doc,
        ["Block", "Letters", "P vector", "K P (raw)", "mod 26", "Output"],
        [
            ["1", "CI", "[2, 8]", "[30, 44]", "[4, 18]", "ES"],
            ["2", "PH", "[15, 7]", "[66, 65]", "[14, 13]", "ON"],
            ["3", "ER", "[4, 17]", "[63, 93]", "[11, 15]", "LP"],
            ["4", "SX", "[18, 23]", "[123, 151]", "[19, 21]", "TV"],
        ],
    )
    p(
        doc,
        "Concatenated ciphertext: ESONLPTV. This matches encrypt() and the README known-good "
        "example. Decryption multiplies each ciphertext block by K⁻¹ and yields CIPHERSX. The "
        "final X is padding. Capture your software producing the same four blocks in Figure 9.1 "
        "and attach it next to this table during binding.",
    )
    p(
        doc,
        "For the attack, take plaintext blocks of CIPHERSX and ciphertext blocks of ESONLPTV. "
        "Two independent plaintext columns form P. If the first two blocks are used, P has columns "
        "[2, 8] and [15, 7]. If that P is invertible modulo 26, K is recovered in one multiplication. "
        "The unit test uses the full strings and asserts equality with [[3, 3], [2, 5]].",
    )
    page_break(doc)


def appendix_b(doc):
    heading(doc, "Appendix B  Extra Screenshot Collection")
    p(
        doc,
        "Use these spare boxes if a chapter box overflowed or if an examiner asks for additional "
        "evidence. Label each paste with a short handwritten note if you change the suggested title.",
        first_line=False,
    )
    extras = [
        ("B.1", "Invalid key preset and disabled Run button (repeat if Chapter 6 is full)", "Invalid 2×2 preset; include sidebar and encrypt tab"),
        ("B.2", "Random valid key toast after generation", "Click Generate Random Valid Key; capture toast and new inverse"),
        ("B.3", "Shareable URL in the browser address bar", "After encrypting, capture the address bar with query parameters visible; crop personal paths"),
        ("B.4", "Decrypt block-length error for odd text", "Decrypt ESONLPT with a 2×2 key and capture the error"),
        ("B.5", "3×3 step-by-step of ACTING", "Step tab, 3×3 key, two blocks"),
        ("B.6", "Attack derivation LaTeX line only", "Zoom to K ≡ C · P⁻¹ equation after recovery"),
        ("B.7", "Chat key LaTeX before any message", "After Generate Chat Key, before Send"),
        ("B.8", "Failed Eve guess", "Type a wrong guess with enough letters; capture Attack failed"),
        ("B.9", "Key-space heatmap at a second (b, c) pair", "Change sliders from the Chapter 11 figure"),
        ("B.10", "Quiz correct answer with balloons/success", "Submit a correct encrypt answer"),
        ("B.11", "Image tab warning about ECB leakage", "Capture the explanatory markdown before upload"),
        ("B.12", "Pillow missing error (optional)", "Only if PIL is not installed; otherwise leave blank"),
        ("B.13", "History cleared confirmation", "Click Clear History and capture the empty state"),
        ("B.14", "Mathematical formulation expander", "About tab, Mathematical Formulation open"),
        ("B.15", "Cryptographic weaknesses expander", "About tab, weaknesses list"),
        ("B.16", "Project running beside this Word document", "Wide desktop capture: Streamlit on one side, this report on the other"),
        ("B.17", "pytest -q one-line summary", "Capture 14 passed"),
        ("B.18", "uv run python main.py decrypt CIPHERSX path", "CLI decrypt session"),
        ("B.19", "Code editor on encrypt() with padding loop", "hill_cipher.py encrypt function on screen"),
        ("B.20", "Code editor on recover_key_from_pair", "Show the combination search loop"),
        ("B.21", "pyproject.toml dependencies section", "Capture requires-python and dependencies"),
        ("B.22", "Default 2×2 inverse displayed as LaTeX only", "Crop to K and K⁻¹"),
        ("B.23", "Live mode warning with invalid key", "Invalid key + Live Mode on"),
        ("B.24", "Downloaded result.txt opened in Notepad", "After Download Result as .txt"),
    ]
    for fig, title, where in extras:
        ss(doc, fig, title, where, height=2.7)
    page_break(doc)


def appendix_c(doc):
    heading(doc, "Appendix C  Test Inventory and Run Log Space")
    simple_table(
        doc,
        ["#", "Test function", "What it locks"],
        [
            ["1", "test_clean_text", "HELLO WORLD punctuation; empty string"],
            ["2", "test_text_and_number_conversions", "ABCZ mapping; wrap 26,27"],
            ["3", "test_mod_inverse", "3,9,7 inverses; 2 and 13 fail"],
            ["4", "test_known_good_2x2", "CIPHERS ↔ ESONLPTV / CIPHERSX"],
            ["5", "test_decrypt_bug_fix_cleaning_and_validation", "Dirty CT; odd length; empty"],
            ["6", "test_3x3_round_trip", "ACTING with documented 3×3 key"],
            ["7", "test_is_valid_key", "Valid, gcd=2, singular"],
            ["8", "test_generate_valid_key", "Five random 2×2 and 3×3 keys"],
            ["9", "test_step_breakdown", "HI → TC numbers 7,8,45,54,19,2"],
            ["10", "test_known_plaintext_attack_recovery", "Recover sample 2×2 key"],
            ["11", "test_caesar_encrypt_and_frequencies", "HELLO→KHOOR; AABBBCCCC counts"],
            ["12", "test_key_space_count", "157248; grid 26×26; inverse table"],
            ["13", "test_quiz_helpers", "2×2 encrypt and 3×3 decrypt shapes"],
            ["14", "test_image_mod256_encryption_round_trip", "Pixel round trip 2×2 and 3×3"],
        ],
    )
    p(
        doc,
        "Paste the raw pytest log in the box below. Do not retype results. If a test is skipped or "
        "failed on the submission machine, leave the failure visible and explain it in one sentence "
        "under the box.",
        first_line=False,
    )
    ss(doc, "C.1", "Full pytest -v log", "Paste the complete terminal output, including failed tests if any", height=3.4)
    ss(doc, "C.2", "Second run after a code change (optional)", "If you modified the engine, paste a new log; otherwise leave blank", height=2.6)
    heading(doc, "C.1  Oral examination checklist", 2)
    bullet(doc, "State the encoding A=0 and the equation C = K P (mod 26).")
    bullet(doc, "Compute det of [[3,3],[2,5]] and explain gcd(9, 26) = 1.")
    bullet(doc, "Show why [[2,3],[4,5]] is rejected.")
    bullet(doc, "Encrypt one block by hand and match the step tab.")
    bullet(doc, "Explain padding of CIPHERS to CIPHERSX.")
    bullet(doc, "Write K = C P⁻¹ and recover a 2×2 key on the attack tab.")
    bullet(doc, "State that 157,248 of 456,976 keys are valid.")
    bullet(doc, "Explain why an odd determinant is enough modulo 256.")
    bullet(doc, "Refuse to claim that the laboratory is secure messaging.")
    heading(doc, "C.2  Final submission reminder", 2)
    p(
        doc,
        "Print or export this Word file to PDF only after screenshots are pasted, so that figure "
        "boxes are not empty in the PDF. Keep fonts as Times New Roman. Do not reduce margins "
        "below 1 inch. Update the name on the cover if a different author line is required by "
        "the department. The software remains an educational Hill cipher laboratory.",
    )
    ss(doc, "C.3", "Blank spare screenshot", "Any additional evidence requested by the examiner", height=3.0)
    ss(doc, "C.4", "Blank spare screenshot", "Any additional evidence requested by the examiner", height=3.0)
    ss(doc, "C.5", "Blank spare screenshot", "Any additional evidence requested by the examiner", height=3.0)


def appendix_d(doc):
    page_break(doc)
    heading(doc, "Appendix D  Complete Screenshot Workbook")
    p(
        doc,
        "This appendix is a paste workbook. Each box corresponds to one observable state of the "
        "laboratory. Fill as many as you can; leave unused boxes empty rather than stretching a "
        "screenshot. The empty area is reserved so that figures remain large enough to read when "
        "printed on A4.",
        first_line=False,
    )
    shots = [
        ("D.1", "Browser tab title Hill Cipher Suite", "Capture only the browser tab strip"),
        ("D.2", "Streamlit running locally status", "http://localhost:8501 loaded"),
        ("D.3", "Sidebar fully scrolled to inverse matrices", "K and K⁻¹ LaTeX"),
        ("D.4", "Matrix size selector set to 3", "n × n select box"),
        ("D.5", "Generate Random Valid Key result", "New numbers and VALID badge"),
        ("D.6", "Encrypt HELLO with default 2×2", "Show padding caption and ciphertext"),
        ("D.7", "Decrypt with lowercase mixed punctuation", "Match the dirty-ciphertext test"),
        ("D.8", "Live Mode off, Run enabled", "Primary button visible"),
        ("D.9", "Download filename dialog or saved txt", "hill_cipher_encrypt_result.txt"),
        ("D.10", "Round-trip padding none for ACTING", "Success without extra X"),
        ("D.11", "Step mode Decrypt on ESONLPTV", "Four decrypt blocks"),
        ("D.12", "Second block expander PH → ON", "LaTeX for block 2"),
        ("D.13", "Third block expander ER → LP", "LaTeX for block 3"),
        ("D.14", "Fourth block expander SX → TV", "LaTeX for block 4"),
        ("D.15", "Animation Previous/Next enabled states", "Middle block so both buttons work"),
        ("D.16", "Animation slider on last block", "Block index at max"),
        ("D.17", "Attack 3×3 ACTING recovery", "Recovered 3×3 key"),
        ("D.18", "Generate pair from sidebar key", "HILLCIPHERWEAKNESS pair"),
        ("D.19", "Recovered key matches sidebar message", "Green check under recovered K"),
        ("D.20", "Apply recovered key toast", "Sidebar cells updated"),
        ("D.21", "Caesar shift slider at 13", "Charts at rot13"),
        ("D.22", "Frequency std-dev metrics close-up", "Three metric cards"),
        ("D.23", "Chat empty state before key", "No chat key set yet"),
        ("D.24", "Eve column showing ciphertext only", "Red ciphertext bubbles"),
        ("D.25", "Heatmap b=0, c=0", "Validity for a,d plane"),
        ("D.26", "Quiz 3×3 decrypt prompt", "Six-letter ciphertext"),
        ("D.27", "Image upload control empty", "File uploader widget"),
        ("D.28", "History with key matrix JSON visible", "Key Matrix column"),
        ("D.29", "pytest collection count 14 items", "collected 14 items line"),
        ("D.30", "README known-good example section", "Key, CIPHERS, ESONLPTV"),
    ]
    for fig, title, where in shots:
        ss(doc, fig, title, where, height=2.85)


def extra_fill_pages(doc):

    """Additional discussion pages so the bound report reaches ~80 pages with screenshot boxes."""
    page_break(doc)
    heading(doc, "Supplementary Notes for Examiners")
    heading(doc, "S.1  Why fourteen tests are the right size for this engine", 2)
    p(
        doc,
        "A course laboratory does not need thousands of randomly generated matrices in order to be "
        "trustworthy. It needs a handful of examples that an examiner can recompute, plus a few "
        "negative paths. The CIPHERS vector is the positive path. Odd-length decrypt is the "
        "validation path. Singular and even-determinant keys are the algebraic path. HI is the "
        "arithmetic path. 157,248 is the counting path. Image bytes [0, 15, 128, 200, 255, 42] are "
        "the modulus-change path. Together they pin the behaviours this report describes.",
    )
    p(
        doc,
        "Adding property-based tests would be valuable later: for every valid 2×2 key and every "
        "alphabetic string, decrypt(encrypt(text)) should equal the padded plaintext. The current "
        "generate_valid_key tests already sample the generator five times. They do not yet close "
        "the round-trip theorem for arbitrary strings. Students who extend the project could add "
        "that property without touching Streamlit.",
    )
    heading(doc, "S.2  Classroom timing", 2)
    p(
        doc,
        "A two-hour lab can follow this sequence: fifteen minutes of encoding and a hand 2×2 "
        "product; fifteen minutes of encrypt/decrypt on CIPHERS; twenty minutes of step-by-step; "
        "twenty minutes of attack; fifteen minutes of frequency charts; fifteen minutes of key "
        "space; remaining time on quiz or image. The chat simulator is best used last, when students "
        "already know why Eve succeeds, so the cartoon names do not replace the algebra.",
    )
    ss(doc, "S.1", "Classroom projector showing the encrypt tab", "Optional: capture the app in presentation/full-browser mode")
    heading(doc, "S.3  Comparison with a handwritten assignment", 2)
    p(
        doc,
        "A paper assignment can ask for one encryption and one inverse. It cannot cheaply ask every "
        "student to count 456,976 keys or to watch an image leak. The software earns its complexity "
        "on those tasks. It should not replace the handwritten HI product. This report therefore "
        "keeps Appendix A in longhand style even though the computer already knows the answer.",
    )
    heading(doc, "S.4  Maintenance notes for the next cohort", 2)
    p(
        doc,
        "If Streamlit changes query_params semantics, sharing may break before encryption does. "
        "If NumPy changes default dtypes, integer_det should still cast with dtype=int. If Plotly "
        "changes heatmap hover templates, the key-space tab may need a one-line update. None of "
        "those framework shifts should alter ESONLPTV. Treat that ciphertext as a canary.",
    )
    ss(doc, "S.2", "Canary check: CIPHERS still encrypts to ESONLPTV", "Repeat Figure 8.1 at submission time if earlier captures are old")
    heading(doc, "S.5  Glossary", 2)
    simple_table(
        doc,
        ["Term", "Meaning in this laboratory"],
        [
            ["Block", "n letters treated as one vector"],
            ["Clean text", "Uppercase alphabetic characters only"],
            ["Coprime determinant", "gcd(det mod 26, 26) = 1"],
            ["KPA", "Known-plaintext attack recovering K"],
            ["Padding X", "Letter appended so length is a multiple of n"],
            ["Query params", "Key/text/mode copied into the page URL"],
            ["Valid key", "Square 2×2 or 3×3 matrix with invertible det"],
            ["Mod 256 mode", "Same linear map on grayscale bytes"],
        ],
    )
    ss(doc, "S.3", "Glossary used beside a live demo (optional)", "Any photo of a whiteboard with A=0…Z=25")
    heading(doc, "S.6  Index of important constants", 2)
    p(
        doc,
        "Alphabet size 26; image modulus 256; valid 2×2 keys 157,248; total 2×2 keys 456,976; "
        "default key [[3, 3], [2, 5]]; default 3×3 [[6, 24, 1], [13, 16, 10], [20, 17, 15]]; "
        "sample plaintext CIPHERS; sample ciphertext ESONLPTV; padded decrypt CIPHERSX; HI product "
        "[45, 54] ≡ [19, 2]; 3⁻¹ ≡ 9 (mod 26); pytest tests 14; Python 3.11. These constants "
        "should appear consistently in screenshots and in oral answers.",
        first_line=False,
    )
    page_break(doc)
    heading(doc, "S.7  Extended discussion of modular inverses")
    p(
        doc,
        "The engine finds inverses by search over 1 … m−1 rather than by an explicit extended "
        "Euclidean algorithm, although the docstring mentions EEA. For m = 26 the loop is trivial. "
        "For m = 256 the loop still has at most 255 trials and is fast enough for classroom keys. "
        "If the modulus were a large prime, a true EEA or binary gcd would be required. Documenting "
        "this gap prevents a reader from believing that mod_inverse is a production number-theory "
        "library.",
    )
    p(
        doc,
        "Units modulo 26 were listed in Chapter 3. Each unit pairs with an inverse: 1·1, 3·9, 5·21, "
        "7·15, 11·19, 17·23, 25·25, and the symmetric swaps. The inverse table tab is simply this "
        "list with gaps at even numbers and at 13. Students who memorise the list can predict the "
        "sidebar’s rejection messages without running code.",
    )
    ss(doc, "S.4", "Inverse table beside a handwritten unit list", "Optional split photo of paper notes and the About/Key Space table")
    heading(doc, "S.8  Extended discussion of determinants", 2)
    p(
        doc,
        "Floating-point determinants are dangerous near integers. A matrix with det = 9 might be "
        "computed as 8.999999, rounded incorrectly, and rejected. The engine avoids that path for "
        "2×2 and 3×3 by using integer formulae. The fallback round(float(np.linalg.det)) exists only "
        "for other sizes, which is_valid_key does not accept. Keep it that way unless a later "
        "assignment genuinely needs 4×4 Hill keys, in which case integer methods (Bareiss, exact "
        "fraction expansion, or sympy) should replace the float fallback.",
    )
    heading(doc, "S.9  Final spare figures", 2)
    p(doc, "These last boxes absorb overflow captures so that earlier chapters stay readable.", first_line=False)
    for i, (title, where) in enumerate(
        [
            ("Wide screenshot of all tabs labels", "Crop the tab strip only"),
            ("Sidebar metrics at 3×3", "Valid 3×3 det/gcd cards"),
            ("Encrypt caption showing two X pads for a 3-letter word on 2×2", "Type HI and capture padding caption before run"),
            ("Quiz streak metric after three correct answers", "Optional"),
            ("Key space spinner on first cache fill", "First load of Key Space tab"),
            ("Stop button on animation tab", "Controls row only"),
            ("Apply Recovered Key to Sidebar toast", "After attack success"),
            ("Image key LaTeX with odd determinant message", "Before upload"),
        ],
        start=5,
    ):
        ss(doc, f"S.{i}", title, where, height=2.65)


def main():
    doc = setup_document()
    cover(doc)
    certificate_and_declaration(doc)
    abstract_and_ack(doc)
    contents(doc)
    chapter1(doc)
    chapter2(doc)
    chapter3(doc)
    chapter4(doc)
    chapter5(doc)
    chapter6(doc)
    chapter7(doc)
    chapter8(doc)
    chapter9(doc)
    chapter10(doc)
    chapter11(doc)
    chapter12(doc)
    chapter13(doc)
    chapter14(doc)
    chapter15(doc)
    appendix_a(doc)
    appendix_b(doc)
    appendix_c(doc)
    extra_fill_pages(doc)
    appendix_d(doc)
    doc.core_properties.title = "Hill Cipher Cryptosystem and Interactive Laboratory — Project Report"
    doc.core_properties.author = "Danish"
    doc.core_properties.subject = "80-page educational project report with screenshot placeholders"
    doc.save(OUTPUT)
    print(f"Created {OUTPUT}")


if __name__ == "__main__":
    main()
