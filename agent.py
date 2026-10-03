#!/usr/bin/env python3
"""AI Agent for Customer Support — Ollama + LangChain.

A fully local, offline AI agent that queries MySQL 9.7 JSON Duality Views
to answer natural-language questions about customer support tickets.

Requirements:
    pip install langchain-ollama langchain-core langchain
    ollama pull llama3.2
"""

import json
import sys

import mysql.connector
from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_ollama import ChatOllama

# ── Database Configuration ────────────────────────────────────────────
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3307,
    "user": "root",
    "password": "root123",
    "database": "support_db",
}


# ── Tool: Query Customer Tickets ──────────────────────────────────────
@tool
def query_customer_tickets(customer_id: int) -> str:
    """Query customer support tickets from the database.

    Reads the customer_profile_dv JSON Duality View to get a full
    customer profile including all their support tickets.

    Args:
        customer_id: The numeric ID of the customer to look up.

    Returns:
        A JSON string with the customer profile and their tickets.
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT JSON_PRETTY(data) FROM customer_profile_dv "
            "WHERE data->'$._id' = %s",
            (customer_id,)
        )
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if row is None:
            return json.dumps({"error": f"Customer {customer_id} not found."})
        return row[0]
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool
def query_ticket_details(ticket_id: int) -> str:
    """Query detailed ticket information including all messages.

    Reads the ticket_conversation_dv JSON Duality View to get the
    full ticket with customer info and conversation history.

    Args:
        ticket_id: The numeric ID of the ticket to look up.

    Returns:
        A JSON string with the full ticket document.
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT JSON_PRETTY(data) FROM ticket_conversation_dv "
            "WHERE data->'$._id' = %s",
            (ticket_id,)
        )
        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if row is None:
            return json.dumps({"error": f"Ticket {ticket_id} not found."})
        return row[0]
    except Exception as e:
        return json.dumps({"error": str(e)})


# ── Agent Setup ───────────────────────────────────────────────────────

def create_support_agent():
    """Create and return the LangChain agent with Ollama LLM."""

    # Local LLM via Ollama — no API keys needed
    llm = ChatOllama(
        model="llama3.2",
        temperature=0,
    )

    # Tools available to the agent
    tools = [query_customer_tickets, query_ticket_details]

    # System prompt for the agent
    system_message = (
        "You are a helpful customer support analyst. You have access to a "
        "MySQL database with customer and ticket data exposed through JSON "
        "Duality Views. Use the available tools to query the database and "
        "answer questions accurately. Always base your answers on the actual "
        "data returned by the tools. Be concise and professional."
    )

    # Create the agent
    agent_executor = create_react_agent(
        model=llm,
        tools=tools,
        prompt=system_message,
    )

    return agent_executor


def main():
    """Interactive agent loop."""
    print("=" * 60)
    print("  AI Support Agent (Ollama + LangChain)")
    print("  Model: llama3.2 (local, offline)")
    print("  Type 'quit' to exit.")
    print("=" * 60)

    agent = create_support_agent()

    # Example questions to try:
    examples = [
        "How many open tickets does customer 1 have?",
        "What is the priority of ticket 5?",
        "List all tickets for customer 2 and their statuses.",
    ]
    print("\nExample questions you can ask:")
    for i, q in enumerate(examples, 1):
        print(f"  {i}. {q}")
    print()

    while True:
        try:
            question = input("\n🤖 Ask a question > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not question or question.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        try:
            result = agent.invoke({"messages": [("user", question)]})
            print(f"\n📋 Answer: {result['messages'][-1].content}")
        except Exception as e:
            print(f"\n[ERROR] Agent failed: {e}")
            print("Make sure Ollama is running: ollama serve")
            print("And the model is downloaded: ollama pull llama3.2")


if __name__ == "__main__":
    main()
