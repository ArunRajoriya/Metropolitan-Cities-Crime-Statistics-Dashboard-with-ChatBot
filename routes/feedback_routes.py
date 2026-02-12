import sqlite3
from datetime import datetime
from flask import Blueprint, jsonify, request, render_template

feedback_bp = Blueprint('feedback_bp', __name__)


@feedback_bp.route("/submit-feedback", methods=["POST"])
def submit_feedback():
    name = request.form.get("name")
    email = request.form.get("email")
    message = request.form.get("message")

    conn = sqlite3.connect("feedback.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO feedback (name, email, message, created_at)
        VALUES (?, ?, ?, ?)""", (name, email, message, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    conn.commit()
    conn.close()

    return render_template("feedback.html", success=True)
