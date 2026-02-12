import pandas as pd
from flask import Blueprint, jsonify, request
from services.data_loader import gov_data
from services.helpers import get_year, find_column

gov_bp = Blueprint('gov_bp', __name__)

@gov_bp.route("/api/gov-data")
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

@gov_bp.route("/api/gov-crimes")
def gov_crimes():
    year = request.args.get("year", "2020")
    df = gov_data[year]

    crimes = sorted(df["Crime Head"].dropna().unique().tolist())
    return {"crimes": crimes}


@gov_bp.route("/api/highest-crime-trend")
def highest_crime_trend():

    result = {}

    for year, df in gov_data.items():
        df = df.copy()
        df.columns = df.columns.str.strip()

        # remove non numeric columns
        numeric_df = df.select_dtypes(include="number")

        # sum each crime column
        sums = numeric_df.sum()

        # get highest crime column
        top_crime = sums.idxmax()
        top_value = int(sums.max())

        result[year] = {
            "crime": top_crime,
            "value": top_value
        }

    return jsonify(result)
