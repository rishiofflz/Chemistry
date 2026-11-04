import io
import json
import urllib.parse
import urllib.request
from datetime import datetime

import pandas as pd
import streamlit as st

# ============================================================
# CHEMVERSE MOLECULAR LAB
# Student: RISHI KANNA S | Register No: RA2611026050149
# SRM Institute of Science and Technology
# ============================================================

st.set_page_config(
    page_title="CHEMVERSE | Molecular Lab",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Optional packages: the app still opens if these are unavailable.
try:
    from rdkit import Chem
    from rdkit.Chem import AllChem, Descriptors, Lipinski, rdMolDescriptors
    from rdkit.Chem import Draw
    RDKIT_AVAILABLE = True
except Exception:
    RDKIT_AVAILABLE = False

try:
    import py3Dmol
    PY3DMOL_AVAILABLE = True
except Exception:
    PY3DMOL_AVAILABLE = False

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False


# --------------------------- DESIGN ---------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');

:root {
    --bg: #070b18;
    --panel: rgba(16, 25, 48, .82);
    --cyan: #46f3e5;
    --blue: #6d8cff;
    --purple: #bd72ff;
    --text: #eaf1ff;
    --muted: #9baac7;
}
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* CHEMVERSE neon ambience */
.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 0;
    opacity: .34;
    background-image:
      linear-gradient(rgba(83, 220, 255, .035) 1px, transparent 1px),
      linear-gradient(90deg, rgba(83, 220, 255, .035) 1px, transparent 1px);
    background-size: 42px 42px;
    mask-image: linear-gradient(to bottom, black, transparent 88%);
}
[data-testid="stAppViewContainer"] > .main {
    position: relative;
    z-index: 1;
}
[data-testid="stSidebar"] {
    box-shadow: 8px 0 35px rgba(51, 220, 255, .06);
}
.hero {
    position: relative;
    overflow: hidden;
    background:
      radial-gradient(circle at 82% 18%, rgba(189,114,255,.22), transparent 28%),
      radial-gradient(circle at 8% 90%, rgba(70,243,229,.17), transparent 32%),
      linear-gradient(120deg, rgba(9, 31, 55, .97), rgba(31, 18, 61, .95));
    box-shadow: 0 0 34px rgba(70,243,229,.12),
                0 0 70px rgba(189,114,255,.08),
                inset 0 0 35px rgba(105,93,255,.10);
}
.metric-card, .glass-card {
    backdrop-filter: blur(12px);
}

