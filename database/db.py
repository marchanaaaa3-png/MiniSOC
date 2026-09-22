import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from flask import current_app
from werkzeug.security import generate_password_hash


# ============================================================
# DEFAULT DETECTOR RULES
# ============================================================

DEFAULT_RULES = [
    (
        "BRUTE_FORCE",
        "Repeated Authentication Failures",
        "Detects repeated failed authentication attempts from the same source IP.",
        "HIGH",
    ),
    (
        "PORT_SCAN",
        "Port Scanning Activity",
        "Detects network reconnaissance and port scanning activity.",
        "MEDIUM",
    ),
    (
        "MALWARE",
        "Malware Detection",
        "Detects events identified as malware activity.",
        "CRITICAL",
    ),
    (
        "SUSPICIOUS_LOGIN",
        "Suspicious Login",
        "Detects suspicious authentication activity.",
        "HIGH",
    ),
    (
        "PRIV_ESC",
        "Privilege Escalation",
        "Detects possible privilege escalation activity.",
        "CRITICAL",
    ),
]


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_db():
    """Return a SQLite database connection."""

    db_path = Path(
        current_app.config["DATABASE_PATH"]
    )

    db_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = sqlite3.connect(
        db_path
    )

    connection.row_factory = sqlite3.Row

    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    return connection


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def init_db(app):
    """Create database tables and initial application data."""

    db_path = Path(
        app.config["DATABASE_PATH"]
    )

    db_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = sqlite3.connect(
        db_path
    )

    connection.row_factory = sqlite3.Row

    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    # --------------------------------------------------------
    # Load schema
    # --------------------------------------------------------

    schema_path = (
        Path(app.root_path)
        / "database"
        / "schema.sql"
    )

    schema = schema_path.read_text(
        encoding="utf-8"
    )

    connection.executescript(
        schema
    )

    # --------------------------------------------------------
    # Create default administrator account
    # --------------------------------------------------------

    user_count = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM users
        """
    ).fetchone()["count"]

    if user_count == 0:

        password_hash = generate_password_hash(
            "Admin@12345"
        )

        connection.execute(
            """
            INSERT INTO users
            (
                username,
                password_hash,
                role,
                created_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                "admin",
                password_hash,
                "Administrator",
                utc_now()
            )
        )

    # --------------------------------------------------------
    # Seed detector rules
    # --------------------------------------------------------

    rule_count = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM detector_rules
        """
    ).fetchone()["count"]

    if rule_count == 0:

        connection.executemany(
            """
            INSERT INTO detector_rules
            (
                rule_id,
                name,
                description,
                severity,
                enabled
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                (
                    rule_id,
                    name,
                    description,
                    severity,
                    1
                )
                for (
                    rule_id,
                    name,
                    description,
                    severity
                ) in DEFAULT_RULES
            ]
        )

    # --------------------------------------------------------
    # Seed safe demonstration threat intelligence
    # --------------------------------------------------------

    ti_count = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM threat_intelligence
        """
    ).fetchone()["count"]

    if ti_count == 0:

        demo_indicators = [

            (
                "203.0.113.44",
                "IPv4",
                88,
                "Brute Force",
                "MiniSOC Demo Feed",
                "Reserved documentation IP used for safe local simulation."
            ),

            (
                "198.51.100.23",
                "IPv4",
                91,
                "Malware Infrastructure",
                "MiniSOC Demo Feed",
                "Reserved documentation IP used for safe local simulation."
            ),

            (
                "192.0.2.55",
                "IPv4",
                72,
                "Suspicious Activity",
                "MiniSOC Demo Feed",
                "Reserved documentation IP used for safe local simulation."
            )
        ]

        connection.executemany(
            """
            INSERT INTO threat_intelligence
            (
                indicator,
                indicator_type,
                confidence,
                category,
                source,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            demo_indicators
        )

    connection.commit()

    connection.close()


# ============================================================
# TIME
# ============================================================

def utc_now():
    """Return current UTC timestamp."""

    return datetime.now(
        timezone.utc
    ).strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )


# ============================================================
# QUERY HELPERS
# ============================================================

def query(sql, params=()):
    """Execute a SELECT query."""

    connection = get_db()

    rows = connection.execute(
        sql,
        params
    ).fetchall()

    connection.close()

    return rows


def execute(sql, params=()):
    """Execute INSERT, UPDATE or DELETE."""

    connection = get_db()

    cursor = connection.execute(
        sql,
        params
    )

    connection.commit()

    last_id = cursor.lastrowid

    connection.close()

    return last_id