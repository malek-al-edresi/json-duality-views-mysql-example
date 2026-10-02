-- ============================================================
-- Customer Support Ticket System — Relational Schema
-- MySQL 9.7 with JSON Duality Views
-- ============================================================

USE support_db;

-- -----------------------------------------------------------
-- 1. Customers
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS customers (
    customer_id   INT           NOT NULL AUTO_INCREMENT,
    name          VARCHAR(120)  NOT NULL,
    email         VARCHAR(255)  NOT NULL UNIQUE,
    tier          ENUM('free','pro','enterprise') NOT NULL DEFAULT 'free',
    PRIMARY KEY (customer_id)
) ENGINE=InnoDB;

-- -----------------------------------------------------------
-- 2. Support Tickets
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS support_tickets (
    ticket_id     INT           NOT NULL AUTO_INCREMENT,
    customer_id   INT           NOT NULL,
    subject       VARCHAR(300)  NOT NULL,
    status        ENUM('open','in_progress','resolved','closed') NOT NULL DEFAULT 'open',
    priority      ENUM('low','medium','high','critical')        NOT NULL DEFAULT 'medium',
    created_at    TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (ticket_id),
    CONSTRAINT fk_ticket_customer
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        ON DELETE CASCADE
) ENGINE=InnoDB;

-- -----------------------------------------------------------
-- 3. Ticket Messages
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS ticket_messages (
    message_id    INT           NOT NULL AUTO_INCREMENT,
    ticket_id     INT           NOT NULL,
    sender        ENUM('customer','agent','system') NOT NULL,
    body          TEXT          NOT NULL,
    created_at    TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (message_id),
    CONSTRAINT fk_message_ticket
        FOREIGN KEY (ticket_id) REFERENCES support_tickets(ticket_id)
        ON DELETE CASCADE
) ENGINE=InnoDB;
