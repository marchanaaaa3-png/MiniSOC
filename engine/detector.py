from database.db import get_db


# ============================================================
# MiniSOC Detection Engine
# ============================================================

def detect_event(event_id):
    """
    Analyze one event against all enabled detector rules.

    Returns a list containing the names of rules that triggered.
    """

    connection = get_db()

    # --------------------------------------------------------
    # Get the event
    # --------------------------------------------------------

    event = connection.execute(
        """
        SELECT *
        FROM events
        WHERE id = ?
        """,
        (event_id,),
    ).fetchone()

    if event is None:
        connection.close()
        return []

    event_type = event["event_type"].upper()

    # --------------------------------------------------------
    # Get enabled detector rules
    # --------------------------------------------------------

    rules = connection.execute(
        """
        SELECT *
        FROM detector_rules
        WHERE enabled = 1
        ORDER BY id
        """
    ).fetchall()

    triggered_rules = []

    # --------------------------------------------------------
    # Check every enabled rule
    # --------------------------------------------------------

    for rule in rules:

        rule_id = rule["rule_id"]

        matched = False

        # ----------------------------------------------------
        # Direct event-type rules
        # ----------------------------------------------------

        if rule_id == event_type:
            matched = True

        # ----------------------------------------------------
        # Brute-force detection
        #
        # Trigger after multiple authentication failures
        # from the same source IP within 10 minutes.
        # ----------------------------------------------------

        elif rule_id == "BRUTE_FORCE":

            if event_type in {
                "AUTH_FAILURE",
                "BRUTE_FORCE",
            }:

                recent_failures = connection.execute(
                    """
                    SELECT COUNT(*) AS count
                    FROM events
                    WHERE source_ip = ?
                      AND event_type IN (
                          'AUTH_FAILURE',
                          'BRUTE_FORCE'
                      )
                      AND id != ?
                      AND timestamp >= ?
                    """,
                    (
                        event["source_ip"],
                        event_id,
                        _ten_minutes_ago(),
                    ),
                ).fetchone()["count"]

                # Current event + at least two previous failures
                if recent_failures >= 2:
                    matched = True

        # ----------------------------------------------------
        # Create alert if rule matched
        # ----------------------------------------------------

        if matched:

            existing_alert = connection.execute(
                """
                SELECT id
                FROM alerts
                WHERE event_id = ?
                  AND rule_id = ?
                """,
                (
                    event_id,
                    rule_id,
                ),
            ).fetchone()

            # Prevent duplicate alerts
            if existing_alert is None:

                description = (
                    f"{rule['name']} detected activity from "
                    f"{event['source_ip']} to "
                    f"{event['destination_ip']}. "
                    f"Event: {event['message']}"
                )

                connection.execute(
                    """
                    INSERT INTO alerts
                    (
                        event_id,
                        created_at,
                        rule_id,
                        title,
                        severity,
                        source_ip,
                        destination_ip,
                        description,
                        status
                    )
                    VALUES
                    (
                        ?,
                        datetime('now'),
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        'OPEN'
                    )
                    """,
                    (
                        event_id,
                        rule_id,
                        rule["name"],
                        rule["severity"],
                        event["source_ip"],
                        event["destination_ip"],
                        description,
                    ),
                )

                triggered_rules.append(rule["name"])

    # --------------------------------------------------------
    # Mark event as analyzed
    # --------------------------------------------------------

    connection.execute(
        """
        UPDATE events
        SET status = 'ANALYZED'
        WHERE id = ?
        """,
        (event_id,),
    )

    connection.commit()
    connection.close()

    return triggered_rules


# ============================================================
# Helper: Timestamp 10 Minutes Ago
# ============================================================

def _ten_minutes_ago():
    """
    Return a SQLite-compatible UTC timestamp representing
    approximately ten minutes ago.

    We use the same timestamp format stored by the application.
    """

    from datetime import datetime, timedelta, timezone

    timestamp = datetime.now(timezone.utc) - timedelta(minutes=10)

    return timestamp.strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )