from flask import Blueprint, flash, redirect, render_template, url_for

from database.db import get_db


alerts_bp = Blueprint("alerts", __name__)


@alerts_bp.route("/alerts")
def alerts():

    connection = get_db()

    alerts = connection.execute(
        """
        SELECT
            id,
            event_id,
            created_at,
            rule_id,
            title,
            severity,
            source_ip,
            destination_ip,
            description,
            status
        FROM alerts
        ORDER BY id DESC
        """
    ).fetchall()

    total_alerts = len(alerts)

    open_alerts = sum(
        1
        for alert in alerts
        if alert["status"] == "OPEN"
    )

    critical_alerts = sum(
        1
        for alert in alerts
        if alert["severity"] == "CRITICAL"
    )

    closed_alerts = sum(
        1
        for alert in alerts
        if alert["status"] == "CLOSED"
    )

    connection.close()

    return render_template(
        "alerts.html",
        alerts=alerts,
        total_alerts=total_alerts,
        open_alerts=open_alerts,
        critical_alerts=critical_alerts,
        closed_alerts=closed_alerts
    )


@alerts_bp.route(
    "/alerts/<int:alert_id>/close",
    methods=["POST"]
)
def close_alert(alert_id):

    connection = get_db()

    alert = connection.execute(
        """
        SELECT id
        FROM alerts
        WHERE id = ?
        """,
        (alert_id,)
    ).fetchone()

    if alert is None:

        connection.close()

        flash(
            "Alert not found.",
            "error"
        )

        return redirect(
            url_for("alerts.alerts")
        )

    connection.execute(
        """
        UPDATE alerts
        SET status = 'CLOSED'
        WHERE id = ?
        """,
        (alert_id,)
    )

    connection.commit()
    connection.close()

    flash(
        "Alert closed successfully.",
        "success"
    )

    return redirect(
        url_for("alerts.alerts")
    )