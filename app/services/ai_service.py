import json
from app.llm.groq_provider import GroqProvider

class AIService:
    def __init__(self):
        try:
            self.provider = GroqProvider()
        except Exception:
            self.provider = None

    def classify_ticket(self, subject: str, description: str) -> dict:
        if not self.provider:
            return {"category": "General", "priority": "Medium"}
            
        prompt = f"""
You are an AI support classifier for EduSupport AI.
Categorize the following student request into exactly ONE of these categories:
Fees, Attendance, Examination, ID Card, Certificates, Documents, Technical Support, Hostel, Transport, General.

Also assign a priority: Low, Medium, High, Critical.

Return exactly valid JSON and nothing else.
Format:
{{
  "category": "...",
  "priority": "..."
}}

Subject: {subject}
Description: {description}
"""
        try:
            response = self.provider.generate(prompt)
            result = json.loads(response)
            return result
        except Exception:
            return {"category": "General", "priority": "Medium"}

    def generate_response(self, ticket_context: dict) -> str:
        if not self.provider:
            return "Hello, we have received your request and are looking into it."
            
        prompt = f"""
You are a helpful support agent for EduSupport AI.
Draft a professional response to the student based on this ticket context.
Keep it concise, polite, and helpful. Do not include placeholders, make a reasonable assumption if needed.

Ticket Context:
{json.dumps(ticket_context, indent=2)}
"""
        try:
            return self.provider.generate(prompt)
        except Exception:
            return "Hello, we have received your request and are looking into it."
