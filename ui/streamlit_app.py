import streamlit as st
import requests
import os
import pandas as pd
from datetime import datetime

st.set_page_config(
    page_title="EduSupport AI",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")

st.markdown("""
    <style>
    .kpi-card { background-color: #ffffff; border-radius: 10px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); text-align: center; border-top: 4px solid #4f46e5; }
    .kpi-card h3 { margin: 0; font-size: 1rem; color: #6b7280; font-weight: 600; text-transform: uppercase; }
    .kpi-card h2 { margin: 10px 0 0 0; font-size: 2rem; color: #111827; font-weight: 700; }
    .stButton>button { border-radius: 8px; }
    .timeline-item { border-left: 2px solid #e5e7eb; padding-left: 15px; margin-bottom: 15px; }
    .timeline-date { font-size: 0.8rem; color: #6b7280; }
    .timeline-action { font-weight: 600; color: #111827; }
    .badge { padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: bold; }
    .badge.high { background: #fee2e2; color: #991b1b; }
    .badge.normal { background: #dcfce3; color: #166534; }
    </style>
""", unsafe_allow_html=True)

def fetch_data(endpoint: str, params=None):
    try:
        res = requests.get(f"{API_BASE_URL}{endpoint}", params=params, timeout=10)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        return None

def post_data(endpoint: str, data: dict):
    try:
        res = requests.post(f"{API_BASE_URL}{endpoint}", json=data, timeout=30)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        st.error(f"Error: {e}")
        return None
        
def patch_data(endpoint: str, data: dict):
    try:
        res = requests.patch(f"{API_BASE_URL}{endpoint}", json=data, timeout=30)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def render_ticket_detail(ticket_id: str, role: str, user_id: str):
    ticket = fetch_data(f"/tickets/{ticket_id}", params={"user_id": user_id, "role": role})
    if not ticket:
        st.error("Ticket not found or you do not have permission to view it.")
        return
        
    if role == "Student" and ticket.get("student_id") != user_id:
        st.error("Access Denied: This ticket belongs to another student.")
        return
        
    st.subheader(f"Ticket: {ticket['ticket_id']} - {ticket['subject']}")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"**Student:** {ticket['student_name']} ({ticket['student_id']})")
        st.markdown(f"**Description:** {ticket['description']}")
        
        st.divider()
        st.markdown("### Activity Timeline")
        for act in ticket.get("activity", []):
            date_str = act.get("created_at", "")[:16].replace("T", " ")
            st.markdown(f"""
            <div class="timeline-item">
                <div class="timeline-date">{date_str} - {act['user_id']} ({act['user_role']})</div>
                <div class="timeline-action">{act['action_type']}</div>
                <div>{act['details']}</div>
            </div>
            """, unsafe_allow_html=True)
            
        st.divider()
        if role == "Student":
            st.markdown("### Add Reply")
        else:
            st.markdown("### Add Reply / Internal Note")
        reply = st.text_area("Your message", key=f"reply_{ticket_id}")
        if st.button("Submit Reply", key=f"btn_reply_{ticket_id}"):
            patch_data(f"/tickets/{ticket_id}", {"reply": reply, "user_id": user_id, "user_role": role.lower()})
            st.rerun()

    with col2:
        st.markdown("### Details")
        st.write(f"**Status:** {ticket['status']}")
        st.write(f"**Priority:** {ticket['priority']}")
        st.write(f"**Category:** {ticket['category']}")
        st.write(f"**Assigned:** {ticket['assigned_agent'] or 'Unassigned'}")
        
        sla = ticket.get("sla", {})
        sla_state = sla.get('state', 'UNKNOWN')
        rem = sla.get('remaining_hours', 0)
        st.write(f"**SLA State:** {sla_state}")
        if ticket['status'] not in ["RESOLVED", "CLOSED"]:
            st.write(f"**Remaining Time:** {rem} hours")
        
        if role in ["Staff", "Manager"]:
            st.markdown("### Actions")
            
            # AI Response Assist
            if st.button("Generate AI Response", key=f"ai_{ticket_id}"):
                with st.spinner("Generating..."):
                    resp = post_data("/tickets/ai/response", {"ticket_id": ticket_id})
                    if resp:
                        st.text_area("AI Draft Response (Copy to reply)", value=resp.get("draft_response", ""), height=150)
            
            # Update Status
            new_status = st.selectbox("Update Status", ["NEW", "ASSIGNED", "IN_PROGRESS", "PENDING", "RESOLVED", "CLOSED", "ESCALATED"], index=["NEW", "ASSIGNED", "IN_PROGRESS", "PENDING", "RESOLVED", "CLOSED", "ESCALATED"].index(ticket['status']), key=f"status_{ticket_id}")
            
            pending_reason = ""
            resolution_notes = ""
            escalation_reason = ""
            
            if new_status == "PENDING":
                pending_reason = st.selectbox("Pending Reason", ["Waiting for Student", "Waiting for Documents", "Waiting for Department", "Waiting for External System"], key=f"pending_{ticket_id}")
            elif new_status in ["RESOLVED", "CLOSED"]:
                resolution_notes = st.text_input("Resolution Notes", key=f"resolve_{ticket_id}")
            elif new_status == "ESCALATED":
                escalation_reason = st.text_input("Escalation Reason", key=f"escalate_{ticket_id}")
                
            if st.button("Save Status", key=f"save_status_{ticket_id}"):
                payload = {"status": new_status, "user_id": user_id, "user_role": role.lower()}
                if pending_reason: payload["pending_reason"] = pending_reason
                if resolution_notes: payload["resolution_notes"] = resolution_notes
                if escalation_reason: payload["escalation_reason"] = escalation_reason
                patch_data(f"/tickets/{ticket_id}", payload)
                st.rerun()
                
            # Assign
            new_agent = st.text_input("Assign to Agent ID", value=ticket['assigned_agent'] or user_id, key=f"agent_{ticket_id}")
            if st.button("Assign", key=f"assign_{ticket_id}"):
                patch_data(f"/tickets/{ticket_id}", {"assigned_agent": new_agent, "user_id": user_id, "user_role": role.lower(), "status": "ASSIGNED" if ticket['status'] == "NEW" else ticket['status']})
                st.rerun()


