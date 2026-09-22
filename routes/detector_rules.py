from flask import Blueprint, flash, redirect, render_template, url_for

from database.db import get_db


detector_rules_bp = Blueprint(
    "detector_rules",
    __name__
)


@detector_rules_bp.route("/detector-rules")
def detector_rules():

    connection = get_db()

    rules = connection.execute(
        """
        SELECT
            id,
            rule_id,
            name,
            description,
            severity,
            enabled
        FROM detector_rules
        ORDER BY id
        """
    ).fetchall()

    connection.close()

    total_rules = len(rules)

    enabled_rules = sum(
        1
        for rule in rules
        if rule["enabled"]
    )

    disabled_rules = total_rules - enabled_rules

    return render_template(
        "detector_rules.html",
        rules=rules,
        total_rules=total_rules,
        enabled_rules=enabled_rules,
        disabled_rules=disabled_rules
    )


@detector_rules_bp.route(
    "/detector-rules/<int:rule_id>/toggle",
    methods=["POST"]
)
def toggle_rule(rule_id):

    connection = get_db()

    rule = connection.execute(
        """
        SELECT
            id,
            rule_id,
            enabled
        FROM detector_rules
        WHERE id = ?
        """,
        (rule_id,)
    ).fetchone()

    if rule is None:

        connection.close()

        flash(
            "Detector rule not found.",
            "error"
        )

        return redirect(
            url_for("detector_rules.detector_rules")
        )

    new_status = 0 if rule["enabled"] else 1

    connection.execute(
        """
        UPDATE detector_rules
        SET enabled = ?
        WHERE id = ?
        """,
        (new_status, rule_id)
    )

    connection.commit()
    connection.close()

    if new_status:
        flash(
            f"Rule {rule['rule_id']} enabled.",
            "success"
        )
    else:
        flash(
            f"Rule {rule['rule_id']} disabled.",
            "success"
        )

    return redirect(
        url_for("detector_rules.detector_rules")
    )