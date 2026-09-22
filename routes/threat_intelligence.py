from flask import Blueprint, render_template

from database.db import get_db


threat_intelligence_bp = Blueprint(
    "threat_intelligence",
    __name__
)


@threat_intelligence_bp.route("/threat-intelligence")
def threat_intelligence():

    connection = get_db()

    indicators = connection.execute(
        """
        SELECT
            id,
            indicator,
            indicator_type,
            confidence,
            category,
            source,
            notes
        FROM threat_intelligence
        ORDER BY confidence DESC, id DESC
        """
    ).fetchall()

    connection.close()

    total_indicators = len(indicators)

    high_confidence = sum(
        1
        for indicator in indicators
        if indicator["confidence"] >= 80
    )

    medium_confidence = sum(
        1
        for indicator in indicators
        if 50 <= indicator["confidence"] < 80
    )

    low_confidence = sum(
        1
        for indicator in indicators
        if indicator["confidence"] < 50
    )

    return render_template(
        "threat_intelligence.html",
        indicators=indicators,
        total_indicators=total_indicators,
        high_confidence=high_confidence,
        medium_confidence=medium_confidence,
        low_confidence=low_confidence
    )