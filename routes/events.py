from flask import Blueprint, render_template, request

from database.db import get_db


events_bp = Blueprint("events", __name__)


@events_bp.route("/events")
def events():

    search = request.args.get("search", "").strip()
    severity = request.args.get("severity", "").strip().upper()
    event_type = request.args.get("event_type", "").strip().upper()

    connection = get_db()

    query = """
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
        WHERE 1 = 1
    """

    params = []

    if search:

        query += """
            AND (
                source_ip LIKE ?
                OR destination_ip LIKE ?
                OR event_type LIKE ?
                OR message LIKE ?
            )
        """

        search_value = f"%{search}%"

        params.extend([
            search_value,
            search_value,
            search_value,
            search_value
        ])

    if severity:

        query += """
            AND severity = ?
        """

        params.append(severity)

    if event_type:

        query += """
            AND event_type = ?
        """

        params.append(event_type)

    query += """
        ORDER BY id DESC
    """

    events = connection.execute(
        query,
        params
    ).fetchall()

    event_types = connection.execute(
        """
        SELECT DISTINCT event_type
        FROM events
        ORDER BY event_type
        """
    ).fetchall()

    connection.close()

    return render_template(
        "events.html",
        events=events,
        event_types=event_types,
        search=search,
        selected_severity=severity,
        selected_event_type=event_type
    )