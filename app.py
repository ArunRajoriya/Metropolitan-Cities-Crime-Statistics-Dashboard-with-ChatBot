import sqlite3
from datetime import datetime
from flask import Flask, render_template, jsonify, request, send_from_directory
import pandas as pd

app = Flask(__name__)
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
    "2019": pd.read_csv("data/crime_data_2019.csv"),
    "2020": pd.read_csv("data/crime_data_2020.csv")
}


gov_data = {
    "2019": pd.read_csv("data/Data by government 2019.csv"),
    "2020": pd.read_csv("data/Data by government 2020.csv")
}

def get_year():
    return request.args.get("year", "2020")


def normalize(df):
    df.columns = df.columns.str.strip()
    return df


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





# ===================== CITY LIST =====================

@app.route("/api/cities")
def get_cities():
    year = get_year()
    df = normalize(crime_data[year])

    if "City" not in df.columns:
        return {"cities": []}

    cities = sorted(df["City"].dropna().unique().tolist())
    return {"cities": cities}


# ===================== CITY WISE =====================

@app.route("/api/city-wise")
def city_wise():
    year = get_year()
    df = normalize(crime_data[year])

    total_col = next(c for c in df.columns if "Total" in c and "Arrested" in c)

    data = df.groupby("City")[total_col].sum().reset_index()
    data.columns = ["City", "Total"]

    return data.to_dict(orient="records")


# ===================== FILTER (CITY + AGE + GENDER) =====================

@app.route("/api/filter")
def filter_data():
    year = get_year()
    city = request.args.get("city", "all")
    age = request.args.get("age", "all")
    gender = request.args.get("gender", "all")

    df = crime_data[year].copy()
    df.columns = df.columns.str.strip()

    if city != "all":
        df = df[df["City"] == city]

    total_col = next(c for c in df.columns
                     if "Total Persons Arrested" in c)

    age_map = {
        "18-30": "18 and above and below 30 years",
        "30-45": "30 and above and below 45 years",
        "45-60": "45 and above and below 60 years",
        "60 years and above": "60 years and above",
    }

    if age != "all" and gender != "all":
        col = f"{age_map[age]} - {gender.capitalize()}"

    elif age != "all":
        col = f"{age_map[age]} - Total"

    elif gender != "all":
        col = f"Total   - {gender.capitalize()}"

    else:
        col = total_col

    if col not in df.columns:
        return jsonify({"grand_total": 0, "filtered_total": 0})

    grand_total = df[total_col].sum()
    filtered_total = df[col].sum()

    return jsonify({
        "grand_total": int(grand_total),
        "filtered_total": int(filtered_total)
    })

#==== HOME KPIs (REAL ANALYTICS) =====================

@app.route("/api/home-kpis")
def home_kpis():

    df = crime_data["2020"].copy()
    df.columns = df.columns.str.strip()

    # ----------- FIX POPULATION COLUMNS -------------
    for col in df.columns:
        if "Population" in col:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(",", "", regex=False)   # remove commas
                .str.replace("nan", "", regex=False)
            )
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # ----------- Detect columns safely -------------
    total_col = next(c for c in df.columns if "Arrested" in c and "Total" in c)
    pop_total_col = next(c for c in df.columns if "Population" in c and "Total" in c)
    pop_male_col = next(c for c in df.columns if "Population" in c and "Male" in c)
    pop_female_col = next(c for c in df.columns if "Population" in c and "Female" in c)

    # ----------- Calculations -------------
    total_arrests = df[total_col].sum()

    city_sum = df.groupby("City")[total_col].sum().sort_values(ascending=False)
    top10_total = city_sum.head(10).sum()
    concentration = (top10_total / total_arrests) * 100

    total_population = df[pop_total_col].sum()
    male_population = df[pop_male_col].sum()
    female_population = df[pop_female_col].sum()

    return jsonify({
        "total_population": int(total_population),
        "male_population": int(male_population),
        "female_population": int(female_population),
        "total_arrests": int(total_arrests),
        "crime_concentration": round(concentration, 1),
        "govt_handling": 100
    })

