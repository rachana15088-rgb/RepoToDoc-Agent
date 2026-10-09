import asyncio
import os
import zipfile
import streamlit as st
from google.antigravity import Agent, LocalAgentConfig

st.set_page_config(page_title="RepoToDoc Agent", layout="wide", page_icon="⚡")

# Header Section
st.title("⚡ RepoToDoc & Code Audit Agent")
st.caption("Autonomous Codebase & Assignment Assistant | Problem Statement 2")

# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key_input = st.text_input("Enter Gemini API Key:", type="password")
    if api_key_input:
        os.environ["GEMINI_API_KEY"] = api_key_input.strip()
        os.environ["GOOGLE_API_KEY"] = api_key_input.strip()
    st.markdown("---")
    st.markdown("### 📌 Agent Workflow")
    st.markdown("1. **Architecture Inspection** (Mermaid.js)")
    st.markdown("2. **Bug Hunting & Code Fixes**")
    st.markdown("3. **README & Spec Generation**")
    st.markdown("4. **Exportable Deliverables**")

# Input Mode Tabs
tab_paste, tab_file = st.tabs(["📝 Paste Code", "📁 Upload File / Zip"])

code_to_audit = ""

with tab_paste:
    code_to_audit = st.text_area(
        "Paste Python Code or Script to Audit:",
        height=220,
        value="""def calculate_total(prices):
    total = 0
    for price in prices:
        total += pric  # Intentional NameError bug
    return total

def generate_report(data):
    result = calculate_total(data)
    print("Total result is:", result)

generate_report([10, 20, 30])"""
    )

with tab_file:
    uploaded_file = st.file_uploader("Upload a Python file (.py) or ZIP archive (.zip)", type=["py", "zip"])
    if uploaded_file is not None:
        if uploaded_file.name.endswith(".py"):
            code_to_audit = uploaded_file.read().decode("utf-8")
            st.code(code_to_audit[:300] + "..." if len(code_to_audit) > 300 else code_to_audit, language="python")
        elif uploaded_file.name.endswith(".zip"):
            with zipfile.ZipFile(uploaded_file, "r") as z:
                all_code = []
                for fname in z.namelist():
                    if fname.endswith(".py"):
                        all_code.append(f"# --- File: {fname} ---\n" + z.read(fname).decode("utf-8", errors="ignore"))
                code_to_audit = "\n\n".join(all_code)
            st.success(f"Extracted {len(z.namelist())} files from ZIP!")

# Antigravity Agent Core Execution
async def run_repotodoc_agent(code: str):
    config = LocalAgentConfig(
        system_instructions=(
            "You are RepoToDoc: an autonomous codebase auditing agent. "
            "Perform an end-to-end analysis on the provided code and structure your output into exact markdown sections:\n\n"
            "## 1. Code Quality Score & Assessment\n"
            "Provide a score out of 100 with detailed breakdown of bugs, structure, and readability.\n\n"
            "## 2. Bug Analysis & Corrected Code\n"
            "Identify all bugs/anti-patterns, explain root causes, and provide fixed executable code inside a ```python ``` block.\n\n"
            "## 3. System Architecture Diagram\n"
            "Provide a visual flowchart of execution/data flow inside a ```mermaid ``` block.\n\n"
            "## 4. Executive README.md\n"
            "Generate a production-ready README file complete with setup steps, usage guide, and API documentation."
        )
    )
    prompt = f"Audit and document this Python project codebase:\n```python\n{code}\n```"
    async with Agent(config) as agent:
        response = await agent.chat(prompt)
        full_text = await response.text()
        return full_text

# Run Action
if st.button("🚀 Audit Project & Generate RepoToDoc Report", type="primary"):
    if not api_key_input and not os.environ.get("GEMINI_API_KEY"):
        st.error("Please enter your Gemini API Key in the sidebar first!")
    elif not code_to_audit.strip():
        st.error("Please provide code input or upload a file first!")
    else:
        with st.spinner("RepoToDoc Agent inspecting codebase, executing tests, fixing bugs, and drafting docs..."):
            try:
                report = asyncio.run(run_repotodoc_agent(code_to_audit))
                st.success("Audit Completed Successfully!")
                st.markdown("---")
                
                # Render Report
                st.markdown(report)
                
                # Download Button
                st.download_button(
                    label="📥 Export Complete README.md",
                    data=report,
                    file_name="README.md",
                    mime="text/markdown"
                )
            except Exception as e:
                st.error(f"Error executing RepoToDoc Agent: {e}")