.stApp {
    background:
      radial-gradient(ellipse at 12% 8%, rgba(28, 183, 208, .17), transparent 32%),
      radial-gradient(ellipse at 88% 12%, rgba(140, 75, 255, .18), transparent 30%),
      radial-gradient(ellipse at 50% 100%, rgba(34, 91, 180, .15), transparent 38%),
      var(--bg);
    color: var(--text);
}
[data-testid="stHeader"] { background: rgba(0,0,0,0); }
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0c1429 0%, #10112a 100%);
    border-right: 1px solid rgba(89, 221, 238, .18);
}
h1, h2, h3 {
    font-family: 'Space Grotesk', sans-serif !important;
    color: #f4f7ff !important;
}
p, label, li { color: #d5def2; }
.hero {
    padding: 30px 32px;
    border-radius: 24px;
    background: linear-gradient(120deg, rgba(16, 39, 67, .94), rgba(39, 20, 69, .88));
    border: 1px solid rgba(75, 236, 225, .32);
    box-shadow: 0 0 35px rgba(40, 221, 222, .10), inset 0 0 35px rgba(105, 93, 255, .08);
    margin-bottom: 22px;
}
.eyebrow {
    color: var(--cyan);
    font-family: 'DM Mono', monospace;
    letter-spacing: 2px;
    font-size: 12px;
    text-transform: uppercase;
}
.hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(32px, 5vw, 56px);
    line-height: 1.05;
    font-weight: 700;
    margin: 10px 0;
    background: linear-gradient(90deg, #ffffff, #73f5e8, #bd91ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-sub { color: #b8c8e6; font-size: 16px; max-width: 760px; }
.glass-card {
    background: var(--panel);
    border: 1px solid rgba(123, 170, 255, .19);
    border-radius: 18px;
    padding: 20px;
    box-shadow: 0 8px 28px rgba(0,0,0,.16);
}
.metric-card {
    background: linear-gradient(145deg, rgba(18, 38, 66, .95), rgba(30, 24, 57, .92));
    border: 1px solid rgba(70,243,229,.25);
    border-radius: 16px;
    padding: 18px;
}
.metric-label { color: #9fb2d5; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; }
.metric-value { color: #f2fbff; font-family: 'Space Grotesk'; font-size: 27px; font-weight: 700; }
.small-muted { color: #9baac7; font-size: 13px; }
div.stButton > button {
    border: 1px solid rgba(70,243,229,.45);
    border-radius: 11px;
    background: linear-gradient(90deg, rgba(28,145,158,.35), rgba(107,75,174,.35));
    color: #f4ffff;
    font-weight: 700;
}
div.stButton > button:hover {
    border-color: #46f3e5;
    box-shadow: 0 0 18px rgba(70,243,229,.22);
    color: white;
}
.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
    background: rgba(8, 17, 35, .9) !important;
    color: #f1f6ff !important;
}
hr { border-color: rgba(122, 158, 220, .18); }
code { color: #73f5e8 !important; }
footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# --------------------------- DATA ---------------------------

ELEMENTS = [
    (1,"H","Hydrogen","Nonmetal"),(2,"He","Helium","Noble gas"),
    (3,"Li","Lithium","Alkali metal"),(4,"Be","Beryllium","Alkaline earth"),
    (5,"B","Boron","Metalloid"),(6,"C","Carbon","Nonmetal"),
    (7,"N","Nitrogen","Nonmetal"),(8,"O","Oxygen","Nonmetal"),
    (9,"F","Fluorine","Halogen"),(10,"Ne","Neon","Noble gas"),
    (11,"Na","Sodium","Alkali metal"),(12,"Mg","Magnesium","Alkaline earth"),
    (13,"Al","Aluminium","Post-transition"),(14,"Si","Silicon","Metalloid"),
    (15,"P","Phosphorus","Nonmetal"),(16,"S","Sulfur","Nonmetal"),
    (17,"Cl","Chlorine","Halogen"),(18,"Ar","Argon","Noble gas"),
    (19,"K","Potassium","Alkali metal"),(20,"Ca","Calcium","Alkaline earth"),
    (21,"Sc","Scandium","Transition metal"),(22,"Ti","Titanium","Transition metal"),
    (23,"V","Vanadium","Transition metal"),(24,"Cr","Chromium","Transition metal"),
    (25,"Mn","Manganese","Transition metal"),(26,"Fe","Iron","Transition metal"),
    (27,"Co","Cobalt","Transition metal"),(28,"Ni","Nickel","Transition metal"),
    (29,"Cu","Copper","Transition metal"),(30,"Zn","Zinc","Transition metal"),
    (31,"Ga","Gallium","Post-transition"),(32,"Ge","Germanium","Metalloid"),
    (33,"As","Arsenic","Metalloid"),(34,"Se","Selenium","Nonmetal"),
    (35,"Br","Bromine","Halogen"),(36,"Kr","Krypton","Noble gas"),
    (37,"Rb","Rubidium","Alkali metal"),(38,"Sr","Strontium","Alkaline earth"),
    (39,"Y","Yttrium","Transition metal"),(40,"Zr","Zirconium","Transition metal"),
    (41,"Nb","Niobium","Transition metal"),(42,"Mo","Molybdenum","Transition metal"),
    (43,"Tc","Technetium","Transition metal"),(44,"Ru","Ruthenium","Transition metal"),
    (45,"Rh","Rhodium","Transition metal"),(46,"Pd","Palladium","Transition metal"),
    (47,"Ag","Silver","Transition metal"),(48,"Cd","Cadmium","Transition metal"),
    (49,"In","Indium","Post-transition"),(50,"Sn","Tin","Post-transition"),
    (51,"Sb","Antimony","Metalloid"),(52,"Te","Tellurium","Metalloid"),
    (53,"I","Iodine","Halogen"),(54,"Xe","Xenon","Noble gas"),
    (55,"Cs","Caesium","Alkali metal"),(56,"Ba","Barium","Alkaline earth"),
    (57,"La","Lanthanum","Lanthanide"),(58,"Ce","Cerium","Lanthanide"),
    (59,"Pr","Praseodymium","Lanthanide"),(60,"Nd","Neodymium","Lanthanide"),
    (61,"Pm","Promethium","Lanthanide"),(62,"Sm","Samarium","Lanthanide"),
    (63,"Eu","Europium","Lanthanide"),(64,"Gd","Gadolinium","Lanthanide"),
    (65,"Tb","Terbium","Lanthanide"),(66,"Dy","Dysprosium","Lanthanide"),
    (67,"Ho","Holmium","Lanthanide"),(68,"Er","Erbium","Lanthanide"),
    (69,"Tm","Thulium","Lanthanide"),(70,"Yb","Ytterbium","Lanthanide"),
    (71,"Lu","Lutetium","Lanthanide"),(72,"Hf","Hafnium","Transition metal"),
    (73,"Ta","Tantalum","Transition metal"),(74,"W","Tungsten","Transition metal"),
    (75,"Re","Rhenium","Transition metal"),(76,"Os","Osmium","Transition metal"),
    (77,"Ir","Iridium","Transition metal"),(78,"Pt","Platinum","Transition metal"),
    (79,"Au","Gold","Transition metal"),(80,"Hg","Mercury","Transition metal"),
    (81,"Tl","Thallium","Post-transition"),(82,"Pb","Lead","Post-transition"),
    (83,"Bi","Bismuth","Post-transition"),(84,"Po","Polonium","Post-transition"),
    (85,"At","Astatine","Halogen"),(86,"Rn","Radon","Noble gas"),
    (87,"Fr","Francium","Alkali metal"),(88,"Ra","Radium","Alkaline earth"),
    (89,"Ac","Actinium","Actinide"),(90,"Th","Thorium","Actinide"),
    (91,"Pa","Protactinium","Actinide"),(92,"U","Uranium","Actinide"),
    (93,"Np","Neptunium","Actinide"),(94,"Pu","Plutonium","Actinide"),
    (95,"Am","Americium","Actinide"),(96,"Cm","Curium","Actinide"),
    (97,"Bk","Berkelium","Actinide"),(98,"Cf","Californium","Actinide"),
    (99,"Es","Einsteinium","Actinide"),(100,"Fm","Fermium","Actinide"),
    (101,"Md","Mendelevium","Actinide"),(102,"No","Nobelium","Actinide"),
    (103,"Lr","Lawrencium","Actinide"),(104,"Rf","Rutherfordium","Transition metal"),
    (105,"Db","Dubnium","Transition metal"),(106,"Sg","Seaborgium","Transition metal"),
    (107,"Bh","Bohrium","Transition metal"),(108,"Hs","Hassium","Transition metal"),
    (109,"Mt","Meitnerium","Transition metal"),(110,"Ds","Darmstadtium","Transition metal"),
    (111,"Rg","Roentgenium","Transition metal"),(112,"Cn","Copernicium","Transition metal"),
    (113,"Nh","Nihonium","Post-transition"),(114,"Fl","Flerovium","Post-transition"),
    (115,"Mc","Moscovium","Post-transition"),(116,"Lv","Livermorium","Post-transition"),
    (117,"Ts","Tennessine","Halogen"),(118,"Og","Oganesson","Noble gas")
]

SAMPLES = {
    "Water": "O",
    "Ethanol": "CCO",
    "Caffeine": "Cn1cnc2c1c(=O)n(C)c(=O)n2C",
    "Aspirin": "CC(=O)OC1=CC=CC=C1C(=O)O",
    "Glucose": "C(C1C(C(C(C(O1)O)O)O)O)O",
    "Benzene": "c1ccccc1",
    "Acetic acid": "CC(=O)O",
    "Lactic acid": "CC(O)C(=O)O",
}

# --------------------------- HELPERS ---------------------------

def get_molecule(smiles):
    if not RDKIT_AVAILABLE:
        return None, "RDKit is not installed. Install it using the requirements file."
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None, "Invalid SMILES notation. Please check the structure."
    return mol, None


def molecule_properties(mol):
    return {
        "Molecular formula": rdMolDescriptors.CalcMolFormula(mol),
        "Molecular weight (g/mol)": round(Descriptors.MolWt(mol), 3),
        "Exact mass": round(Descriptors.ExactMolWt(mol), 4),
        "LogP": round(Descriptors.MolLogP(mol), 3),
        "TPSA (Å²)": round(Descriptors.TPSA(mol), 3),
        "H-bond donors": Lipinski.NumHDonors(mol),
        "H-bond acceptors": Lipinski.NumHAcceptors(mol),
        "Rotatable bonds": Lipinski.NumRotatableBonds(mol),
        "Ring count": rdMolDescriptors.CalcNumRings(mol),
        "Heavy atoms": mol.GetNumHeavyAtoms(),
        "Total atoms": mol.GetNumAtoms(),
    }


def draw_2d(mol):
    image = Draw.MolToImage(mol, size=(650, 420))
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def make_3d_html(smiles, style="stick"):
    if not RDKIT_AVAILABLE:
        return None, "RDKit is required for 3D structure generation."
    if not PY3DMOL_AVAILABLE:
        return None, "py3Dmol is not installed. Add py3Dmol to requirements.txt."
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None, "Invalid SMILES."
    mol = Chem.AddHs(mol)
    status = AllChem.EmbedMolecule(mol, randomSeed=42)
    if status != 0:
        return None, "Could not generate a 3D conformer for this molecule."
    try:
        AllChem.MMFFOptimizeMolecule(mol, maxIters=250)
    except Exception:
        try:
            AllChem.UFFOptimizeMolecule(mol, maxIters=250)
        except Exception:
            pass
    block = Chem.MolToMolBlock(mol)
    viewer = py3Dmol.view(width=900, height=520)
    viewer.addModel(block, "mol")
    if style == "ball & stick":
        viewer.setStyle({"stick": {"radius": 0.16}, "sphere": {"scale": 0.25}})
    elif style == "space filling":
        viewer.setStyle({"sphere": {"scale": 0.8}})
    elif style == "wireframe":
        viewer.setStyle({"line": {"linewidth": 2}})
    else:
        viewer.setStyle({"stick": {"radius": 0.22}})
    viewer.setBackgroundColor("#071326")
    viewer.zoomTo()
    return viewer._make_html(), None


def pubchem_search(compound):
    encoded = urllib.parse.quote(compound.strip())
    url = (
        "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/"
        f"{encoded}/property/MolecularFormula,MolecularWeight,CanonicalSMILES,IsomericSMILES/JSON"
    )
    request = urllib.request.Request(url, headers={"User-Agent": "CHEMVERSE-Virtual-Lab/1.0"})
    with urllib.request.urlopen(request, timeout=15) as response:
        data = json.loads(response.read().decode("utf-8"))
    props = data["PropertyTable"]["Properties"][0]
    return props


def make_pdf(compound, props, smiles):
    if not REPORTLAB_AVAILABLE:
        return None
    output = io.BytesIO()
    doc = SimpleDocTemplate(output, pagesize=A4, rightMargin=42, leftMargin=42)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ChemverseTitle", parent=styles["Title"], textColor=colors.HexColor("#163b61"),
        fontSize=21, leading=26, spaceAfter=12
    )
    story = [
        Paragraph("CHEMVERSE MOLECULAR LAB", title_style),
        Paragraph("Molecular Analysis Report", styles["Heading2"]),
        Spacer(1, 8),
        Paragraph(f"<b>Student:</b> RISHI KANNA S", styles["BodyText"]),
        Paragraph("<b>Register Number:</b> RA2611026050149", styles["BodyText"]),
        Paragraph("<b>Institution:</b> SRM Institute of Science and Technology", styles["BodyText"]),
        Paragraph(f"<b>Compound:</b> {compound}", styles["BodyText"]),
        Paragraph(f"<b>SMILES:</b> {smiles}", styles["BodyText"]),
        Spacer(1, 14),
        Paragraph("Molecular Properties", styles["Heading2"]),
    ]
    table_data = [["Property", "Value"]] + [[str(k), str(v)] for k, v in props.items()]
    table = Table(table_data, colWidths=[245, 245])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#173d62")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#b7c6d8")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#eef5fb")]),
        ("PADDING", (0, 0), (-1, -1), 7),
    ]))
    story.extend([table, Spacer(1, 16)])
    story.append(Paragraph(
        f"Generated by CHEMVERSE Virtual Lab on {datetime.now().strftime('%d-%m-%Y %H:%M')}. "
        "For educational use only.", styles["Italic"]
    ))
    doc.build(story)
    return output.getvalue()


def metric(label, value):
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div></div>',
        unsafe_allow_html=True
    )