# Sidebar - Role Selection
st.sidebar.title("🎓 EduSupport AI")
role = st.sidebar.selectbox("Select Role", ["Student", "Staff", "Manager"])
st.sidebar.divider()

if role == "Student":
    student_id = st.sidebar.text_input("Student ID", value="STU1234")
    student_name = st.sidebar.text_input("Student Name", value="Demo Student")
    
    page = st.sidebar.radio("Navigation", ["My Tickets", "Create Ticket", "Ticket Detail"])
    
    if page == "Create Ticket":
        st.title("Create a Support Ticket")
        with st.form("create_ticket_form"):
            subject = st.text_input("Subject")
            description = st.text_area("Description")
            
            if st.form_submit_button("Submit"):
                if not subject.strip() or len(subject.strip()) < 5:
                    st.error("Please enter a valid subject (min 5 characters).")
                elif not description.strip() or len(description.strip()) < 10:
                    st.error("Please enter a valid description (min 10 characters).")
                else:
                    with st.spinner("AI is classifying your request..."):
                        classification = post_data("/tickets/ai/classify", {"subject": subject, "description": description})
                        cat = classification.get("category", "General") if classification else "General"
                        prio = classification.get("priority", "Medium") if classification else "Medium"
                        
                        data = {
                            "student_id": student_id,
                            "student_name": student_name,
                            "category": cat,
                            "subject": subject,
                            "description": description,
                            "priority": prio
                        }
                        res = post_data("/tickets", data)
                        if res:
                            st.success(f"Ticket created successfully! Ticket ID: {res.get('ticket_id')} (Category: {cat}, Priority: {prio})")
                        
    elif page == "My Tickets":
        st.title("My Tickets")
        tickets = fetch_data("/tickets", params={"student_id": student_id})
        if tickets:
            df = pd.DataFrame(tickets)
            if not df.empty:
                # Add SLA formatted string
                df['SLA'] = df.apply(lambda row: f"{row['sla']['state']}" if row['status'] in ('RESOLVED', 'CLOSED') else f"{row['sla']['state']} ({row['sla']['remaining_hours']}h left)", axis=1)
                st.dataframe(df[['ticket_id', 'subject', 'status', 'priority', 'category', 'SLA', 'created_at']])
                st.info("To view a ticket's details, select 'Ticket Detail' from the navigation and enter the Ticket ID.")
        else:
            st.info("No tickets found.")
            
    elif page == "Ticket Detail":
        tid = st.text_input("Enter Ticket ID to view:")
        if tid:
            render_ticket_detail(tid, role, student_id)

