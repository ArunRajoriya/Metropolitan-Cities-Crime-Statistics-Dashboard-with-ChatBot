import sqlite3
from datetime import datetime
from flask import Blueprint, jsonify, request, render_template

feedback_bp = Blueprint('feedback_bp', __name__)


@feedback_bp.route("/submit-feedback", methods=["POST"])
def submit_feedback():
    name = request.form.get("name")
    email = request.form.get("email")
    category = request.form.get("category", "general")
    message = request.form.get("message")

    conn = sqlite3.connect("feedback.db")
    cursor = conn.cursor()

    # Check if category column exists, if not add it
    cursor.execute("PRAGMA table_info(feedback)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'category' not in columns:
        cursor.execute("ALTER TABLE feedback ADD COLUMN category TEXT DEFAULT 'general'")

    cursor.execute("""
        INSERT INTO feedback (name, email, category, message, created_at)
        VALUES (?, ?, ?, ?, ?)""", (name, email, category, message, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    conn.commit()
    conn.close()

    return render_template("feedback.html", success=True)
