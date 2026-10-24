import streamlit as st
import requests

# API Gateway Endpoint
API_URL = "http://localhost:8000/api/research"

st.set_page_config(page_title="PATHFINDER Agent", layout="wide")

st.title("PATHFINDER: Academic Literature to Codebase Agent")
st.markdown("Automate mapping academic research to your specific GitHub repositories.")

with st.sidebar:
    st.header("Input Parameters")
    query = st.text_area("User Prompt", placeholder="e.g., Improve retrieval latency using lightweight chunking...")
    repo_link = st.text_input("Repo Link", placeholder="https://github.com/user/repo")
    submit_btn = st.button("Run Agent")

if submit_btn:
    if not query:
        st.warning("Please enter a User Prompt.")
    else:
        with st.spinner("Agent is running..."):
            payload = {
                "query": query,
                "repo_link": repo_link
            }
            
            try:
                response = requests.post(API_URL, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    
                    st.success(f"Status: {data.get('status', 'Unknown')}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("Agent Brain Trace")
                        st.info(f"**Classified Domain:** {data.get('domain', 'N/A')}")
                        st.markdown("### Generated Plan")
                        st.write(data.get("plan", ""))
                        
                    with col2:
                        st.subheader("TinyFish Fetched Data")
                        with st.expander("View Raw Markdown"):
                            st.text(data.get("raw_markdown", ""))
                            
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
            except requests.exceptions.ConnectionError:
                st.error("Failed to connect to the FastAPI backend. Ensure main.py is running on port 8000.")