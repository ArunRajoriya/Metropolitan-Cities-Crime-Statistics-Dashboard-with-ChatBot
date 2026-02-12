import pandas as pd
from flask import Blueprint, jsonify, request
from services.data_loader import foreign_data
from services.helpers import get_year, find_column

foreign_bp = Blueprint('foreign_bp', __name__)

@foreign_bp.route("/api/foreigner-crimes")
def foreigner_crimes():
    year = get_year(foreign_data)
    df = foreign_data[year]


    df = foreign_data[year].copy()
    df.columns = df.columns.str.strip()   # REQUIRED
    df["Crime Head"] = df["Crime Head"].astype(str).str.strip()

    crimes = sorted(df["Crime Head"].unique().tolist())
    return {"crimes": crimes}


@foreign_bp.route("/api/foreigner-data")
def foreigner_data_api():
    year = get_year(foreign_data)
    df = foreign_data[year]

    crime = request.args.get("crime", "all")

    df = foreign_data[year].copy()

    # IMPORTANT
    df.columns = df.columns.str.strip()
    df["Crime Head"] = df["Crime Head"].astype(str).str.strip()

    if crime != "all":
        df = df[df["Crime Head"] == crime]

    df = df.fillna("")

    return jsonify({
        "columns": df.columns.tolist(),
        "rows": df.to_dict(orient="records")
    })

@foreign_bp.route("/api/foreigner-trend")
def foreigner_trend():

    result = {}

    for year, df in foreign_data.items():
        df = df.copy()
        df.columns = df.columns.str.strip()

        # find numeric columns only
        numeric_cols = df.select_dtypes(include="number").columns

        if len(numeric_cols) == 0:
            result[year] = {"crime": "-", "value": 0}
            continue

        totals = df[numeric_cols].sum()

        highest_crime = totals.idxmax()
        highest_value = int(totals.max())

        result[year] = {
            "crime": highest_crime,
            "value": highest_value
        }

    return jsonify(result)

