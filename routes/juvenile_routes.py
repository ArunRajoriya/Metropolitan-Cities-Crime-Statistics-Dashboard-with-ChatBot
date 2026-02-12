import pandas as pd
from flask import Blueprint, jsonify, request
from services.data_loader import crime_data
from services.helpers import get_year, find_column

juvenile_bp = Blueprint('juvenile_bp', __name__)

def get_total_row(df):
    df.columns = df.columns.str.strip()
    return df.tail(1).iloc[0]   # ← THIS is the truth for your CSV



@juvenile_bp.route("/api/juvenile-kpis")
def juvenile_kpis():

    year = request.args.get("year", "all")

    def extract(df):
        row = get_total_row(df)
        return (
            int(row["Juveniles Apprehended - Boys"]),
            int(row["Juveniles Apprehended - Girls"]),
            int(row["Juveniles Apprehended - Total"])
        )

    if year == "all":
        boys = girls = total = 0
        for y in crime_data:
            b, g, t = extract(crime_data[y].copy())
            boys += b
            girls += g
            total += t
        return jsonify({"boys": boys, "girls": girls, "total": total})
    else:
        b, g, t = extract(crime_data[year].copy())
        return jsonify({"boys": b, "girls": g, "total": t})
    
@juvenile_bp.route("/api/juvenile-filter")
def juvenile_filter():

    year   = request.args.get("year", "2020")
    gender = request.args.get("gender", "total").lower()
    city   = request.args.get("city", "all").strip()

    df = crime_data[year].copy()
    df.columns = df.columns.str.strip()

    if city.lower() == "all":
        row = get_total_row(df)
    else:
        city_row = df[df["City"].str.strip().str.lower() == city.lower()]
        row = city_row.iloc[0] if not city_row.empty else get_total_row(df)

    boys  = int(row["Juveniles Apprehended - Boys"])
    girls = int(row["Juveniles Apprehended - Girls"])

    if gender == "boys":
        return jsonify({"labels": ["Boys"], "values": [boys]})
    elif gender == "girls":
        return jsonify({"labels": ["Girls"], "values": [girls]})
    else:
        return jsonify({"labels": ["Boys", "Girls"], "values": [boys, girls]})


@juvenile_bp.route("/api/juvenile-cities")
def juvenile_cities():

    year = request.args.get("year", "2020")

    df = crime_data[year].copy()
    df.columns = df.columns.str.strip()

    df["City"] = df["City"].astype(str).str.strip()
    df["Juveniles Apprehended - Total"] = pd.to_numeric(
        df["Juveniles Apprehended - Total"],
        errors="coerce"
    )

    # remove last row (grand total row)
    df = df.iloc[:-1]

    return jsonify({
        "labels": df["City"].tolist(),
        "values": df["Juveniles Apprehended - Total"].astype(int).tolist()
    })


@juvenile_bp.route("/api/juvenile-trend")
def juvenile_trend():

    result = {}

    for year, df in crime_data.items():
        df = df.copy()
        df.columns = df.columns.str.strip()

        # NCRB total row is ALWAYS last row
        total_row = df.tail(1).iloc[0]

        total_value = pd.to_numeric(
            total_row["Juveniles Apprehended - Total"],
            errors="coerce"
        )

        result[year] = int(total_value)

    return jsonify(result)

