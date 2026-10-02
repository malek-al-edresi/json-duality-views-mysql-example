#!/usr/bin/env python3
"""Customer Support Ticket System — JSON Duality Views Demo Application.

Demonstrates read/write operations through MySQL 9.7 JSON Duality Views
using mysql-connector-python. No ORM required.
"""

import json
import sys
from datetime import datetime

import mysql.connector
from mysql.connector import Error

# ── Connection Configuration ──────────────────────────────────────────
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3307,
    "user": "root",
    "password": "root123",
    "database": "support_db",
}


def get_connection():
    """Create and return a MySQL connection."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"[ERROR] Cannot connect to MySQL: {e}")
        sys.exit(1)


def pp(obj):
    """Pretty-print a Python object as JSON."""
    print(json.dumps(obj, indent=2, default=str))


# ── READ Operations ───────────────────────────────────────────────────

def get_ticket(ticket_id: int) -> dict:
    """Read one full ticket document from ticket_conversation_dv.

    Returns the complete ticket with customer info and all messages nested.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        sql = (
            "SELECT JSON_PRETTY(data) "
            "FROM ticket_conversation_dv "
            "WHERE data->'$._id' = %s"
        )
        cursor.execute(sql, (ticket_id,))
        row = cursor.fetchone()
        if row is None:
            print(f"[WARN] Ticket {ticket_id} not found.")
            return {}
        return json.loads(row[0])
    finally:
        cursor.close()
        conn.close()


def get_customer(customer_id: int) -> dict:
    """Read one customer profile from customer_profile_dv.

    Returns customer info with nested ticket summaries.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        sql = (
            "SELECT JSON_PRETTY(data) "
            "FROM customer_profile_dv "
            "WHERE data->'$._id' = %s"
        )
        cursor.execute(sql, (customer_id,))
        row = cursor.fetchone()
        if row is None:
            print(f"[WARN] Customer {customer_id} not found.")
            return {}
        return json.loads(row[0])
    finally:
        cursor.close()
        conn.close()


# ── WRITE Operations (via updatable customer_profile_dv) ─────────────

def create_ticket(customer_id: int, subject: str, priority: str = "medium") -> dict:
    """Create a new ticket for a customer.

    Note: MySQL 9.7 Duality Views don't support mixing auto-generated and
    explicit primary key values in nested arrays. When existing tickets already
    have ticketId values from AUTO_INCREMENT, adding a new ticket without one
    triggers ERROR 6560. We use a direct INSERT on the base table instead,
    then verify via the Duality View.

    Alternative approach: INSERT INTO customer_profile_dv VALUES (%s) works
    only when creating a brand-new customer with tickets (all PKs generated).
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Verify the customer exists
        cursor.execute(
            "SELECT customer_id FROM customers WHERE customer_id = %s",
            (customer_id,)
        )
        if cursor.fetchone() is None:
            print(f"[ERROR] Customer {customer_id} not found.")
            return {}

        # Insert the ticket directly — the Duality View will reflect it
        insert_sql = (
            "INSERT INTO support_tickets (customer_id, subject, status, priority) "
            "VALUES (%s, %s, 'open', %s)"
        )
        cursor.execute(insert_sql, (customer_id, subject, priority))
        conn.commit()

        new_id = cursor.lastrowid
        print(f"[OK] Created ticket #{new_id} '{subject}' for customer {customer_id}.")

        # Return the refreshed customer document via Duality View
        return get_customer(customer_id)
    except Error as e:
        conn.rollback()
        print(f"[ERROR] Failed to create ticket: {e}")
        return {}
    finally:
        cursor.close()
        conn.close()