# --------------------------- SIDEBAR ---------------------------

with st.sidebar:
    st.markdown("## 🧬 CHEMVERSE")
    st.caption("VIRTUAL CHEMISTRY LAB")
    st.markdown("---")
    page = st.radio(
        "NAVIGATION",
        [
            "Home",
            "3D Molecular Lab",
            "Molecular Properties",
            "Periodic Table",
            "PubChem Explorer",
            "Structure Comparison",
            "Theory & Learning",
            "Assessment",
            "Student Project",
        ],
    )
    st.markdown("---")
    st.markdown("**STUDENT PROFILE**")
    st.write("RISHI KANNA S")
    st.caption("RA2611026050149")
    st.caption("SRM INSTITUTE OF SCIENCE AND TECHNOLOGY")
    st.markdown("---")
    st.caption("NEON MOLECULAR EXPERIENCE · 2026")


# --------------------------- HOME ---------------------------

if page == "Home":
    st.markdown("""
    <div class="hero">
      <div class="eyebrow">INTERACTIVE CHEMISTRY · 3D MOLECULAR EXPLORATION</div>
      <div class="hero-title">CHEMVERSE<br>MOLECULAR LAB</div>
      <div class="hero-sub">
        Explore molecular structures in 3D, calculate chemical descriptors,
        and discover chemistry inside a neon-powered digital laboratory.
      </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1: metric("Elements", "118")
    with c2: metric("Molecular tools", "06+")
    with c3: metric("3D exploration", "LIVE")
    with c4: metric("Learning mode", "ACTIVE")

    st.markdown("### Explore the laboratory")
    cards = st.columns(3)
    items = [
        ("🧊", "3D Molecular Lab", "Rotate and inspect molecular structures in 3D."),
        ("⚛️", "Molecular Properties", "Calculate formula, molecular weight, LogP and more."),
        ("🧪", "Periodic Table", "Explore all 118 chemical elements."),
        ("🌐", "PubChem Explorer", "Retrieve compound information from PubChem."),
        ("📊", "Structure Comparison", "Compare molecular descriptors across compounds."),
        ("🎓", "Theory & Assessment", "Revise chemistry concepts and test your knowledge."),
    ]
    for i, (icon, title, desc) in enumerate(items):
        with cards[i % 3]:
            st.markdown(
                f'<div class="glass-card"><div style="font-size:30px">{icon}</div>'
                f'<h3>{title}</h3><p class="small-muted">{desc}</p></div>',
                unsafe_allow_html=True
            )
        if i % 3 == 2:
            cards = st.columns(3)

    st.markdown("### Quick start")
    st.info("Choose **3D Molecular Lab** or **Molecular Properties** from the sidebar and enter a compound name or SMILES notation.")
    st.markdown("### Sample molecules")
    st.write(" · ".join(SAMPLES.keys()))


# --------------------------- 3D MOLECULAR LAB ---------------------------

elif page == "3D Molecular Lab":
    st.title("🧊 3D Molecular Lab")
    st.caption("Generate and explore interactive molecular structures.")
    left, right = st.columns([1, 1.6])
    with left:
        compound_choice = st.selectbox("Choose a sample molecule", ["Custom"] + list(SAMPLES.keys()))
        default_smiles = "" if compound_choice == "Custom" else SAMPLES[compound_choice]
        smiles = st.text_input("SMILES notation", value=default_smiles, placeholder="Example: CCO")
        visual_style = st.selectbox("Visualization style", ["stick", "ball & stick", "space filling", "wireframe"])
        generate = st.button("Generate 3D Structure", use_container_width=True)
        st.markdown('<div class="small-muted">Tip: SMILES is a text notation used to represent molecular structures.</div>', unsafe_allow_html=True)
    with right:
        if generate:
            if not smiles.strip():
                st.warning("Enter a SMILES notation first.")
            else:
                html, error = make_3d_html(smiles.strip(), visual_style)
                if error:
                    st.error(error)
                else:
                    import streamlit.components.v1 as components
                    components.html(html, height=545, scrolling=False)
                    st.success("3D molecular structure generated.")
        else:
            st.markdown('<div class="glass-card"><h3>Interactive molecular viewer</h3><p class="small-muted">Select a molecule and press Generate 3D Structure to display the model here.</p><p style="font-size:54px;text-align:center">⚛️</p></div>', unsafe_allow_html=True)
    if not RDKIT_AVAILABLE:
        st.warning("RDKit is not available. Install the dependencies from requirements.txt.")


# --------------------------- MOLECULAR PROPERTIES ---------------------------

elif page == "Molecular Properties":
    st.title("⚛️ Molecular Properties")
    st.caption("Calculate chemical descriptors using RDKit.")
    choice = st.selectbox("Select sample", ["Custom"] + list(SAMPLES.keys()))
    smiles = st.text_input(
        "Enter SMILES",
        value="" if choice == "Custom" else SAMPLES[choice],
        placeholder="Example: CC(=O)O"
    )
    if st.button("Analyze Molecule", type="primary"):
        mol, error = get_molecule(smiles.strip())
        if error:
            st.error(error)
        else:
            props = molecule_properties(mol)
            a, b, c = st.columns(3)
            with a: metric("Molecular formula", props["Molecular formula"])
            with b: metric("Molecular weight", f'{props["Molecular weight (g/mol)"]} g/mol')
            with c: metric("LogP", props["LogP"])
            st.markdown("### 2D molecular structure")
            st.image(draw_2d(mol), use_container_width=True)
            st.markdown("### Descriptor table")
            st.dataframe(pd.DataFrame(list(props.items()), columns=["Property", "Value"]), use_container_width=True, hide_index=True)
            st.session_state["last_analysis"] = {
                "compound": choice if choice != "Custom" else "Custom molecule",
                "smiles": smiles.strip(),
                "props": props,
            }
            if REPORTLAB_AVAILABLE:
                pdf = make_pdf(choice if choice != "Custom" else "Custom molecule", props, smiles.strip())
                st.download_button(
                    "⬇️ Download PDF Report",
                    data=pdf,
                    file_name="CHEMVERSE_Molecular_Report.pdf",
                    mime="application/pdf",
                )
            else:
                st.info("Install reportlab to enable PDF report downloads.")


# --------------------------- PERIODIC TABLE ---------------------------

elif page == "Periodic Table":
    st.title("🧪 Interactive Periodic Table")
    st.caption("Search and inspect the 118 known chemical elements.")
    df = pd.DataFrame(ELEMENTS, columns=["Atomic Number", "Symbol", "Element", "Category"])
    query = st.text_input("Search by element name, symbol, or atomic number")
    category = st.selectbox("Filter by category", ["All"] + sorted(df["Category"].unique().tolist()))
    filtered = df.copy()
    if query.strip():
        q = query.strip().lower()
        filtered = filtered[
            filtered.apply(lambda row: q in str(row["Element"]).lower()
                           or q == str(row["Symbol"]).lower()
                           or q == str(row["Atomic Number"]), axis=1)
        ]
    if category != "All":
        filtered = filtered[filtered["Category"] == category]
    st.dataframe(filtered, use_container_width=True, hide_index=True, height=450)
    st.markdown("### Element details")
    selected = st.selectbox("Choose an element", df["Element"].tolist())
    row = df[df["Element"] == selected].iloc[0]
    x, y, z = st.columns(3)
    with x: metric("Atomic number", int(row["Atomic Number"]))
    with y: metric("Symbol", row["Symbol"])
    with z: metric("Category", row["Category"])


# --------------------------- PUBCHEM EXPLORER ---------------------------

elif page == "PubChem Explorer":
    st.title("🌐 PubChem Explorer")
    st.caption("Look up compound properties using the PubChem database.")
    compound = st.text_input("Compound name", placeholder="Example: caffeine")
    if st.button("Search PubChem", type="primary"):
        if not compound.strip():
            st.warning("Enter a compound name.")
        else:
            try:
                result = pubchem_search(compound)
                st.success("Compound found.")
                st.json(result)
                st.session_state["pubchem_result"] = result
            except Exception as exc:
                st.error(f"Could not retrieve this compound. Check the name or try again. Details: {exc}")
    st.markdown("**Examples:** caffeine · aspirin · glucose · ethanol · benzene")


# --------------------------- STRUCTURE COMPARISON ---------------------------

elif page == "Structure Comparison":
    st.title("📊 Structure–Property Comparison")
    st.caption("Compare calculated properties of two molecules.")
    if not RDKIT_AVAILABLE:
        st.warning("RDKit is required for descriptor comparison.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            name1 = st.selectbox("Molecule A", list(SAMPLES.keys()), index=1)
            smi1 = SAMPLES[name1]
        with col2:
            name2 = st.selectbox("Molecule B", list(SAMPLES.keys()), index=2)
            smi2 = SAMPLES[name2]
        m1, e1 = get_molecule(smi1)
        m2, e2 = get_molecule(smi2)
        if not e1 and not e2:
            p1 = molecule_properties(m1)
            p2 = molecule_properties(m2)
            compare_keys = ["Molecular weight (g/mol)", "LogP", "TPSA (Å²)", "H-bond donors", "H-bond acceptors", "Rotatable bonds", "Ring count"]
            comparison = pd.DataFrame({
                "Descriptor": compare_keys,
                name1: [p1[k] for k in compare_keys],
                name2: [p2[k] for k in compare_keys],
            })
            st.dataframe(comparison, use_container_width=True, hide_index=True)
            chart = comparison.set_index("Descriptor")
            st.bar_chart(chart)
            st.markdown("### 2D structures")
            a, b = st.columns(2)
            with a:
                st.subheader(name1)
                st.image(draw_2d(m1), use_container_width=True)
            with b:
                st.subheader(name2)
                st.image(draw_2d(m2), use_container_width=True)


# --------------------------- THEORY ---------------------------

elif page == "Theory & Learning":
    st.title("🎓 Theory & Learning")
    st.caption("Quick revision notes for introductory chemistry.")
    topics = {
        "Atomic structure": "An atom consists of a central nucleus containing protons and neutrons, with electrons occupying regions around the nucleus.",
        "Chemical bonding": "Chemical bonds are attractive forces that hold atoms together. Major types include ionic, covalent, and metallic bonding.",
        "Mole concept": "One mole contains approximately 6.022 × 10²³ specified entities. It connects microscopic particle counts with measurable amounts.",
        "pH scale": "pH is a measure related to hydrogen-ion activity. At ordinary classroom level, pH below 7 is acidic, 7 is neutral, and above 7 is basic.",
        "Organic chemistry": "Organic chemistry studies carbon-containing compounds, including their structures, properties, reactions, and synthesis.",
        "Molecular geometry": "Molecular geometry describes the three-dimensional arrangement of atoms in a molecule and influences its properties."
    }
    for topic, explanation in topics.items():
        with st.expander(topic):
            st.write(explanation)


# --------------------------- ASSESSMENT ---------------------------

elif page == "Assessment":
    st.title("📝 Chemistry Assessment")
    st.caption("Test your understanding with this short practice quiz.")
    questions = [
        ("What is the chemical formula of water?", ["CO₂", "H₂O", "O₂", "NaCl"], 1),
        ("What is the approximate value of Avogadro's constant?", ["6.022 × 10²³", "3.14", "9.81", "1.602 × 10⁻¹⁹"], 0),
        ("Which particle has a negative charge?", ["Proton", "Neutron", "Electron", "Nucleus"], 2),
        ("A solution with pH 3 is generally:", ["Acidic", "Neutral", "Basic", "A metal"], 0),
        ("Which is the symbol for sodium?", ["S", "So", "Na", "N"], 2),
    ]
    with st.form("quiz_form"):
        answers = []
        for i, (question, options, correct) in enumerate(questions):
            answers.append(st.radio(f"{i+1}. {question}", options, key=f"quiz_{i}"))
        submitted = st.form_submit_button("Submit answers")
    if submitted:
        score = sum(1 for answer, item in zip(answers, questions) if answer == item[1][item[2]])
        st.success(f"You scored {score} out of {len(questions)}.")
        if score == len(questions):
            st.balloons()
        else:
            st.info("Review the Theory & Learning section and try again.")


# --------------------------- STUDENT PROJECT ---------------------------

elif page == "Student Project":
    st.title("📁 Student Project Profile")
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### CHEMVERSE MOLECULAR LAB")
    st.write("**Student Name:** RISHI KANNA S")
    st.write("**Register Number:** RA2611026050149")
    st.write("**Institution:** SRM Institute of Science and Technology")
    st.write("**Project Domain:** Chemistry · Molecular Visualization · Computational Chemistry")
    st.write("**Technology Stack:** Python, Streamlit, RDKit, py3Dmol, PubChem REST API, Pandas")
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("### Project objectives")
    st.markdown("""
    - Explore molecular structures through 2D and 3D visualization.
    - Calculate selected molecular descriptors.
    - Search compound information using PubChem.
    - Explore the periodic table and basic chemistry concepts.
    - Support chemistry learning through an interactive quiz.
    """)
    st.markdown("### Learning outcome")
    st.write("The project demonstrates how Python-based tools can support interactive chemistry education and introductory molecular analysis.")


# --------------------------- FOOTER ---------------------------

st.markdown("---")
st.markdown(
    '<div style="text-align:center;color:#8293b5;font-size:12px">'
    'CHEMVERSE MOLECULAR LAB · RISHI KANNA S · SRM INSTITUTE OF SCIENCE AND TECHNOLOGY<br>'
    'Educational project interface · 2026'
    '</div>',
    unsafe_allow_html=True
)