elif role == "Staff":
    agent_id = st.sidebar.text_input("Agent ID", value="AGT-01")
    page = st.sidebar.radio("Navigation", ["My Queue", "Unassigned Tickets", "Ticket Detail", "Similar Tickets"])
    
    if page == "My Queue":
        st.title("My Assigned Tickets")
        tickets = fetch_data("/tickets", params={"agent_id": agent_id})
        if tickets:
            df = pd.DataFrame(tickets)
            df['SLA'] = df.apply(lambda row: f"{row['sla']['state']}" if row['status'] in ('RESOLVED', 'CLOSED') else f"{row['sla']['state']} ({row['sla']['remaining_hours']}h left)", axis=1)
            st.dataframe(df[['ticket_id', 'subject', 'status', 'priority', 'category', 'SLA']])
            st.info("Navigate to 'Ticket Detail' to process a ticket.")
        else:
            st.info("No assigned tickets.")
            
    elif page == "Unassigned Tickets":
        st.title("Unassigned Tickets")
        tickets = fetch_data("/tickets")
        if tickets:
            unassigned = [t for t in tickets if not t.get("assigned_agent") and t.get("status") not in ("RESOLVED", "CLOSED")]
            if unassigned:
                df = pd.DataFrame(unassigned)
                df['SLA'] = df.apply(lambda row: f"{row['sla']['state']}" if row['status'] in ('RESOLVED', 'CLOSED') else f"{row['sla']['state']} ({row['sla']['remaining_hours']}h left)", axis=1)
                st.dataframe(df[['ticket_id', 'subject', 'status', 'priority', 'category', 'SLA']])
                st.info("Navigate to 'Ticket Detail' to claim a ticket.")
            else:
                st.info("No unassigned tickets.")
                
    elif page == "Ticket Detail":
        tid = st.text_input("Enter Ticket ID to manage:")
        if tid:
            render_ticket_detail(tid, role, agent_id)
                
    elif page == "Similar Tickets":
        st.title("Similar Ticket Search")
        query = st.text_input("Describe the issue:")
        if st.button("Search") and query:
            res = fetch_data("/search/semantic", params={"q": query, "top_k": 5})
            if res and res.get("results"):
                found = False
                for r in res["results"]:
                    if r.get('similarity', 0) > 0.4:
                        st.write(f"**{r['ticket_id']}**: {r.get('issue_summary', r.get('subject', ''))} (Similarity: {r['similarity']:.2f})")
                        found = True
                if not found:
                    st.info("No similar resolved tickets found.")
            else:
                st.info("No similar resolved tickets found.")

