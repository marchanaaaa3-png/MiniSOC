from flask import Blueprint, flash, redirect, render_template, request, url_for
from werkzeug.security import generate_password_hash

from database.db import get_db


settings_bp = Blueprint(
    "settings",
    __name__
)


@settings_bp.route("/settings", methods=["GET", "POST"])
def settings():

    # --------------------------------------------------------
    # Create new user
    # --------------------------------------------------------

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        role = request.form.get(
            "role",
            "SOC Analyst"
        ).strip()

        if not username or not password:

            flash(
                "Username and password are required.",
                "error"
            )

            return redirect(
                url_for("settings.settings")
            )

        if len(username) < 3:

            flash(
                "Username must contain at least 3 characters.",
                "error"
            )

            return redirect(
                url_for("settings.settings")
            )

        if len(password) < 8:

            flash(
                "Password must contain at least 8 characters.",
                "error"
            )

            return redirect(
                url_for("settings.settings")
            )

        if role not in {
            "Administrator",
            "SOC Analyst"
        }:

            role = "SOC Analyst"

        connection = get_db()

        existing_user = connection.execute(
            """
            SELECT id
            FROM users
            WHERE username = ?
            """,
            (username,)
        ).fetchone()

        if existing_user:

            connection.close()

            flash(
                "Username already exists.",
                "error"
            )

            return redirect(
                url_for("settings.settings")
            )

        password_hash = generate_password_hash(
            password
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
            VALUES (?, ?, ?, datetime('now'))
            """,
            (
                username,
                password_hash,
                role
            )
        )

        connection.commit()
        connection.close()

        flash(
            f"User '{username}' created successfully.",
            "success"
        )

        return redirect(
            url_for("settings.settings")
        )

    # --------------------------------------------------------
    # Database information
    # --------------------------------------------------------

    connection = get_db()

    event_count = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM events
        """
    ).fetchone()["count"]

    alert_count = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM alerts
        """
    ).fetchone()["count"]

    rule_count = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM detector_rules
        """
    ).fetchone()["count"]

    enabled_rule_count = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM detector_rules
        WHERE enabled = 1
        """
    ).fetchone()["count"]

    indicator_count = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM threat_intelligence
        """
    ).fetchone()["count"]

    user_count = connection.execute(
        """
        SELECT COUNT(*) AS count
        FROM users
        """
    ).fetchone()["count"]

    users = connection.execute(
        """
        SELECT
            id,
            username,
            role,
            created_at
        FROM users
        ORDER BY id
        """
    ).fetchall()

    connection.close()

    system_info = {
        "database": "SQLite",
        "database_status": "CONNECTED",
        "event_count": event_count,
        "alert_count": alert_count,
        "rule_count": rule_count,
        "enabled_rule_count": enabled_rule_count,
        "indicator_count": indicator_count,
        "user_count": user_count,
        "authentication": "ENABLED",
        "detection_engine": "ACTIVE",
        "monitoring": "LOCAL"
    }

    return render_template(
        "settings.html",
        system_info=system_info,
        users=users
    )