-- ============================================================
-- JSON Duality Views — MySQL 9.7
-- ============================================================

USE support_db;

-- -----------------------------------------------------------
-- View 1: ticket_conversation_dv (READ-ONLY)
-- Purpose: Full ticket document with customer info and all
--          messages nested as a JSON array.
-- No WITH tags → entire view is read-only.
-- NOTE: '_id' key is reserved for the root object's PK only.
--       Nested objects use 'id' or other key names.
-- -----------------------------------------------------------
CREATE OR REPLACE JSON DUALITY VIEW ticket_conversation_dv AS
SELECT JSON_DUALITY_OBJECT(
    '_id':        t.ticket_id,
    'subject':    t.subject,
    'status':     t.status,
    'priority':   t.priority,
    'createdAt':  t.created_at,
    'customer':   (SELECT JSON_DUALITY_OBJECT(
                      'customerId': c.customer_id,
                      'name':       c.name,
                      'email':      c.email,
                      'tier':       c.tier
                  )
                  FROM customers c
                  WHERE c.customer_id = t.customer_id),
    'messages':   (SELECT JSON_ARRAYAGG(JSON_DUALITY_OBJECT(
                      'messageId':  m.message_id,
                      'sender':     m.sender,
                      'body':       m.body,
                      'sentAt':     m.created_at
                  ))
                  FROM ticket_messages m
                  WHERE m.ticket_id = t.ticket_id)
)
FROM support_tickets t;

-- -----------------------------------------------------------
-- View 2: customer_profile_dv (UPDATABLE)
-- Purpose: Customer document with nested ticket summaries.
-- WITH(INSERT, UPDATE, DELETE) on both root and nested objects
-- so DML operations work through the view.
-- -----------------------------------------------------------
CREATE OR REPLACE JSON DUALITY VIEW customer_profile_dv AS
SELECT JSON_DUALITY_OBJECT(
    WITH(INSERT, UPDATE, DELETE)
    '_id':     c.customer_id,
    'name':    c.name,
    'email':   c.email,
    'tier':    c.tier,
    'tickets': (SELECT JSON_ARRAYAGG(JSON_DUALITY_OBJECT(
                    WITH(INSERT, UPDATE, DELETE)
                    'ticketId':  t.ticket_id,
                    'subject':   t.subject,
                    'status':    t.status,
                    'priority':  t.priority,
                    'createdAt': t.created_at
                ))
               FROM support_tickets t
               WHERE t.customer_id = c.customer_id)
)
FROM customers c;