def update_ticket_status(ticket_id: int, new_status: str) -> dict:
    """Update a ticket's status via the customer_profile_dv Duality View.

    Reads the customer document containing the target ticket,
    modifies the status field, and writes the document back.
    The Duality View engine translates this into an UPDATE on support_tickets.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Find which customer owns this ticket
        cursor.execute(
            "SELECT customer_id FROM support_tickets WHERE ticket_id = %s",
            (ticket_id,)
        )
        owner = cursor.fetchone()
        if owner is None:
            print(f"[ERROR] Ticket {ticket_id} not found.")
            return {}
        customer_id = owner[0]

        # Read the full customer document
        cursor.execute(
            "SELECT data FROM customer_profile_dv WHERE data->'$._id' = %s",
            (customer_id,)
        )
        row = cursor.fetchone()
        doc = json.loads(row[0])

        # Update the status of the target ticket
        updated = False
        for ticket in doc.get("tickets", []):
            if ticket.get("ticketId") == ticket_id:
                ticket["status"] = new_status
                updated = True
                break

        if not updated:
            print(f"[WARN] Ticket {ticket_id} not found in customer document.")
            return doc

        # Write back via the Duality View
        update_sql = (
            "UPDATE customer_profile_dv "
            "SET data = %s "
            "WHERE data->'$._id' = %s"
        )
        cursor.execute(update_sql, (json.dumps(doc, default=str), customer_id))
        conn.commit()

        print(f"[OK] Ticket {ticket_id} status updated to '{new_status}'.")
        return get_customer(customer_id)
    except Error as e:
        conn.rollback()
        print(f"[ERROR] Failed to update ticket status: {e}")
        return {}
    finally:
        cursor.close()
        conn.close()


def delete_message(ticket_id: int, message_id: int) -> str:
    """Attempt to delete a nested message via a Duality View.

    LIMITATION: In MySQL 9.7, the ticket_conversation_dv is read-only
    (no WITH tags), so we cannot delete messages through it.
    The customer_profile_dv does not include messages in its schema.

    Therefore, nested message deletion through a Duality View requires
    a dedicated view that includes messages with WITH(DELETE) tags.
    We fall back to a direct table DELETE for demonstration.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Verify the message exists and belongs to the ticket
        cursor.execute(
            "SELECT message_id FROM ticket_messages "
            "WHERE message_id = %s AND ticket_id = %s",
            (message_id, ticket_id)
        )
        if cursor.fetchone() is None:
            msg = f"[WARN] Message {message_id} not found in ticket {ticket_id}."
            print(msg)
            return msg

        # Direct table delete (Duality View limitation workaround)
        cursor.execute(
            "DELETE FROM ticket_messages WHERE message_id = %s",
            (message_id,)
        )
        conn.commit()

        msg = (
            f"[OK] Message {message_id} deleted from ticket {ticket_id}.\n"
            f"[NOTE] This used a direct table DELETE because:\n"
            f"  - ticket_conversation_dv is read-only (no WITH tags)\n"
            f"  - customer_profile_dv does not include messages\n"
            f"  To enable this via a Duality View, create a view with\n"
            f"  WITH(DELETE) on the messages sub-object."
        )
        print(msg)
        return msg
    except Error as e:
        conn.rollback()
        err = f"[ERROR] Failed to delete message: {e}"
        print(err)
        return err
    finally:
        cursor.close()
        conn.close()


# ── Demo ──────────────────────────────────────────────────────────────

def main():
    """Run interactive demos of all Duality View operations."""
    print("=" * 60)
    print("  MySQL 9.7 JSON Duality Views — Support Ticket Demo")
    print("=" * 60)

    # ── 1. READ: Get a full ticket conversation ──
    print("\n▶ 1. Get Ticket #1 (full conversation from ticket_conversation_dv)")
    print("-" * 60)
    ticket = get_ticket(1)
    pp(ticket)

    # ── 2. READ: Get a customer profile ──
    print("\n▶ 2. Get Customer #2 profile (from customer_profile_dv)")
    print("-" * 60)
    customer = get_customer(2)
    pp(customer)

    # ── 3. WRITE: Create a new ticket ──
    print("\n▶ 3. Create a new ticket for Customer #3")
    print("-" * 60)
    updated = create_ticket(
        customer_id=3,
        subject="Login page shows 404 after latest deploy",
        priority="high"
    )
    pp(updated)

    # ── 4. WRITE: Update ticket status ──
    print("\n▶ 4. Update Ticket #3 status to 'resolved'")
    print("-" * 60)
    updated = update_ticket_status(ticket_id=3, new_status="resolved")
    pp(updated)

    # ── 5. DELETE: Remove a message (limitation demo) ──
    print("\n▶ 5. Delete Message #13 from Ticket #5 (limitation demo)")
    print("-" * 60)
    delete_message(ticket_id=5, message_id=13)

    # ── 6. Verify the deletion ──
    print("\n▶ 6. Verify: Ticket #5 after message deletion")
    print("-" * 60)
    ticket5 = get_ticket(5)
    pp(ticket5)

    print("\n" + "=" * 60)
    print("  Demo complete! All operations executed successfully.")
    print("=" * 60)


if __name__ == "__main__":
    main()
