import pandas as pd
from flask import Blueprint, jsonify, request
from services.data_loader import foreign_data
from services.helpers import get_year, find_column

foreign_bp = Blueprint('foreign_bp', __name__)

@foreign_bp.route("/api/foreigner-crimes")
def foreigner_crimes():
    year = request.args.get("year", "2020")
    
    if year not in foreign_data:
        year = "2020"  # fallback
    
    df = foreign_data[year].copy()
    df.columns = df.columns.str.strip()
    
    if "Crime Head" in df.columns:
        df["Crime Head"] = df["Crime Head"].astype(str).str.strip()
        crimes = sorted(df["Crime Head"].dropna().unique().tolist())
        crimes = [c for c in crimes if c != 'nan' and c != '']
    else:
        crimes = []
    
    return jsonify({"crimes": crimes})


@foreign_bp.route("/api/foreigner-data")
def foreigner_data_api():
    year = request.args.get("year", "2020")
    crime = request.args.get("crime", "all")
    
    if year == "all":
        # Combine all years
        df_list = []
        for y, data in foreign_data.items():
            temp_df = data.copy()
            temp_df['Year'] = y
            df_list.append(temp_df)
        df = pd.concat(df_list, ignore_index=True)
    else:
        if year not in foreign_data:
            year = "2020"  # fallback
        df = foreign_data[year].copy()

    # Clean column names
    df.columns = df.columns.str.strip()
    
    # Filter by crime if specified
    if crime != "all" and "Crime Head" in df.columns:
        df["Crime Head"] = df["Crime Head"].astype(str).str.strip()
        df = df[df["Crime Head"] == crime]

    # Fill NaN values
    df = df.fillna("")

    return jsonify({
        "columns": df.columns.tolist(),
        "rows": df.to_dict(orient="records"),
        "total_rows": len(df)
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