elif role == "Manager":
    page = st.sidebar.radio("Navigation", ["Dashboard", "All Tickets", "Ticket Detail", "NL Analytics"])
    
    if page == "Dashboard":
        st.title("Manager Dashboard")
        tickets = fetch_data("/tickets")
        if tickets:
            total = len(tickets)
            open_t = len([t for t in tickets if t['status'] not in ("RESOLVED", "CLOSED")])
            unassigned = len([t for t in tickets if not t.get("assigned_agent") and t['status'] not in ("RESOLVED", "CLOSED")])
            at_risk = len([t for t in tickets if t['sla']['state'] == 'AT_RISK' and t['status'] not in ("RESOLVED", "CLOSED")])
            breached = len([t for t in tickets if t['sla']['state'] == 'BREACHED' and t['status'] not in ("RESOLVED", "CLOSED")])
            escalated = len([t for t in tickets if t['status'] == 'ESCALATED'])
            resolved = len([t for t in tickets if t['status'] in ("RESOLVED", "CLOSED")])
            
            c1, c2, c3, c4 = st.columns(4)
            with c1: st.markdown(f'<div class="kpi-card"><h3>Total</h3><h2>{total}</h2></div>', unsafe_allow_html=True)
            with c2: st.markdown(f'<div class="kpi-card"><h3>Open (incl. Escalated)</h3><h2>{open_t}</h2></div>', unsafe_allow_html=True)
            with c3: st.markdown(f'<div class="kpi-card"><h3>Unassigned</h3><h2>{unassigned}</h2></div>', unsafe_allow_html=True)
            with c4: st.markdown(f'<div class="kpi-card"><h3>Resolved</h3><h2>{resolved}</h2></div>', unsafe_allow_html=True)
            
            st.divider()
            c5, c6, c7 = st.columns(3)
            with c5: st.markdown(f'<div class="kpi-card"><h3>SLA At Risk</h3><h2>{at_risk}</h2></div>', unsafe_allow_html=True)
            with c6: st.markdown(f'<div class="kpi-card"><h3>SLA Breached</h3><h2>{breached}</h2></div>', unsafe_allow_html=True)
            with c7: st.markdown(f'<div class="kpi-card"><h3>Escalated</h3><h2>{escalated}</h2></div>', unsafe_allow_html=True)
            
            st.divider()
            df = pd.DataFrame(tickets)
            if not df.empty:
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Tickets by Category")
                    st.bar_chart(df['category'].value_counts())
                with col2:
                    st.subheader("Tickets by Priority")
                    st.bar_chart(df['priority'].value_counts())
                    
    elif page == "All Tickets":
        st.title("All Tickets")
        tickets = fetch_data("/tickets")
        if tickets:
            df = pd.DataFrame(tickets)
            df['SLA'] = df.apply(lambda row: f"{row['sla']['state']}" if row['status'] in ('RESOLVED', 'CLOSED') else f"{row['sla']['state']} ({row['sla']['remaining_hours']}h left)", axis=1)
            
            # Filters
            col1, col2, col3, col4 = st.columns(4)
            f_id = col1.text_input("Filter by Ticket ID")
            f_name = col2.text_input("Filter by Student Name")
            f_cat = col3.selectbox("Category", ["All"] + sorted(list(df['category'].dropna().unique())))
            f_status = col4.selectbox("Status", ["All"] + sorted(list(df['status'].dropna().unique())))
            
            if f_id:
                df = df[df['ticket_id'].str.contains(f_id, case=False, na=False)]
            if f_name:
                df = df[df['student_name'].str.contains(f_name, case=False, na=False)]
            if f_cat != "All":
                df = df[df['category'] == f_cat]
            if f_status != "All":
                df = df[df['status'] == f_status]
                
            st.dataframe(df[['ticket_id', 'student_name', 'category', 'priority', 'status', 'assigned_agent', 'SLA', 'created_at']])
            st.info("Navigate to 'Ticket Detail' to view or manage a ticket.")
            
    elif page == "Ticket Detail":
        tid = st.text_input("Enter Ticket ID to view:")
        if tid:
            render_ticket_detail(tid, role, "Manager")
            
    elif page == "NL Analytics":
        st.title("Natural Language Analytics")
        query = st.text_input("Ask a question about support data:")
        if st.button("Ask") and query:
            with st.spinner("Thinking..."):
                res = post_data("/query", {"question": query})
                if res:
                    res_dict = res.get("result", {})
                    if "error" in res_dict:
                        st.error(res_dict["error"])
                    elif "count" in res_dict and "aggregation" not in res_dict:
                        st.success(f"Result: {res_dict['count']}")
                        if "rows" in res_dict and res_dict["rows"]:
                            st.dataframe(pd.DataFrame(res_dict["rows"]))
                    elif "aggregation" in res_dict:
                        agg = res_dict.get("aggregation")
                        field = res_dict.get("aggregation_field")
                        val = res_dict.get("aggregation_value")
                        st.success(f"Result ({agg} of {field}): {val}")
                    elif "rows" in res_dict:
                        st.success("Result:")
                        st.dataframe(pd.DataFrame(res_dict["rows"]))
                    else:
                        st.json(res_dict)
                        
                    if "plan" in res:
                        with st.expander("View Execution Plan"):
                            st.json(res["plan"])
