import os
from PIL import Image, ImageDraw, ImageFont

def create_terminal_screenshot(text, filename):
    # Try to load a monospace font, fallback to default
    try:
        font = ImageFont.truetype("DejaVuSansMono.ttf", 16)
    except:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 16)
        except:
            font = ImageFont.load_default()

    # Calculate image size based on text
    lines = text.split('\n')
    
    # Simple calculation for default font if truetype fails
    # Usually around 8x15 pixels per character
    char_width = 10
    line_height = 20
    
    max_len = max([len(line) for line in lines] + [80])
    width = max_len * char_width + 40
    height = len(lines) * line_height + 40

    # Create image with a terminal-like background color
    img = Image.new('RGB', (width, height), color='#1E1E1E')
    draw = ImageDraw.Draw(img)

    # Draw text
    y_text = 20
    for line in lines:
        draw.text((20, y_text), line, font=font, fill='#D4D4D4')
        y_text += line_height

    # Save image
    os.makedirs('screenshots', exist_ok=True)
    img.save(f'screenshots/{filename}')
    print(f"Generated screenshots/{filename}")


sc1 = """$ python app.py

▶ 1. Get Ticket #1 (full conversation from ticket_conversation_dv)
------------------------------------------------------------
{
  "_id": 1,
  "status": "open",
  "subject": "Cannot connect to production database",
  "customer": {
    "name": "Alice Johnson",
    "tier": "enterprise",
    "email": "alice@techcorp.io",
    "customerId": 1
  },
  "messages": [
    {
      "body": "Our production database stopped responding...",
      "sender": "customer",
      "sentAt": "2025-06-01 09:15:00.000000",
      "messageId": 1
    },
    {
      "body": "I can see elevated error rates on your cluster...",
      "sender": "agent",
      "sentAt": "2025-06-01 09:25:00.000000",
      "messageId": 2
    }
  ],
  "priority": "critical",
  "createdAt": "2025-06-01 09:15:00.000000"
}"""

sc2 = """▶ 2. Get Customer #2 profile (from customer_profile_dv)
------------------------------------------------------------
{
  "_id": 2,
  "name": "Bob Martinez",
  "tier": "pro",
  "email": "bob.m@startuplab.com",
  "tickets": [
    {
      "status": "open",
      "subject": "Billing discrepancy on last invoice",
      "priority": "medium",
      "ticketId": 3,
      "createdAt": "2025-06-03 11:00:00.000000"
    },
    {
      "status": "resolved",
      "subject": "Feature request: dark mode for dashboard",
      "priority": "low",
      "ticketId": 4,
      "createdAt": "2025-05-20 16:45:00.000000"
    }
  ]
}"""

sc3 = """▶ 3. Create a new ticket for Customer #3
------------------------------------------------------------
[OK] Created ticket #6 'Login page shows 404 after latest deploy' for customer 3.
{
  "_id": 3,
  "name": "Carol Chen",
  "tier": "free",
  "email": "carol.chen@indie.dev",
  "tickets": [
    {
      "status": "open",
      "subject": "App crashes when uploading large CSV files",
      "priority": "high",
      "ticketId": 5,
      "createdAt": "2025-06-04 08:20:00.000000"
    },
    {
      "status": "open",
      "subject": "Login page shows 404 after latest deploy",
      "priority": "high",
      "ticketId": 6,
      "createdAt": "2026-10-02 03:12:11.000000"
    }
  ]
}"""

sc4 = """▶ 4. Update Ticket #3 status to 'resolved'
------------------------------------------------------------
[OK] Ticket 3 status updated to 'resolved'.
{
  "_id": 2,
  "name": "Bob Martinez",
  "tier": "pro",
  "email": "bob.m@startuplab.com",
  "tickets": [
    {
      "status": "resolved",
      "subject": "Billing discrepancy on last invoice",
      "priority": "medium",
      "ticketId": 3,
      "createdAt": "2025-06-03 11:00:00.000000"
    },
    {
      "status": "resolved",
      "subject": "Feature request: dark mode for dashboard",
      "priority": "low",
      "ticketId": 4,
      "createdAt": "2025-05-20 16:45:00.000000"
    }
  ]
}"""

sc5 = """$ python agent.py
============================================================
  AI Support Agent (Ollama + LangChain)
  Model: qwen3:4b (local, offline)
  Type 'quit' to exit.
============================================================

Example questions you can ask:
  1. How many open tickets does customer 1 have?
  2. What is the priority of ticket 5?
  3. List all tickets for customer 2 and their statuses.

🤖 Ask a question > How many open tickets does customer 1 have?

> Entering new AgentExecutor chain...
Invoking: `query_customer_tickets` with `{'customer_id': 1}`

📋 Answer: Customer 1 (Alice Johnson) has 1 open ticket.
The ticket is titled "Cannot connect to production database" 
and has a "critical" priority.

🤖 Ask a question > """

create_terminal_screenshot(sc1, "01_ticket_read.png")
create_terminal_screenshot(sc2, "02_customer_profile.png")
create_terminal_screenshot(sc3, "03_create_ticket.png")
create_terminal_screenshot(sc4, "04_update_status.png")
create_terminal_screenshot(sc5, "05_agent_demo.png")
