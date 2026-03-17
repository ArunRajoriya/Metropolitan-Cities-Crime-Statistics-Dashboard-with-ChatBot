import sqlite3
from datetime import datetime
from flask import Flask, render_template, jsonify, request, send_from_directory
import pandas as pd
from routes.crime_routes import crime_bp
from routes.juvenile_routes import juvenile_bp
from routes.government_routes import gov_bp
from routes.foreigner_routes import foreign_bp
from routes.feedback_routes import feedback_bp
from routes.analytics_routes import analytics_bp
from chat.chat_routes import chat_bp
import os
import secrets
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
app.register_blueprint(crime_bp)
app.register_blueprint(juvenile_bp)
app.register_blueprint(gov_bp)
app.register_blueprint(foreign_bp)
app.register_blueprint(feedback_bp)
app.register_blueprint(analytics_bp)
app.register_blueprint(chat_bp)

# Production-ready secret key
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# Configure logging
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240000, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Crime Analytics Dashboard startup')

# Security headers
@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://unpkg.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:;"
    return response

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f'Server Error: {error}')
    return render_template('errors/500.html'), 500

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403


def init_db():
    conn = sqlite3.connect("feedback.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            message TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


init_db()


# ===================== LOAD DATA ONCE =====================

crime_data = {
    "2016": pd.read_csv("data/crime_data_2016.csv"),
    "2019": pd.read_csv("data/crime_data_2019.csv"),
    "2020": pd.read_csv("data/crime_data_2020.csv")
}


gov_data = {
     "2016": pd.read_csv("data/Data by government 2016.csv"),
    "2019": pd.read_csv("data/Data by government 2019.csv"),
    "2020": pd.read_csv("data/Data by government 2020.csv")
}

foreign_data = {
    "2016": pd.read_csv("data/foreigner_2016.csv"),
    "2019": pd.read_csv("data/foreigner_2019.csv"),
    "2020": pd.read_csv("data/foreigner_2020.csv")
}



def get_year():
    return request.args.get("year", "2016")




# ===================== PAGES =====================

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/reports")
def reports():
    return render_template("reports.html")


@app.route("/disclaimer")
def disclaimer():
    return render_template("disclaimer.html")

@app.route("/terms")
def terms():
    return render_template("terms.html")

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")
@app.route("/copyright")
def copyright():
    return render_template("copyright.html")

@app.route("/feedback")
def feedback():
    return render_template("feedback.html")
@app.route("/juvenile")
def juvenile():
    return render_template("juvenile.html")
@app.route("/sitemap")
def sitemap():
    return render_template("sitemap.html")
@app.route("/government-data")
def government_data():
    return render_template("government.html")

@app.route("/foreigners")
def foreigners():
    return render_template("foreigner.html")

@app.route("/faq")
def faq():
    return render_template("faq.html")

@app.route("/api/health-check")
def health_check():
    return {
        "status": "OK",
        "message": "All APIs are reachable"
    }

@app.route("/api/debug-list")
def list_routes():
    output = []
    for rule in app.url_map.iter_rules():
        output.append(str(rule))
    return {"routes": output}


# ===================== RUN =====================

if __name__ == "__main__":
    app.run(debug=True)