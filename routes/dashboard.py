from flask import Blueprint, jsonify, render_template

from database.db import get_db


dashboard_bp = Blueprint(
    "dashboard",
    __name__
)


@dashboard_bp.route("/")
@dashboard_bp.route("/dashboard")
def dashboard():

    connection = get_db()

    # --------------------------------------------------------
    # Event statistics
    # --------------------------------------------------------

    event_stats = connection.execute(
        """
        SELECT
            COUNT(*) AS total_events,

            SUM(
                CASE
                    WHEN severity = 'CRITICAL'
                    THEN 1
                    ELSE 0
                END
            ) AS critical_events,

            SUM(
                CASE
                    WHEN severity = 'HIGH'
                    THEN 1
                    ELSE 0
                END
            ) AS high_events,

            SUM(
                CASE
                    WHEN severity = 'MEDIUM'
                    THEN 1
                    ELSE 0
                END
            ) AS medium_events,

            SUM(
                CASE
                    WHEN severity = 'LOW'
                    THEN 1
                    ELSE 0
                END
            ) AS low_events,

            COUNT(DISTINCT source_ip) AS source_ips,

            SUM(
                CASE
                    WHEN status = 'ANALYZED'
                    THEN 1
                    ELSE 0
                END
            ) AS analyzed_events

        FROM events
        """
    ).fetchone()

    # --------------------------------------------------------
    # Alert statistics
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Recent events
    # --------------------------------------------------------

    recent_events = connection.execute(
        """
        SELECT
            id,
            timestamp,
            source_ip,
            destination_ip,
            event_type,
            severity,
            message,
            status
        FROM events
        ORDER BY id DESC
        LIMIT 10
        """
    ).fetchall()

    # --------------------------------------------------------
    # Recent alerts
    # --------------------------------------------------------

    recent_alerts = connection.execute(
        """
        SELECT
            id,
            created_at,
            rule_id,
            title,
            severity,
            source_ip,
            destination_ip,
            status
        FROM alerts
        ORDER BY id DESC
        LIMIT 5
        """
    ).fetchall()

    connection.close()

    # --------------------------------------------------------
    # Prepare dashboard statistics
    # --------------------------------------------------------

    stats = {
        "total_events": event_stats["total_events"] or 0,
        "critical_events": event_stats["critical_events"] or 0,
        "high_events": event_stats["high_events"] or 0,
        "medium_events": event_stats["medium_events"] or 0,
        "low_events": event_stats["low_events"] or 0,
        "source_ips": event_stats["source_ips"] or 0,
        "analyzed_events": event_stats["analyzed_events"] or 0,

        "total_alerts": alert_stats["total_alerts"] or 0,
        "open_alerts": alert_stats["open_alerts"] or 0
    }

    return render_template(
        "dashboard.html",
        stats=stats,
        recent_events=recent_events,
        recent_alerts=recent_alerts
    )


@dashboard_bp.route("/api/dashboard-data")
def dashboard_data():

    connection = get_db()

    # --------------------------------------------------------
    # Live event statistics
    # --------------------------------------------------------

    event_stats = connection.execute(
        """
        SELECT
            COUNT(*) AS total_events,

            SUM(
                CASE
                    WHEN severity = 'CRITICAL'
                    THEN 1
                    ELSE 0
                END
            ) AS critical_events,

            SUM(
                CASE
                    WHEN severity = 'HIGH'
                    THEN 1
                    ELSE 0
                END
            ) AS high_events,

            SUM(
                CASE
                    WHEN severity = 'MEDIUM'
                    THEN 1
                    ELSE 0
                END
            ) AS medium_events,

            SUM(
                CASE
                    WHEN severity = 'LOW'
                    THEN 1
                    ELSE 0
                END
            ) AS low_events,

            COUNT(DISTINCT source_ip) AS source_ips,

            SUM(
                CASE
                    WHEN status = 'ANALYZED'
                    THEN 1
                    ELSE 0
                END
            ) AS analyzed_events

        FROM events
        """
    ).fetchone()

    # --------------------------------------------------------
    # Live alert statistics
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Recent events
    # --------------------------------------------------------

    recent_events = connection.execute(
        """
        SELECT
            timestamp,
            source_ip,
            destination_ip,
            event_type,
            severity,
            status
        FROM events
        ORDER BY id DESC
        LIMIT 10
        """
    ).fetchall()

    connection.close()

    # --------------------------------------------------------
    # JSON response
    # --------------------------------------------------------

    data = {
        "total_events": event_stats["total_events"] or 0,
        "critical_events": event_stats["critical_events"] or 0,
        "high_events": event_stats["high_events"] or 0,
        "medium_events": event_stats["medium_events"] or 0,
        "low_events": event_stats["low_events"] or 0,
        "source_ips": event_stats["source_ips"] or 0,
        "analyzed_events": event_stats["analyzed_events"] or 0,

        "total_alerts": alert_stats["total_alerts"] or 0,
        "open_alerts": alert_stats["open_alerts"] or 0,

        "recent_events": [
            dict(event)
            for event in recent_events
        ]
    }

    return jsonify(data)