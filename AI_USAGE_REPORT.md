# AI Usage Report

## 1. AI Tools Used
- Gemini 3.1 Pro (via Antigravity IDE)

## 2. What AI Was Asked to Do
- Analyze the existing AI Support Intelligence Platform and propose an architecture shift towards a Student Support domain (EduSupport AI).
- Implement a persistent database layer using SQLite to enable mutable data (creation, updates, assignment, activity history).
- Write an SLA Engine with predefined threshold rules (Critical=4h, High=8h, Medium=24h, Low=48h) to compute elapsed time, percentage consumed, and breach status.
- Add AI Ticket Classification to parse incoming descriptions and assign Categories and Priorities via the existing Groq LLM integration.
- Add an AI Draft Response generator for staff to efficiently resolve tickets.
- Redesign the Streamlit UI to support Role-Based access (Student, Staff, Manager).
- Create a data seeding script to transform existing analytical dataset into domain-specific mutable student tickets.

## 3. Useful Prompts
- "Transform the existing AI Support Intelligence Platform into a polished product-engineering solution for: 'Student Support & Ticket Management'"
- "Implement a real ticket workflow... Use role-based behavior at the application level."
- "Implement a deterministic SLA system... Do not rely on the LLM for SLA calculations."

## 4. What Code AI Generated
- `app/data/db.py`: SQLite connection and initialization logic.
- `app/services/ticket_service.py`: CRUD operations for tickets, integrating with activity logs.
- `app/services/sla_service.py`: Deterministic SLA calculation based on elapsed time and priority limits.
- `app/services/ai_service.py`: AI Classification and Response Assistant functions integrating with `GroqProvider`.
- `app/api/routes_tickets.py`: FastAPI endpoints for Ticket and AI functionality.
- `ui/streamlit_app.py`: Complete overhaul of the frontend, introducing tabs, role selection, and interacting with the new mutability endpoints.
- `scripts/seed_db.py`: Transformation script parsing `support_tickets.csv` and populating `edusupport.db`.

## 5. Errors Produced by AI & Fixes
- **SQLite Database Lock**: Initially, the `seed_db.py` loop called a DB function `log_activity` that created a new connection for every iteration while an outer connection was uncommitted, resulting in an `sqlite3.OperationalError: database is locked`.
  - *Fix*: Refactored `log_activity` in `app/data/db.py` to optionally accept an existing `conn` parameter, and updated the `seed_db.py` script to pass its active connection.
- **File Replace Content Error**: Faced a target-content mismatch when trying to append AI endpoints to `routes_tickets.py`.
  - *Fix*: Used `view_file` to read the exact end of the file before re-applying the patch.

## 6. What Was Manually Validated
- Verified that SQLite correctly stored tickets and activity logs.
- Ensured the Streamlit UI switched cleanly between Student, Staff, and Manager modes.
- Confirmed that LLM classification gracefully defaults when no provider is active, keeping the app usable.
- Validated that the SLA percentages computed correctly against historical dataset time intervals.
