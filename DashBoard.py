import streamlit as st
import subprocess
import importlib.util
import sys
from pathlib import Path
import pandas as pd

# ================================
# 📌 CONFIGURATION
# ================================
REPO_ROOT = Path(__file__).parent
GRAPHS_DIR = REPO_ROOT / "graphs"

# ✅ Use the CLEANED CSV files here
CSV_FILES = {
    "Clean LinkedIn Historical": REPO_ROOT / "clean_linkedin_historical.csv",
    "Clean Indeed Webscrape": REPO_ROOT / "clean_indeed_webscrape.csv",
    "Clean LinkedIn No Skills": REPO_ROOT / "clean_linkedin_no_skills.csv",
}

SCRIPTS = [
    "clean_linkedin",
    "clean_skills_plot",
    "most_common_job_titles",
    "skill_demand_evolution",
    "top_hiring_companies",
    "top_hiring_locations",
    "hiring_trends_overtime",
    "forecast_job_postings",
]

# ================================
# 📌 HELPER FUNCTIONS
# ================================
def run_script(script_name: str):
    """Try importing module and calling main(); fallback to subprocess."""
    path = REPO_ROOT / f"{script_name}.py"
    if not path.exists():
        return False, f"❌ Script not found: {path.name}"

    try:
        # Try importing and running main()
        spec = importlib.util.spec_from_file_location(script_name, str(path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if hasattr(module, "main"):
            module.main()
            return True, f"✅ Successfully imported and ran {script_name}.main()"
        else:
            raise AttributeError("No main() found")
    except Exception:
        # Fallback: run as subprocess
        try:
            result = subprocess.run([sys.executable, str(path)], capture_output=True, text=True)
            if result.returncode == 0:
                return True, f"✅ Ran {script_name}.py as subprocess\n{result.stdout}"
            else:
                return False, f"❌ Subprocess error:\n{result.stderr}"
        except Exception as e2:
            return False, f"❌ Failed to run {script_name}.py\n{e2}"

def list_graph_files():
    """Return list of image files in ./graphs sorted by last modified."""
    if not GRAPHS_DIR.exists():
        return []
    exts = (".png", ".jpg", ".jpeg", ".svg")
    files = [f for f in GRAPHS_DIR.glob("*") if f.suffix.lower() in exts]
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)

# ================================
# 🌟 STREAMLIT UI
# ================================
st.set_page_config(
    page_title="🕷️ Job Market Analysis Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- HEADER ---
col1, col2 = st.columns([1, 9])
logo_path = REPO_ROOT / "spiderman_logo.png"

with col1:
    if logo_path.exists():
        st.image(str(logo_path), width=110)
    else:
        st.markdown("<div style='font-size:50px'>🕷️</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<h1 style='margin-bottom:0'>Job Market Analysis Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:gray'>Using cleaned datasets • Run scripts • Explore data • View generated graphs — all locally</p>", unsafe_allow_html=True)

st.write("---")

# --- SIDEBAR ---
st.sidebar.header("⚡ Run Scripts")
selected_scripts = st.sidebar.multiselect(
    "Select analysis scripts to run",
    options=SCRIPTS
)

if st.sidebar.button("▶ Run Selected"):
    st.sidebar.info("Running scripts...")
    for s in selected_scripts:
        ok, msg = run_script(s)
        if ok:
            st.sidebar.success(msg)
        else:
            st.sidebar.error(msg)

st.sidebar.markdown("---")
st.sidebar.header("📊 CSV Files (Cleaned)")

for name, path in CSV_FILES.items():
    if path.exists():
        size_kb = path.stat().st_size // 1024
        st.sidebar.write(f"✅ {name} ({size_kb} KB)")
    else:
        st.sidebar.write(f"❌ {name} not found")

# ================================
# 📈 MAIN CONTENT
# ================================
tab1, tab2, tab3 = st.tabs(["📑 Data Explorer", "🖼️ Graphs", "📝 Script Outputs"])

# --- Tab 1: Data Explorer ---
with tab1:
    st.subheader("📂 Explore Cleaned CSV Data")
    for label, path in CSV_FILES.items():
        st.markdown(f"### {label}")
        if path.exists():
            df = pd.read_csv(path)
            st.dataframe(df.head(10))
            with st.expander("Show basic info"):
                st.write(df.describe(include='all').transpose())
        else:
            st.warning(f"{path.name} not found")

# --- Tab 2: Graph Viewer ---
with tab2:
    st.subheader("🖼️ Generated Graphs")
    graph_files = list_graph_files()
    if not graph_files:
        st.info("No graphs found in ./graphs/. Run analysis scripts to generate plots.")
    else:
        for img_path in graph_files:
            st.image(str(img_path), caption=img_path.name, use_column_width=True)

# --- Tab 3: Script Outputs / Log ---
with tab3:
    st.subheader("📜 Log & Run Feedback")
    st.write("Script run results appear in the sidebar when you execute them.")

# ================================
# 🦸 FOOTER
# ================================
st.write("---")
st.caption("🕷️ Local Job Market Analysis Dashboard — using cleaned datasets. Drop your 'spiderman_logo.png' in the repo folder for custom branding.")
