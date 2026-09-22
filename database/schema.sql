-- ============================================================
-- MiniSOC Database Schema
-- ============================================================


-- ============================================================
-- USERS
-- ============================================================

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'Analyst',
    created_at TEXT NOT NULL
);


-- ============================================================
-- SECURITY EVENTS
-- ============================================================

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    source_ip TEXT NOT NULL,
    destination_ip TEXT NOT NULL,
    event_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    message TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'NEW'
);


-- ============================================================
-- ALERTS
-- ============================================================

CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER,
    created_at TEXT NOT NULL,
    rule_id TEXT NOT NULL,
    title TEXT NOT NULL,
    severity TEXT NOT NULL,
    source_ip TEXT NOT NULL,
    destination_ip TEXT NOT NULL,
    description TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'OPEN',

    FOREIGN KEY (event_id)
        REFERENCES events(id)
        ON DELETE CASCADE
);


-- ============================================================
-- DETECTOR RULES
-- ============================================================

CREATE TABLE IF NOT EXISTS detector_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    severity TEXT NOT NULL,
    enabled INTEGER NOT NULL DEFAULT 1
);


-- ============================================================
-- THREAT INTELLIGENCE
-- ============================================================

CREATE TABLE IF NOT EXISTS threat_intelligence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    indicator TEXT NOT NULL,
    indicator_type TEXT NOT NULL,
    confidence INTEGER NOT NULL,
    category TEXT NOT NULL,
    source TEXT NOT NULL,
    notes TEXT NOT NULL
);