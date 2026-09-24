# AI Usage Report — EduSupport AI

## AI Tools Used

- ChatGPT
- Antigravity AI Coding Agent
- Browser/Preview Subagent

AI assistance was used throughout the development process to accelerate implementation, debugging, testing, UI refinement, and validation.

The AI tools were used as development assistants. Product decisions, scope selection, architecture direction, engineering trade-offs, validation criteria, and final acceptance were reviewed and directed by me.

---

## What I Asked AI To Do

1. Help analyze the Edumerge open-ended Student Support & Ticket Management problem and define a practical product scope, user roles, workflows, architecture, and implementation priorities.

2. Help transform an existing AI support analytics prototype into a student-support product while preserving reusable backend, AI, semantic-search, and deterministic analytics components.

3. Assist with implementation, debugging, UI refinement, test creation/fixing, repository cleanup, and browser-based Preview verification.

---

## My Role in the Development Process

I used AI tools primarily to accelerate implementation and iteration under the assessment's limited development timeline.

I was responsible for:

- selecting the assignment and defining the product direction
- deciding which existing components should be reused
- defining the Student, Staff, and Manager workflows
- defining ticket lifecycle and operational requirements
- defining SLA behavior and escalation/pending workflows
- deciding where deterministic logic should be used instead of LLM-generated execution
- reviewing generated implementation changes
- testing the application and identifying incorrect behavior
- directing corrective changes
- validating the final product through automated tests and Preview/browser verification
- reviewing the final repository structure and documentation
- deciding which experimental functionality should be removed because it was outside the selected problem scope

---

## What AI Assisted With

AI-assisted implementation was used for areas including:

- ticket workflow implementation
- assignment and reassignment
- role-based authorization behavior
- SLA logic and SLA presentation
- pending and escalation workflow handling
- activity timeline implementation
- input validation
- ticket filtering
- AI ticket classification
- AI response generation
- semantic similar-ticket search
- Natural Language Analytics integration
- test implementation and updates
- UI refinement
- code cleanup and refactoring

The coding agent was instructed to inspect and reuse the existing codebase rather than rebuild the project from scratch.

---

## Most Useful Prompt

The most useful prompt was the structured product-engineering implementation prompt that instructed the AI coding agent to:

- inspect the existing repository first
- reuse working components
- transform the system into a Student Support & Ticket Management platform
- implement student, staff and manager workflows
- implement ticket lifecycle, SLA, assignment, escalation and pending workflows
- retain controlled AI capabilities
- preserve deterministic business logic
- add validation and edge-case handling
- test the implementation using the Preview environment
- report actual bugs and verification results

---

## Where AI-Generated Implementation Was Reviewed

AI-generated or AI-assisted changes were not accepted solely because they compiled or appeared correct.

The implementation was repeatedly reviewed through:

- Pytest
- API behavior
- Preview/browser verification
- end-to-end workflow testing
- dashboard/data consistency checks
- role-based access testing
- invalid-input testing
- AI failure/fallback testing
- semantic-search testing

---

## AI Output That Was Wrong

During iterative development, several AI-assisted implementation issues were identified.

Examples:

1. Ticket activity initially included events from other tickets.
2. Student ID and Ticket ID were initially displayed incorrectly in one ticket-detail workflow.
3. Student access initially allowed viewing another student's ticket by entering its ticket ID.
4. SLA presentation initially allowed resolved tickets to appear as if their live SLA timer were still active.
5. The All Tickets view initially lacked practical filtering controls.
6. Similar-ticket search initially had an insufficiently clear no-result experience.
7. Short or whitespace-only ticket descriptions were initially accepted.
8. Test execution initially introduced temporary test data into the active SQLite database.

These issues were identified during review and verification and were subsequently corrected.

---

## How I Identified the Problems

Problems were identified by combining automated and manual validation:

- unit/integration tests
- Preview/browser testing
- end-to-end role workflows
- API checks
- inspection of displayed ticket data
- verification of dashboard counts
- authorization tests
- invalid-input tests
- comparison of analytics answers with deterministic application results

---

## How the Problems Were Fixed

The issues were addressed through targeted implementation changes.

Examples include:

- enforcing activity filtering by `ticket_id`
- enforcing student ticket ownership
- separating Student ID from Ticket ID
- updating resolved/closed SLA behavior to use historical SLA outcomes
- adding practical ticket filters
- adding similarity thresholds and explicit no-result handling
- adding minimum-length input validation
- resetting the database to clean deterministic seed data
- removing an obsolete anomaly module that was outside the final assessment scope

---

## AI and Deterministic Architecture

A core engineering decision was to avoid giving the LLM unrestricted control over business-critical execution.

The Natural Language Analytics flow uses:

User Question
    ↓
LLM Interpretation
    ↓
Validated Structured QueryPlan
    ↓
Deterministic Execution
    ↓
Verified Result

The LLM interprets user intent, while application logic performs the actual ticket analytics and business calculations.

Similarly, SLA calculations and ticket workflow rules remain deterministic.

---

## Human-in-the-Loop AI

AI-generated responses are treated as drafts rather than automatically sent messages.

For example:

Ticket Context
    ↓
AI Response Generation
    ↓
Draft Response
    ↓
Staff Review / Edit
    ↓
Manual Send

This keeps the final communication under staff control.

---

## Final Validation

The final implementation was validated using automated tests and Preview/browser workflows.

Final reported test result:

37 passed
2 warnings

The final Preview verification included:

- Student ticket creation
- Student ticket ownership enforcement
- Staff assignment
- AI response generation
- status updates
- pending workflow
- resolution
- SLA historical outcome
- Manager dashboard visibility
- Natural Language Analytics
- Similar Ticket Search
- unsupported-query fallback

---

## Final Perspective

AI tools significantly reduced implementation time and helped accelerate development, debugging, and iteration.

However, the final product was driven by product and engineering decisions made during the development process, followed by repeated review, testing, correction, and validation before submission.
