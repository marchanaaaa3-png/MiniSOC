from flask import Blueprint, render_template

from database.db import get_db


reports_bp = Blueprint(
    "reports",
    __name__
)


@reports_bp.route("/reports")
def reports():

    connection = get_db()

    # ========================================================
    # OVERVIEW STATISTICS
    # ========================================================

    event_stats = connection.execute(
        """
        SELECT
            COUNT(*) AS total_events,
            COUNT(DISTINCT source_ip) AS source_ips
        FROM events
        """
    ).fetchone()

    alert_stats = connection.execute(
        """
        SELECT
            COUNT(*) AS total_alerts,
            SUM(
                CASE
                    WHEN status = 'OPEN'
                    THEN 1
                    ELSE 0
                END
            ) AS open_alerts
        FROM alerts
        """
    ).fetchone()

    # ========================================================
    # EVENT SEVERITY
    # ========================================================

    severity_rows = connection.execute(
        """
        SELECT
            severity,
            COUNT(*) AS count
        FROM events
        GROUP BY severity
        ORDER BY count DESC
        """
    ).fetchall()

    total_events = event_stats["total_events"] or 0

    severity_stats = []

    for row in severity_rows:

        count = row["count"] or 0

        percentage = (
            (count / total_events) * 100
            if total_events > 0
            else 0
        )

        severity_stats.append(
            {
                "severity": row["severity"],
                "count": count,
                "percentage": round(percentage, 1)
            }
        )

    # ========================================================
    # ALERT SEVERITY
    # ========================================================

    alert_severity_rows = connection.execute(
        """
        SELECT
            severity,
            COUNT(*) AS count
        FROM alerts
        GROUP BY severity
        ORDER BY count DESC
        """
    ).fetchall()

    total_alerts = alert_stats["total_alerts"] or 0

    alert_severity_stats = []

    for row in alert_severity_rows:

        count = row["count"] or 0

        percentage = (
            (count / total_alerts) * 100
            if total_alerts > 0
            else 0
        )

        alert_severity_stats.append(
            {
                "severity": row["severity"],
                "count": count,
                "percentage": round(percentage, 1)
            }
        )

    # ========================================================
    # EVENT TYPES
    # ========================================================

    event_type_stats = connection.execute(
        """
        SELECT
            event_type,
            COUNT(*) AS count
        FROM events
        GROUP BY event_type
        ORDER BY count DESC
        """
    ).fetchall()

    # ========================================================
    # TOP SOURCE IPS
    # ========================================================

    top_sources = connection.execute(
        """
        SELECT
            source_ip,
            COUNT(*) AS count
        FROM events
        GROUP BY source_ip
        ORDER BY count DESC
        LIMIT 10
        """
    ).fetchall()

    # ========================================================
    # DETECTOR RULE ACTIVITY
    # ========================================================

    rule_stats = connection.execute(
        """
        SELECT
            rule_id,
            COUNT(*) AS count
        FROM alerts
        GROUP BY rule_id
        ORDER BY count DESC
        """
    ).fetchall()

    connection.close()

    # ========================================================
    # RENDER REPORT
    # ========================================================

    return render_template(
        "reports.html",

        total_events=total_events,

        total_alerts=total_alerts,

        open_alerts=(
            alert_stats["open_alerts"] or 0
        ),

        source_ips=(
            event_stats["source_ips"] or 0
        ),

        severity_stats=severity_stats,

        alert_severity_stats=alert_severity_stats,

        event_type_stats=event_type_stats,

        top_sources=top_sources,

        rule_stats=rule_stats
    )