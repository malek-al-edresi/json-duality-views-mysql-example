-- ============================================================
-- Seed Data — Realistic Sample Records
-- ============================================================

USE support_db;

-- -----------------------------------------------------------
-- Customers
-- -----------------------------------------------------------
INSERT INTO customers (name, email, tier) VALUES
  ('Alice Johnson',   'alice@techcorp.io',     'enterprise'),
  ('Bob Martinez',    'bob.m@startuplab.com',  'pro'),
  ('Carol Chen',      'carol.chen@indie.dev',  'free');

-- -----------------------------------------------------------
-- Support Tickets
-- -----------------------------------------------------------
INSERT INTO support_tickets (customer_id, subject, status, priority, created_at) VALUES
  (1, 'Cannot connect to production database',       'open',        'critical', '2025-06-01 09:15:00'),
  (1, 'Need help configuring SSO integration',        'in_progress', 'high',     '2025-06-02 14:30:00'),
  (2, 'Billing discrepancy on last invoice',          'open',        'medium',   '2025-06-03 11:00:00'),
  (2, 'Feature request: dark mode for dashboard',     'resolved',    'low',      '2025-05-20 16:45:00'),
  (3, 'App crashes when uploading large CSV files',   'open',        'high',     '2025-06-04 08:20:00');

-- -----------------------------------------------------------
-- Ticket Messages (10+ messages across tickets)
-- -----------------------------------------------------------
INSERT INTO ticket_messages (ticket_id, sender, body, created_at) VALUES
  -- Ticket 1: Production DB issue
  (1, 'customer', 'Our production database stopped responding at 9 AM. All services are down. Please help urgently!', '2025-06-01 09:15:00'),
  (1, 'agent',    'I can see elevated error rates on your cluster. Checking the connection pool settings now.', '2025-06-01 09:25:00'),
  (1, 'agent',    'Found the issue — max_connections was hit. I am increasing it to 500. Please try reconnecting.', '2025-06-01 09:40:00'),
  (1, 'customer', 'Still getting timeouts after the change. Could it be a network ACL issue?', '2025-06-01 10:05:00'),

  -- Ticket 2: SSO integration
  (2, 'customer', 'We are trying to set up SAML-based SSO with Okta but the callback URL is rejected.', '2025-06-02 14:30:00'),
  (2, 'agent',    'Please ensure the callback URL uses HTTPS and matches the pattern registered in your Okta app.', '2025-06-02 15:00:00'),

  -- Ticket 3: Billing
  (3, 'customer', 'My June invoice shows $450 but I only used the Pro plan at $29/month. Something is wrong.', '2025-06-03 11:00:00'),
  (3, 'agent',    'Looking into your billing records now. Could you share your invoice number?', '2025-06-03 11:30:00'),
  (3, 'customer', 'Invoice number is INV-2025-0603. The charge appeared on June 1st.', '2025-06-03 11:45:00'),

  -- Ticket 4: Feature request
  (4, 'customer', 'It would be great to have a dark mode option. The white background is too bright at night.', '2025-05-20 16:45:00'),
  (4, 'agent',    'Great suggestion! We have added this to our roadmap for Q3 2025. Thanks for the feedback!', '2025-05-21 10:00:00'),

  -- Ticket 5: CSV crash
  (5, 'customer', 'When I upload a CSV file larger than 50MB the app crashes with a 502 error.', '2025-06-04 08:20:00'),
  (5, 'system',   'Automatic crash report generated. Stack trace attached: OutOfMemoryError at FileUploadHandler.java:142.', '2025-06-04 08:21:00');
