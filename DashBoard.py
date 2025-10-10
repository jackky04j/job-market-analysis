import streamlit as st
import subprocess
import importlib.util
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    mean_squared_error, r2_score
)

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
        spec = importlib.util.spec_from_file_location(script_name, str(path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if hasattr(module, "main"):
            module.main()
            return True, f"✅ Successfully imported and ran {script_name}.main()"
        else:
            raise AttributeError("No main() found")
    except Exception:
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
    st.markdown("<p style='color:gray'>Using cleaned datasets • Run scripts • Explore data • Evaluate metrics — all locally</p>", unsafe_allow_html=True)

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
tab1, tab2, tab3, tab4 = st.tabs([
    "📑 Data Explorer",
    "🖼️ Graphs",
    "📝 Script Outputs",
    "📏 Evaluation & Metrics"
])

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

# --- Tab 4: Evaluation & Metrics ---
with tab4:
    st.subheader("📏 Evaluation & Metrics")

    dataset_choice = st.selectbox("Select dataset for evaluation", list(CSV_FILES.keys()))
    data_path = CSV_FILES[dataset_choice]

    if data_path.exists():
        df_eval = pd.read_csv(data_path)
        st.write(f"Dataset shape: {df_eval.shape}")
        
        # 🧠 Basic Evaluation
        st.markdown("### 🔸 Basic Statistics")
        st.write(df_eval.describe(include='all').transpose())

        st.markdown("### 🔸 Missing Values")
        st.write(df_eval.isnull().sum())

        # 📊 Correlation Heatmap
        if not df_eval.select_dtypes(include=[np.number]).empty:
            st.markdown("### 🔸 Correlation Heatmap")
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.heatmap(df_eval.select_dtypes(include=[np.number]).corr(), annot=True, cmap="coolwarm", ax=ax)
            st.pyplot(fig)

        # 📈 Distribution Plots
        numeric_cols = df_eval.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_cols:
            st.markdown("### 🔸 Column Distribution")
            col_to_plot = st.selectbox("Select numeric column to view distribution", numeric_cols)
            fig, ax = plt.subplots(figsize=(8, 4))
            sns.histplot(df_eval[col_to_plot], kde=True, ax=ax)
            st.pyplot(fig)

        # 🧪 Metrics Demo (if applicable)
        st.markdown("### 🧮 Model Metric Demonstration")
        st.info("Demo using random y_true / y_pred — Replace with actual model results when available.")
        y_true = np.random.randint(0, 2, size=100)
        y_pred = np.random.randint(0, 2, size=100)

        st.write({
            "Accuracy": accuracy_score(y_true, y_pred),
            "Precision": precision_score(y_true, y_pred, zero_division=0),
            "Recall": recall_score(y_true, y_pred, zero_division=0),
            "F1 Score": f1_score(y_true, y_pred, zero_division=0)
        })

        # Regression metrics demo
        y_true_reg = np.random.rand(100)
        y_pred_reg = y_true_reg + np.random.normal(0, 0.1, size=100)
        st.write({
            "MSE": mean_squared_error(y_true_reg, y_pred_reg),
            "R² Score": r2_score(y_true_reg, y_pred_reg)
        })

    else:
        st.warning(f"{data_path.name} not found")

# ================================
# 🦸 FOOTER
# ================================
st.write("---")
st.caption("🕷️ Local Job Market Analysis Dashboard — Evaluation integrated • Clean datasets • Run locally")
