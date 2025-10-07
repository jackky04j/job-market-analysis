"""
dashboard.py
A single-file Streamlit dashboard that orchestrates and visualizes
the analyses in the repository "job-market-analysis".

How it works:
- Provides toggles in the sidebar to run/import each analysis script.
- Attempts to import <script>.py and call main(); if import fails, runs it with subprocess.
- Displays CSV samples, summary stats and any PNGs produced under ./graphs/.
- Looks for 'spiderman_logo.png' in repo root; if missing, uses emoji header.

Drop this file in the repo root (next to the other .py files & CSVs).
Run: streamlit run dashboard.py
"""

import streamlit as st
import subprocess
import importlib.util
import sys
import os
import glob
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import textwrap

# ---------------------------
# Configuration / helpers
# ---------------------------
REPO_ROOT = Path(__file__).parent
GRAPHS_DIR = REPO_ROOT / "graphs"
CSV_FILES = {
    "linkedin": REPO_ROOT / "linkedin_historical.csv",
    "indeed": REPO_ROOT / "indeed_webscrape.csv",
    "linkedin_no_skills": REPO_ROOT / "linkedin_no_skills.csv",
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

def run_script_as_subprocess(script_name: str):
    """Run a script as a subprocess and return (success, output)."""
    path = REPO_ROOT / f"{script_name}.py"
    if not path.exists():
        return False, f"{path} not found."
    try:
        # Use same python executable
        proc = subprocess.run([sys.executable, str(path)], capture_output=True, text=True, timeout=300)
        success = proc.returncode == 0
        out = proc.stdout + ("\nERR:\n" + proc.stderr if proc.stderr else "")
        return success, out
    except Exception as e:
        return False, str(e)

def try_import_and_run(script_name: str):
    """Try to import a module and call main() if present."""
    path = REPO_ROOT / f"{script_name}.py"
    if not path.exists():
        return False, f"{path} not found."

    spec = importlib.util.spec_from_file_location(script_name, str(path))
    try:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if hasattr(module, "main"):
            result = module.main()
            return True, f"Imported and executed {script_name}.main() (returned: {result})"
        else:
            return False, f"Imported {script_name} but no main() found."
    except Exception as e:
        return False, f"Import failed: {e}"

def list_graphs():
    """Return list of PNG/SVG/JPG in graphs dir, sorted by mtime desc."""
    if not GRAPHS_DIR.exists():
        return []
    files = sorted(GRAPHS_DIR.glob("*"), key=lambda p: p.stat().st_mtime, reverse=True)
    return [p for p in files if p.suffix.lower() in [".png", ".jpg", ".jpeg", ".svg"]]

def show_image(path: Path, caption=None):
    try:
        st.image(str(path), caption=caption, use_column_width=True)
    except Exception:
        st.write(f"Could not render image: {path}")

# ---------------------------
# Streamlit layout & styles
# ---------------------------

st.set_page_config(page_title="Job Market Analysis — Dashboard", layout="wide", initial_sidebar_state="expanded")
# A little CSS for nicer look
st.markdown(
    """
    <style>
    .stApp { font-family: 'Inter', sans-serif; }
    .big-title { font-size:34px; font-weight:700; }
    .muted { color: #6c757d; }
    .card { padding: 1rem; border-radius: 12px; box-shadow: 0 6px 18px rgba(0,0,0,0.06); background: linear-gradient(180deg, #ffffff, #fbfbff); }
    </style>
    """,
    unsafe_allow_html=True,
)

# Header: Spiderman logo if available; else emoji
logo_path = REPO_ROOT / "spiderman_logo.png"
col1, col2 = st.columns([1, 9])
with col1:
    if logo_path.exists():
        st.image(str(logo_path), width=120)
    else:
        st.markdown("<div style='font-size:48px'>🕷️</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='big-title'>Job Market Analysis</div>", unsafe_allow_html=True)
    st.markdown("<div class='muted'>Interactive dashboard — run analyses, view graphs and inspect data</div>", unsafe_allow_html=True)

st.write("---")

# Sidebar controls
st.sidebar.header("Controls")
st.sidebar.markdown("Pick analyses to run or refresh outputs. The dashboard will try to import scripts (preferred) and fallback to running them as standalone scripts if import fails.")
selected = {s: st.sidebar.checkbox(s.replace("_", " ").title(), value=False) for s in SCRIPTS}
st.sidebar.markdown("### Data preview")
for name, path in CSV_FILES.items():
    if path.exists():
        st.sidebar.write(f"- {name}: {path.name} ({path.stat().st_size//1024} KB)")
    else:
        st.sidebar.write(f"- {name}: *not found*")

if st.sidebar.button("Run selected scripts"):
    st.sidebar.info("Running... outputs will appear below.")
    run_results = {}
    for script_name, chosen in selected.items():
        if not chosen:
            continue
        st.sidebar.write(f"→ {script_name}.py")
        ok, msg = try_import_and_run(script_name)
        if not ok:
            # fallback to subprocess
            ok_sub, out = run_script_as_subprocess(script_name)
            run_results[script_name] = (ok_sub, out)
        else:
            run_results[script_name] = (True, msg)
    st.sidebar.success("Done. Scroll main area for outputs.")
    # Show run results in main area
    st.subheader("Run results")
    for name, (ok, out) in run_results.items():
        if ok:
            st.success(f"{name}: success")
            st.code(out[:1500] if isinstance(out, str) else str(out))
        else:
            st.error(f"{name}: failed")
            st.code(out[:1500] if isinstance(out, str) else str(out))

# Main panels
left, right = st.columns([2, 3])

with left:
    st.markdown("### Data Explorer")
    for label, path in CSV_FILES.items():
        if path.exists():
            df = pd.read_csv(path, nrows=10000)  # sample
            st.markdown(f"#### {label} ({path.name}) — sample")
            st.dataframe(df.head(10))
            if st.button(f"Show basic stats for {label}", key=f"stats_{label}"):
                st.write(df.describe(include="all").transpose())
            if st.button(f"Show column types for {label}", key=f"types_{label}"):
                st.write(pd.DataFrame(df.dtypes, columns=["dtype"]))
        else:
            st.markdown(f"#### {label} — *file not found*")

    st.markdown("### Quick custom query")
    expr = st.text_area("Pandas query on linkedin_historical (e.g. df[df['location'].str.contains('Bengaluru', na=False)])", height=80)
    if st.button("Run query"):
        if CSV_FILES["linkedin"].exists():
            df_full = pd.read_csv(CSV_FILES["linkedin"])
            try:
                res = df_full.query(expr) if "@" not in expr else df_full.loc[eval(expr)]
                st.dataframe(res.head(200))
            except Exception as e:
                try:
                    # fallback: use eval with df variable
                    df = df_full
                    res = eval(expr)
                    st.dataframe(res.head(200))
                except Exception as e2:
                    st.error(f"Query failed: {e} / {e2}")
        else:
            st.error("linkedin_historical.csv not found in repo root.")

with right:
    st.markdown("### Generated Graphs")
    graphs = list_graphs()
    if not graphs:
        st.info("No graphs found in ./graphs/. Try running scripts to produce plots (select them in sidebar and click 'Run selected scripts').")
    else:
        for p in graphs:
            st.markdown(f"**{p.name}** — {p.stat().st_mtime_ns}")
            show_image(p)

st.write("---")
st.markdown("### Utilities & Notes")
st.markdown(textwrap.dedent("""
- The dashboard first **attempts to import** the .py files and call `main()`. This is the safest integration path.
- If import fails (missing `main()` or dependencies), it runs the script as `python script.py`. Make sure each script can run standalone.
- Produced plots should be saved by the scripts into `./graphs/` for the dashboard to automatically display them.
- To add a Spiderman logo, drop an image named `spiderman_logo.png` into the repo root and refresh the app.
"""))

st.markdown("#### Export / Download")
if st.button("Bundle graphs into zip"):
    import shutil, tempfile
    tmp = tempfile.mkdtemp()
    zip_path = Path(tmp) / "graphs_bundle.zip"
    if GRAPHS_DIR.exists():
        shutil.make_archive(str(zip_path).replace(".zip",""), 'zip', str(GRAPHS_DIR))
        with open(zip_path, "rb") as f:
            st.download_button("Download graphs_bundle.zip", f, file_name="graphs_bundle.zip")
    else:
        st.error("No graphs folder found to zip.")

st.markdown("---")
st.caption("Dashboard generated by a helper script. If any script errors appear, paste the traceback and I'll help fix them.")
