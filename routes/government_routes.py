import pandas as pd
from flask import Blueprint, jsonify, request
from services.data_loader import gov_data
from services.helpers import get_year, find_column

gov_bp = Blueprint('gov_bp', __name__)

@gov_bp.route("/api/gov-data")
def gov_data_api():
    year = request.args.get("year", "all")
    crime = request.args.get("crime", "all")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 100))

    try:
        # Handle year selection
        if year == "all":
            # Combine all years
            df_list = []
            for y, data in gov_data.items():
                temp_df = data.copy()
                temp_df['Year'] = y
                df_list.append(temp_df)
            df = pd.concat(df_list, ignore_index=True)
        else:
            if year not in gov_data:
                year = "2020"  # fallback
            df = gov_data[year].copy()

        # Clean column names
        df.columns = df.columns.str.strip()

        # Filter by crime if specified
        if crime != "all" and "Crime Head" in df.columns:
            df["Crime Head"] = df["Crime Head"].astype(str).str.strip()
            df = df[df["Crime Head"] == crime]

        total_rows = len(df)

        # Pagination
        start = (page - 1) * per_page
        end = start + per_page
        df_page = df.iloc[start:end]

        # Fill NaN values
        df_page = df_page.fillna("")

        return jsonify({
            "columns": df.columns.tolist(),
            "rows": df_page.to_dict(orient="records"),
            "total_rows": total_rows,
            "page": page,
            "per_page": per_page
        })
    
    except Exception as e:
        return jsonify({
            "error": str(e),
            "columns": [],
            "rows": [],
            "total_rows": 0,
            "page": page,
            "per_page": per_page
        }), 500

# GOV CRIMES

@gov_bp.route("/api/gov-crimes")
def gov_crimes():
    year = request.args.get("year", "2020")
    
    if year not in gov_data:
        year = "2020"  # fallback
    
    df = gov_data[year].copy()
    df.columns = df.columns.str.strip()
    
    if "Crime Head" in df.columns:
        df["Crime Head"] = df["Crime Head"].astype(str).str.strip()
        crimes = sorted(df["Crime Head"].dropna().unique().tolist())
        crimes = [c for c in crimes if c != 'nan' and c != '']
    else:
        crimes = []
    
    return jsonify({"crimes": crimes})


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
