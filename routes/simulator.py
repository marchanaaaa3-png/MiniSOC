from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for
)

from database.db import get_db, utc_now
from engine.detector import detect_event


simulator_bp = Blueprint(
    "simulator",
    __name__
)


# ============================================================
# EVENT SCENARIOS
# ============================================================

SCENARIOS = {

    "normal": {
        "source_ip": "10.0.0.24",
        "destination_ip": "10.0.0.10",
        "event_type": "NORMAL",
        "severity": "LOW",
        "message": "Normal network activity detected."
    },

    "auth_failure": {
        "source_ip": "203.0.113.44",
        "destination_ip": "10.0.0.10",
        "event_type": "AUTH_FAILURE",
        "severity": "MEDIUM",
        "message": "Failed authentication attempt detected."
    },

    "port_scan": {
        "source_ip": "198.51.100.23",
        "destination_ip": "10.0.0.10",
        "event_type": "PORT_SCAN",
        "severity": "MEDIUM",
        "message": "Network reconnaissance and port scanning activity detected."
    },

    "malware": {
        "source_ip": "198.51.100.23",
        "destination_ip": "10.0.0.20",
        "event_type": "MALWARE",
        "severity": "CRITICAL",
        "message": "Potential malware activity detected."
    },

    "suspicious_login": {
        "source_ip": "192.0.2.55",
        "destination_ip": "10.0.0.10",
        "event_type": "SUSPICIOUS_LOGIN",
        "severity": "HIGH",
        "message": "Suspicious login activity detected."
    },

    "priv_esc": {
        "source_ip": "10.0.0.24",
        "destination_ip": "10.0.0.10",
        "event_type": "PRIV_ESC",
        "severity": "CRITICAL",
        "message": "Possible privilege escalation activity detected."
    }
}


# ============================================================
# LIVE INDIAN TRAFFIC
# ============================================================

LIVE_TRAFFIC = [

    {
        "source_ip": "203.0.113.44",
        "destination_ip": "10.0.0.10",
        "event_type": "AUTH_FAILURE",
        "severity": "MEDIUM",
        "message": "Authentication failure observed from Mumbai."
    },

    {
        "source_ip": "198.51.100.23",
        "destination_ip": "10.0.0.10",
        "event_type": "PORT_SCAN",
        "severity": "MEDIUM",
        "message": "Port scanning activity observed from New Delhi."
    },

    {
        "source_ip": "192.0.2.55",
        "destination_ip": "10.0.0.10",
        "event_type": "SUSPICIOUS_LOGIN",
        "severity": "HIGH",
        "message": "Suspicious login activity observed from Bengaluru."
    },

    {
        "source_ip": "10.0.0.30",
        "destination_ip": "10.0.0.10",
        "event_type": "AUTH_FAILURE",
        "severity": "MEDIUM",
        "message": "Authentication anomaly observed from Chennai."
    },

    {
        "source_ip": "10.0.0.31",
        "destination_ip": "10.0.0.10",
        "event_type": "PORT_SCAN",
        "severity": "MEDIUM",
        "message": "Network reconnaissance observed from Pune."
    },

    {
        "source_ip": "10.0.0.32",
        "destination_ip": "10.0.0.20",
        "event_type": "MALWARE",
        "severity": "CRITICAL",
        "message": "Potential malware activity observed from Kolkata."
    },

    {
        "source_ip": "10.0.0.33",
        "destination_ip": "10.0.0.10",
        "event_type": "SUSPICIOUS_LOGIN",
        "severity": "HIGH",
        "message": "Suspicious authentication activity observed from Ahmedabad."
    },

    {
        "source_ip": "10.0.0.24",
        "destination_ip": "10.0.0.10",
        "event_type": "PRIV_ESC",
        "severity": "CRITICAL",
        "message": "Possible privilege escalation detected in Hyderabad."
    }

]


# ============================================================
# INSERT EVENT
# ============================================================

def create_event(event):

    connection = get_db()

    cursor = connection.execute(
        """
        INSERT INTO events
        (
            timestamp,
            source_ip,
            destination_ip,
            event_type,
            severity,
            message,
            status
        )
        VALUES
        (
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            'NEW'
        )
        """,
        (
            utc_now(),
            event["source_ip"],
            event["destination_ip"],
            event["event_type"],
            event["severity"],
            event["message"]
        )
    )

    event_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return event_id


# ============================================================
# EVENT SIMULATOR PAGE
# ============================================================

@simulator_bp.route(
    "/simulator",
    methods=["GET", "POST"]
)
def simulator():

    if request.method == "POST":

        source_ip = request.form.get(
            "source_ip",
            ""
        ).strip()

        destination_ip = request.form.get(
            "destination_ip",
            ""
        ).strip()

        event_type = request.form.get(
            "event_type",
            ""
        ).strip().upper()

        severity = request.form.get(
            "severity",
            ""
        ).strip().upper()

        message = request.form.get(
            "message",
            ""
        ).strip()


        if not all([
            source_ip,
            destination_ip,
            event_type,
            severity,
            message
        ]):

            flash(
                "All event fields are required.",
                "error"
            )

            return render_template(
                "simulator.html",
                scenarios=SCENARIOS
            )


        valid_severities = {
            "LOW",
            "MEDIUM",
            "HIGH",
            "CRITICAL"
        }


        if severity not in valid_severities:

            flash(
                "Invalid severity level.",
                "error"
            )

            return render_template(
                "simulator.html",
                scenarios=SCENARIOS
            )


        event_id = create_event({

            "source_ip": source_ip,

            "destination_ip": destination_ip,

            "event_type": event_type,

            "severity": severity,

            "message": message

        })


        triggered_rules = detect_event(event_id)
        detect_event(event_id)


        if triggered_rules:

            flash(
                f"Event #{event_id} generated. "
                f"{len(triggered_rules)} detector rule(s) triggered.",
                "success"
            )

        else:

            flash(
                f"Event #{event_id} generated successfully. "
                "No detector rules triggered.",
                "success"
            )


        return redirect(
            url_for(
                "simulator.simulator"
            )
        )


    return render_template(
        "simulator.html",
        scenarios=SCENARIOS
    )


# ============================================================
# LIVE TRAFFIC GENERATOR
# ============================================================

@simulator_bp.route(
    "/simulator/live-traffic",
    methods=["POST"]
)
def live_traffic():

    created_events = 0

    triggered_alerts = 0


    for event in LIVE_TRAFFIC:

        event_id = create_event(event)

    triggered_rules = detect_event(event_id)

    created_events += 1

    triggered_alerts += len(
            triggered_rules
        )


    flash(
        f"Live Indian traffic generated: "
        f"{created_events} events, "
        f"{triggered_alerts} detector alert(s).",
        "success"
    )


    return redirect(
        url_for(
            "simulator.simulator"
        )
    )