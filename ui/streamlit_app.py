import streamlit as st
import requests
import os
import pandas as pd
import json

# Setup page configuration
st.set_page_config(
    page_title="AI Support Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

# Custom CSS for a professional look
st.markdown("""
    <style>
    /* General Typography & Spacing */
    .stMarkdown, .stText { font-size: 1.05rem; }
    h1 { font-size: 2.2rem !important; font-weight: 600 !important; color: #1f2937 !important; margin-bottom: 1rem !important; }
    h2 { font-size: 1.5rem !important; font-weight: 600 !important; color: #374151 !important; margin-top: 1.5rem !important; margin-bottom: 1rem !important; }
    h3 { font-size: 1.25rem !important; font-weight: 600 !important; color: #4b5563 !important; }
    
    /* Navigation / Radio Buttons */
    div[data-testid="stSidebar"] div[role="radiogroup"] > label {
        padding: 14px 18px; background-color: transparent; border-radius: 8px; transition: all 0.2s; margin-bottom: 8px;
    }
    div[data-testid="stSidebar"] div[role="radiogroup"] > label:hover { background-color: rgba(0,0,0,0.04); }
    div[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child { transform: scale(1.2); margin-right: 12px; }
    div[data-testid="stSidebar"] p { font-size: 1.15rem; font-weight: 500; }
    
    /* Buttons */
    .stButton > button {
        padding: 0.6rem 1.8rem !important; font-size: 1.1rem !important; font-weight: 500 !important; border-radius: 6px !important; min-height: 48px !important; transition: all 0.2s;
    }
    
    /* KPI Cards */
    .kpi-card {
        background-color: #ffffff; border-radius: 10px; padding: 24px 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.03); text-align: center; border: 1px solid #e5e7eb; border-top: 4px solid #3b82f6; transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .kpi-card:hover { transform: translateY(-2px); box-shadow: 0 6px 16px rgba(0,0,0,0.08); }
    .kpi-card h3 { margin: 0; font-size: 0.95rem !important; color: #6b7280 !important; font-weight: 600 !important; text-transform: uppercase; letter-spacing: 0.05em; }
    .kpi-card h2 { margin: 12px 0 0 0 !important; font-size: 2.2rem !important; color: #111827 !important; font-weight: 700 !important; }

    /* Anomaly Cards */
    .anomaly-card {
        background-color: #fef3c7; border-radius: 8px; padding: 20px; margin-bottom: 16px; border: 1px solid #fde68a; border-left: 6px solid #f59e0b; color: #1f2937 !important; box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .anomaly-card strong { color: #92400e; font-weight: 600; }
    .anomaly-card.critical { background-color: #fee2e2; border-color: #fecaca; border-left: 6px solid #ef4444; }
    .anomaly-card.critical strong { color: #991b1b; }
    .anomaly-row { margin-bottom: 8px; font-size: 1.05rem; }
    
    /* Search Cards */
    .search-card {
        background-color: #ffffff; border-radius: 10px; padding: 24px; margin-bottom: 20px; border: 1px solid #e5e7eb; border-left: 6px solid #8b5cf6; box-shadow: 0 2px 8px rgba(0,0,0,0.04); transition: transform 0.2s ease;
    }
    .search-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
    .search-card-header { font-size: 1.15rem; font-weight: 600; color: #111827; margin-bottom: 6px; }
    .search-card-summary { color: #4b5563; font-size: 1.05rem; margin-bottom: 16px; line-height: 1.5; }
    .search-card-meta { font-size: 0.95rem; color: #6b7280; display: flex; flex-wrap: wrap; gap: 16px; align-items: center; border-top: 1px solid #f3f4f6; padding-top: 12px; }
    .search-card-similarity { background-color: #f3f4f6; color: #374151; padding: 4px 10px; border-radius: 6px; font-weight: 500; font-size: 0.9rem; }
    </style>
""", unsafe_allow_html=True)

# Helper functions for API calls
def fetch_data(endpoint: str, params=None):
    try:
        response = requests.get(f"{API_BASE_URL}{endpoint}", params=params, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data from {endpoint}: {e}")
        return None

def post_data(endpoint: str, data: dict):
    try:
        response = requests.post(f"{API_BASE_URL}{endpoint}", json=data, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json().get('detail', str(e))
                st.error(f"Error: {error_detail}")
            except ValueError:
                st.error(f"Error executing query: {e}")
        else:
            st.error(f"Error executing query: {e}")
        return None

def check_backend_status():
    try:
        # Pinging root or a health endpoint
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

# Sidebar
with st.sidebar:
    st.title("📊 AI Support Intelligence")
    
    page = st.radio("Navigation", ["Overview", "AI Query", "Anomalies", "Semantic Search"])
    
    st.divider()
    st.subheader("System Status")
    is_backend_up = check_backend_status()
    if is_backend_up:
        st.success("Backend: Online")
    else:
        st.error("Backend: Offline")
        st.caption(f"Could not reach {API_BASE_URL}")

# Main Content
if page == "Overview":
    st.title("Support Dashboard Overview")
    st.markdown("High-level metrics and performance analytics for support tickets.")
    
    if is_backend_up:
        summary_data = fetch_data("/analytics/summary")
        if summary_data:
            cols = st.columns(6)
            metrics = [
                ("Total Tickets", summary_data.get("total_tickets", 0)),
                ("Open", summary_data.get("open_tickets", 0)),
                ("Resolved", summary_data.get("resolved_tickets", 0)),
                ("Escalated", summary_data.get("escalated_tickets", 0)),
                ("Critical", summary_data.get("critical_tickets", 0)),
                ("Anomalies", summary_data.get("anomaly_count", 0)),
            ]
            
            for i, (label, value) in enumerate(metrics):
                with cols[i]:
                    st.markdown(f'''
                        <div class="kpi-card">
                            <h3>{label}</h3>
                            <h2>{value}</h2>
                        </div>
                    ''', unsafe_allow_html=True)
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Tickets by Category")
                categories_data = fetch_data("/analytics/categories")
                if categories_data and "results" in categories_data:
                    df_categories = pd.DataFrame(categories_data["results"])
                    if not df_categories.empty and "category" in df_categories.columns and "count" in df_categories.columns:
                        st.bar_chart(df_categories.set_index("category")["count"])
                    else:
                        st.info("No category data available.")
                        
            with col2:
                st.subheader("Tickets by Priority")
                priorities_data = fetch_data("/analytics/priorities")
                if priorities_data and "results" in priorities_data:
                    df_priorities = pd.DataFrame(priorities_data["results"])
                    if not df_priorities.empty and "priority" in df_priorities.columns and "count" in df_priorities.columns:
                        st.bar_chart(df_priorities.set_index("priority")["count"])
                    else:
                        st.info("No priority data available.")
            
            st.subheader("Agent Performance")
            agents_data = fetch_data("/analytics/agents")
            if agents_data and "results" in agents_data:
                df_agents = pd.DataFrame(agents_data["results"])
                if not df_agents.empty:
                    st.dataframe(df_agents, use_container_width=True)
                else:
                    st.info("No agent performance data available.")
    else:
        st.warning("Please ensure the backend is running to view analytics.")

elif page == "AI Query":
    st.title("AI Natural Language Query")
    st.markdown("Ask questions about your support ticket data in plain English.")
    
    question = st.text_input(
        "Ask a question about your support ticket data...",
        placeholder="e.g., How many Critical tickets are unresolved?"
    )
    
    st.markdown("**Suggestions:**")
    st.caption("- How many tickets are currently open?")
    st.caption("- What is the average resolution time for Technical tickets?")
    st.caption("- Which agent resolved the most tickets?")
    st.caption("- How many unresolved High or Critical tickets are older than 24 hours?")
    
    if st.button("Submit Query", type="primary"):
        if not question:
            st.warning("Please enter a question.")
        elif not is_backend_up:
            st.error("Cannot execute query: Backend is offline.")
        else:
            with st.spinner("Analyzing and querying data..."):
                response_data = post_data("/query", {"question": question})
                
                if response_data:
                    st.markdown("### Answer / Result")
                    result_val = response_data.get("result", "No result returned.")
                    plan = response_data.get("plan", {})
                    query_status = plan.get("query_status", "supported")
                    
                    if isinstance(result_val, dict) and "error" in result_val:
                        if query_status == "semantic_search":
                            st.info("I couldn't find a direct statistical answer. Try using the Semantic Search page for this query.")
                        elif query_status == "unclear":
                            st.warning("I couldn't interpret this as a support-ticket question.\n\nI can answer questions about ticket status, priority, category, agents, resolution time, customer ratings, dates, and anomalies.")
                        elif query_status == "out_of_scope":
                            st.warning("This question is outside the scope of this application.\n\nThis system answers questions about the provided support-ticket dataset.")
                        elif query_status == "unsupported":
                            st.warning("This type of analysis is not currently supported.")
                        else:
                            st.error("An error occurred while processing your query.")
                    elif isinstance(result_val, dict):
                        if "results" in result_val and "group_by" in result_val:
                            for row in result_val["results"]:
                                label = str(row.get(result_val["group_by"], "Unknown"))
                                val = row.get("value", 0)
                                st.success(f"**{label}** — {val} tickets")
                        elif "aggregation" in result_val:
                            val = result_val.get("value")
                            agg = result_val.get("aggregation")
                            agg_field = result_val.get("aggregation_field")
                            
                            if agg == "count":
                                st.success(f"**{val} tickets**")
                            elif agg_field and "time" in agg_field:
                                if isinstance(val, float):
                                    st.success(f"**{val:.2f} hours**")
                                else:
                                    st.success(f"**{val} hours**")
                            else:
                                st.success(f"**{val}**")
                        else:
                            count = result_val.get("count", 0)
                            st.success(f"**{count} tickets match this query.**")
                            
                        if "rows" in result_val:
                            with st.expander("View Data"):
                                st.dataframe(result_val["rows"])
                    elif isinstance(result_val, list):
                        st.json(result_val)
                    else:
                        st.info(f"**{result_val}**")
                        
                    if plan and not (isinstance(result_val, dict) and "error" in result_val):
                        if "explanation" in plan:
                            st.markdown("#### How this was calculated")
                            st.info(plan["explanation"])
                            
                        if isinstance(result_val, dict) and "count" in result_val and query_status == "supported":
                            st.markdown("#### Data scope")
                            count = result_val.get("count", 0)
                            agg = plan.get("aggregation")
                            agg_field = plan.get("aggregation_field")
                            
                            if agg and agg != "count" and agg_field:
                                clean_field = agg_field.replace('_hrs', '').replace('_', ' ')
                                st.caption(f"Based on {count} tickets with recorded {clean_field}.")
                            elif count > 0:
                                st.caption(f"{count} tickets matched all specified conditions.")
                            else:
                                st.caption("0 tickets matched the specified conditions.")
                        
                    if plan:
                        st.markdown("#### Query Details")
                        with st.expander("View Execution Plan", expanded=False):
                            st.json(plan)
                    else:
                        st.info("No execution plan details available.")

elif page == "Anomalies":
    st.title("Data Anomalies")
    st.markdown("Review detected anomalies and outliers in support tickets.")
    
    if is_backend_up:
        with st.spinner("Fetching anomalies..."):
            anomalies_data = fetch_data("/anomalies")
            
            if anomalies_data:
                summary = anomalies_data.get("summary", {})
                st.subheader("Anomaly Summary")
                st.write(f"**Total Anomalies:** {summary.get('total_anomalies', 0)}")
                
                counts = summary.get("counts_by_type", {})
                if counts:
                    df_counts = pd.DataFrame(list(counts.items()), columns=["Type", "Count"])
                    st.bar_chart(df_counts.set_index("Type")["Count"])
                
                st.subheader("Anomaly Records")
                anomalies_list = anomalies_data.get("anomalies", [])
                
                if not anomalies_list:
                    st.success("No anomalies detected.")
                else:
                    for anomaly in anomalies_list:
                        severity = anomaly.get("severity", "medium").lower()
                        css_class = "anomaly-card critical" if severity in ["high", "critical"] else "anomaly-card"
                        
                        st.markdown(f'''
                            <div class="{css_class}">
                                <div class="anomaly-row"><strong>Ticket ID:</strong> {anomaly.get("ticket_id", "N/A")}</div>
                                <div class="anomaly-row"><strong>Type:</strong> {anomaly.get("anomaly_type", "Unknown")}</div>
                                <div class="anomaly-row"><strong>Severity:</strong> {anomaly.get("severity", "Unknown")}</div>
                                <div class="anomaly-row"><strong>Reason:</strong> {anomaly.get("reason", "No reason provided")}</div>
                                <div class="anomaly-row"><strong>Value:</strong> {anomaly.get("value", "N/A")}</div>
                            </div>
                        ''', unsafe_allow_html=True)
    else:
        st.warning("Please ensure the backend is running to view anomalies.")

elif page == "Semantic Search":
    st.title("Semantic Ticket Search")
    st.markdown("Find support tickets by meaning, not just exact keywords.")
    
    query = st.text_input(
        "Describe the issue you're looking for...",
        placeholder="e.g., customers being charged incorrectly"
    )
    
    top_k = st.selectbox("Number of results", options=[3, 5, 10], index=1)
    
    if st.button("Search", type="primary"):
        if not query:
            st.warning("Please enter a search query.")
        elif not is_backend_up:
            st.error("Cannot execute search: Backend is offline.")
        else:
            with st.spinner("Searching semantically..."):
                search_data = fetch_data("/search/semantic", params={"q": query, "top_k": top_k})
                
                if not search_data or not search_data.get("results"):
                    st.info("No semantically relevant tickets were found.")
                else:
                    st.markdown(
                        "**Note:** Results are ranked by semantic similarity between your query and the ticket issue summaries using locally generated text embeddings."
                    )
                    
                    for result in search_data["results"]:
                        similarity_val = result.get("similarity", 0)
                        
                        st.markdown(f'''
                            <div class="search-card">
                                <div class="search-card-header">
                                    Ticket: {result.get('ticket_id', 'N/A')}
                                </div>
                                <div class="search-card-summary">
                                    {result.get('issue_summary', 'N/A')}
                                </div>
                                <div class="search-card-meta">
                                    <span class="search-card-similarity">
                                        Similarity: {similarity_val:.3f}
                                    </span>
                                    <span>{result.get('category', 'N/A')} &bull; {result.get('priority', 'N/A')} &bull; {result.get('status', 'N/A')}</span>
                                    <span>Agent: {result.get('agent_id', 'N/A')}</span>
                                    <span>Created: {result.get('created_at', 'N/A')}</span>
                                </div>
                            </div>
                        ''', unsafe_allow_html=True)