@app.route("/api/city-profile")
def city_profile():
    year = request.args.get("year", "2020")
    city = request.args.get("city", "all")

    df = crime_data[year].copy()
    df.columns = df.columns.str.strip()

    if city != "all":
        df = df[df["City"] == city]

    # Sum all numeric columns
    sums = df.sum(numeric_only=True)

    required_cols = [
        "Juveniles Apprehended - Boys",
        "Juveniles Apprehended - Girls",
        "Juveniles Apprehended - Total",

        "18 and above and below 30 years - Male",
        "18 and above and below 30 years - Female",
        "18 and above and below 30 years - Total",

        "30 and above and below 45 years - Male",
        "30 and above and below 45 years - Female",
        "30 and above and below 45 years - Total",

        "45 and above and below 60 years - Male",
        "45 and above and below 60 years - Female",
        "45 and above and below 60 years - Total",

        "60 years and above - Male",
        "60 years and above - Female",
        "60 years and above - Total",

        "Total   - Male",
        "Total   - Female",
        "Total   - Total Persons Arrested by age and Sex"
    ]

    data = {col: int(sums.get(col, 0)) for col in required_cols}

    return jsonify(data)


@app.route("/api/juvenile-kpis")
def juvenile_kpis():

    response = {}

    for year in ["2019", "2020"]:
        df = crime_data[year].copy()
        df.columns = df.columns.str.strip()

        last = df.tail(1).iloc[0]  # NCRB total row

        response[f"boys{year}"]  = int(last["Juveniles Apprehended - Boys"])
        response[f"girls{year}"] = int(last["Juveniles Apprehended - Girls"])
        response[f"total{year}"] = int(last["Juveniles Apprehended - Total"])

    return jsonify(response)


@app.route("/api/juvenile-filter")
def juvenile_filter():

    year   = request.args.get("year", "2020")
    gender = request.args.get("gender", "total").lower()
    city   = request.args.get("city", "all").lower()

    df = crime_data[year].copy()
    df.columns = df.columns.str.strip()
    df["City"] = df["City"].astype(str).str.strip()

    # ---- Find total row safely (works for 2019, 2020, any year)
    total_row = df[df["City"].str.lower().str.contains("total")].iloc[0]

    if city == "all":
        row = total_row
    else:
        city_row = df[df["City"].str.lower() == city]
        if city_row.empty:
            row = total_row
        else:
            row = city_row.iloc[0]

    boys  = int(row["Juveniles Apprehended - Boys"])
    girls = int(row["Juveniles Apprehended - Girls"])

    if gender == "boys":
        labels = ["Boys"]
        values = [boys]
    elif gender == "girls":
        labels = ["Girls"]
        values = [girls]
    else:
        labels = ["Boys", "Girls"]
        values = [boys, girls]

    return jsonify({
        "labels": labels,
        "values": values
    })


@app.route("/api/juvenile-cities")
def juvenile_cities():

    year = request.args.get("year", "2020")

    df = crime_data[year].copy()
    df.columns = df.columns.str.strip()

    # Clean columns properly
    df["City"] = df["City"].astype(str).str.strip()
    df["Juveniles Apprehended - Total"] = pd.to_numeric(
        df["Juveniles Apprehended - Total"],
        errors="coerce"
    )

    # ❗ Remove rows where city is invalid or total is invalid
    df = df[
        df["City"].notna() &
        (df["City"] != "") &
        (df["City"].str.lower() != "nan") &
        (~df["City"].str.lower().str.contains("total")) &
        (df["Juveniles Apprehended - Total"].notna())
    ]

    labels = df["City"].tolist()
    totals = df["Juveniles Apprehended - Total"].astype(int).tolist()

    return jsonify({
        "labels": labels,
        "values": totals
    })

# API GOV DATA
@app.route("/api/gov-data")
def gov_data_api():
    year = request.args.get("year", "2020")
    crime = request.args.get("crime", "all")

    df = gov_data[year].copy()
    df.columns = df.columns.str.strip()

    if crime != "all":
        df = df[df["Crime Head"] == crime]

    # Convert NaN to empty for clean table
    df = df.fillna("")

    return jsonify({
        "columns": df.columns.tolist(),
        "rows": df.to_dict(orient="records")
    })
# GOV CRIMES

@app.route("/api/gov-crimes")
def gov_crimes():
    year = request.args.get("year", "2020")
    df = gov_data[year]

    crimes = sorted(df["Crime Head"].dropna().unique().tolist())
    return {"crimes": crimes}



# API SUBMIT FEEDBACK
@app.route("/submit-feedback", methods=["POST"])
def submit_feedback():
    name = request.form.get("name")
    email = request.form.get("email")
    message = request.form.get("message")

    conn = sqlite3.connect("feedback.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO feedback (name, email, message, created_at)
        VALUES (?, ?, ?, ?)
    """, (name, email, message, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    conn.commit()
    conn.close()

    return render_template("feedback.html", success=True)

   
# ===================== RUN =====================

if __name__ == "__main__":
    app.run(debug=True)
