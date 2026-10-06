import sqlite3

from flask import (Flask, jsonify, redirect, render_template, request,
                   abort)

import config
from database import get_db, init_app
from utils import generate_code, is_valid_url, normalize_url


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(config)
    if test_config:
        app.config.update(test_config)

    init_app(app)

    # ------------------------------------------------------------------ UI
    @app.get("/")
    def index():
        return render_template("index.html")

    # ----------------------------------------------------------------- API
    @app.post("/api/shorten")
    def shorten():
        data = request.get_json(silent=True) or {}
        long_url = normalize_url(data.get("url"))

        if not is_valid_url(long_url, app.config["MAX_URL_LENGTH"]):
            return jsonify(error="Enter a valid http:// or https:// URL."), 400

        db = get_db()

        # Re-use the existing code if this URL was already shortened.
        row = db.execute(
            "SELECT short_code FROM urls WHERE original_url = ?", (long_url,)
        ).fetchone()
        if row:
            return jsonify(_payload(row["short_code"], long_url)), 200

        # Insert with a fresh code; retry on the rare collision.
        for _ in range(10):
            code = generate_code(app.config["SHORT_CODE_LENGTH"])
            try:
                db.execute(
                    "INSERT INTO urls (short_code, original_url) VALUES (?, ?)",
                    (code, long_url),
                )
                db.commit()
                return jsonify(_payload(code, long_url)), 201
            except sqlite3.IntegrityError:
                db.rollback()
        return jsonify(error="Could not generate a unique code. Try again."), 500

    @app.get("/api/stats/<code>")
    def stats(code):
        row = get_db().execute(
            "SELECT * FROM urls WHERE short_code = ?", (code,)
        ).fetchone()
        if row is None:
            return jsonify(error="Short code not found."), 404
        return jsonify(
            short_code=row["short_code"],
            short_url=request.host_url + row["short_code"],
            original_url=row["original_url"],
            clicks=row["clicks"],
            created_at=row["created_at"],
        )

    @app.get("/api/urls")
    def list_urls():
        rows = get_db().execute(
            "SELECT short_code, original_url, clicks, created_at "
            "FROM urls ORDER BY id DESC LIMIT 20"
        ).fetchall()
        return jsonify([
            {**dict(r), "short_url": request.host_url + r["short_code"]}
            for r in rows
        ])

    # ------------------------------------------------------------ Redirect
    @app.get("/<code>")
    def follow(code):
        db = get_db()
        row = db.execute(
            "SELECT original_url FROM urls WHERE short_code = ?", (code,)
        ).fetchone()
        if row is None:
            abort(404)
        db.execute("UPDATE urls SET clicks = clicks + 1 WHERE short_code = ?",
                   (code,))
        db.commit()
        return redirect(row["original_url"], code=302)

    @app.errorhandler(404)
    def not_found(_e):
        if request.path.startswith("/api/"):
            return jsonify(error="Not found."), 404
        return render_template("404.html"), 404

    def _payload(code, long_url):
        return {
            "short_code": code,
            "short_url": request.host_url + code,
            "original_url": long_url,
        }

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
