from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from werkzeug.security import check_password_hash

from database.db import get_db


auth_bp = Blueprint(
    "auth",
    __name__
)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    # --------------------------------------------------------
    # Already logged in
    # --------------------------------------------------------

    if session.get("user_id"):

        return redirect(
            url_for("dashboard.dashboard")
        )

    # --------------------------------------------------------
    # Login request
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

        # ----------------------------------------------------
        # Validate input
        # ----------------------------------------------------

        if not username or not password:

            flash(
                "Username and password are required.",
                "error"
            )

            return render_template(
                "login.html"
            )

        # ----------------------------------------------------
        # Find user
        # ----------------------------------------------------

        connection = get_db()

        user = connection.execute(
            """
            SELECT
                id,
                username,
                password_hash,
                role
            FROM users
            WHERE username = ?
            """,
            (username,)
        ).fetchone()

        connection.close()

        # ----------------------------------------------------
        # Check username
        # ----------------------------------------------------

        if user is None:

            flash(
                "Invalid username or password.",
                "error"
            )

            return render_template(
                "login.html"
            )

        # ----------------------------------------------------
        # Check password
        # ----------------------------------------------------

        if not check_password_hash(
            user["password_hash"],
            password
        ):

            flash(
                "Invalid username or password.",
                "error"
            )

            return render_template(
                "login.html"
            )

        # ----------------------------------------------------
        # Create application session
        # ----------------------------------------------------

        session.clear()

        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["role"] = user["role"]

        session.permanent = True

        # ----------------------------------------------------
        # Redirect to MiniSOC
        # ----------------------------------------------------

        return redirect(
            url_for("dashboard.dashboard")
        )

    # --------------------------------------------------------
    # Login page
    # --------------------------------------------------------

    return render_template(
        "login.html"
    )


@auth_bp.route("/logout")
def logout():

    username = session.get(
        "username",
        "User"
    )

    session.clear()

    flash(
        f"{username} has been logged out.",
        "success"
    )

    return redirect(
        url_for("auth.login")
    )