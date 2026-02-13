import pandas as pd
from flask import Blueprint, jsonify, request
from services.data_loader import crime_data
from services.helpers import get_year, find_column, POP_COLUMNS


crime_bp = Blueprint('crime_bp', __name__)
@crime_bp.route("/api/cities")
def get_cities():
    year = get_year(crime_data)
    if year == "all":
     df = pd.concat(crime_data.values(), ignore_index=True)
    else:
     df = crime_data[year].copy()

    df.columns = df.columns.str.strip()

    if "City" not in df.columns:
        return {"cities": []}

    cities = sorted(df["City"].dropna().unique().tolist())
    return {"cities": cities}


@crime_bp.route("/api/city-profile")
def city_profile():
    year = request.args.get("year", "2020")
    city = request.args.get("city", "all")

    # ✅ Correct year handling
    if year == "all":
        df = pd.concat(crime_data.values(), ignore_index=True)
    else:
        df = crime_data[year].copy()

    df.columns = df.columns.str.strip()

    if city != "all":
        df = df[df["City"] == city]

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
        "Total - Male",
        "Total - Female",
        "Total - Total Persons Arrested by age and Sex"
    ]

    data = {col: int(sums.get(col, 0)) for col in required_cols}

    return jsonify(data)


@crime_bp.route("/api/filter")
def filter_data():

    year   = request.args.get("year", "2020")
    city   = request.args.get("city", "all")
    age    = request.args.get("age", "all")
    gender = request.args.get("gender", "all")

    # -------- YEAR HANDLING --------
    if year == "all":
        df = pd.concat(crime_data.values(), ignore_index=True)
    else:
        df = crime_data[year].copy()

    df.columns = df.columns.str.strip()

    # -------- CITY FILTER --------
    if city != "all":
        df = df[df["City"].astype(str).str.strip() == city]

    # -------- TOTAL COLUMN --------
    total_col = find_column(df, ["Total", "Arrested"])
    if not total_col:
        return jsonify({"grand_total": 0, "filtered_total": 0})

    # -------- AGE MAP --------
    age_map = {
        "18-30": "18 and above and below 30 years",
        "30-45": "30 and above and below 45 years",
        "45-60": "45 and above and below 60 years",
        "60 years and above": "60 years and above",
    }

    # -------- HELPER: SAFE COLUMN FIND --------
    def find_real_column(target):
        for c in df.columns:
            if c.replace(" ", "") == target.replace(" ", ""):
                return c
        return None

    # -------- DETERMINE FILTER COLUMN --------
    col = total_col

    if age != "all" and gender != "all":
        target = f"{age_map[age]} - {gender.capitalize()}"
        col = find_real_column(target)

    elif age != "all":
        target = f"{age_map[age]} - Total"
        col = find_real_column(target)

    elif gender != "all":
        target = f"Total - {gender.capitalize()}"
        col = find_real_column(target)

    # -------- COLUMN SAFETY --------
    if not col or col not in df.columns:
        return jsonify({"grand_total": 0, "filtered_total": 0})

    # -------- NUMERIC CLEAN --------
    df[total_col] = pd.to_numeric(df[total_col], errors="coerce").fillna(0)
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    grand_total = int(df[total_col].sum())
    filtered_total = int(df[col].sum())

    return jsonify({
        "grand_total": grand_total,
        "filtered_total": filtered_total
    })


@crime_bp.route("/api/year-trend")
def year_trend():

    result = {}

    for year, df in crime_data.items():
        df = df.copy()
        df.columns = df.columns.str.strip()

        total_col = find_column(df, ["Total", "Arrested"])
        df[total_col] = pd.to_numeric(df[total_col], errors="coerce").fillna(0)

        result[year] = int(df[total_col].sum())

    return jsonify(result)


@crime_bp.route("/api/all-kpis")
def all_year_kpis():

    totals = {}

    for year, df in crime_data.items():
        df = df.copy()
        df.columns = df.columns.str.strip()

        total_col = find_column(df, ["Total", "Arrested"])
        df[total_col] = pd.to_numeric(df[total_col], errors="coerce").fillna(0)

        totals[year] = int(df[total_col].sum())

    total_all = sum(totals.values())
    highest_year = max(totals, key=totals.get)
    lowest_year = min(totals, key=totals.get)
    avg = int(total_all / len(totals))

    return jsonify({
        "totals": totals,
        "total_all": total_all,
        "highest_year": highest_year,
        "lowest_year": lowest_year,
        "average": avg
    })

@crime_bp.route("/api/home-kpis")
def home_kpis():

    # Use latest year data for population
    latest_year = max(crime_data.keys())
    df = crime_data[latest_year].copy()
    df.columns = df.columns.str.strip()

    # ---- Population columns ----
    pop_total_col  = POP_COLUMNS["total"]
    pop_male_col   = POP_COLUMNS["male"]
    pop_female_col = POP_COLUMNS["female"]

    last_row = df.iloc[-1]

    total_population  = int(str(last_row[pop_total_col]).replace(",", "").strip())
    male_population   = int(str(last_row[pop_male_col]).replace(",", "").strip())
    female_population = int(str(last_row[pop_female_col]).replace(",", "").strip())

    # ---- Crime concentration ----
    total_col = find_column(df, ["Total", "Arrested"])
    df[total_col] = pd.to_numeric(df[total_col], errors="coerce").fillna(0)

    total_arrests = int(df[total_col].sum())
    crime_concentration = round((total_arrests / total_population) * 100, 2)

    return jsonify({
        "total_population": total_population,
        "male_population": male_population,
        "female_population": female_population,
       
    })


@crime_bp.route("/api/gender-ratio")
def gender_ratio():

    year = request.args.get("year", "all")

    # Handle all years
    if year == "all":
        df = pd.concat(crime_data.values(), ignore_index=True)
    else:
        df = crime_data[year].copy()

    df.columns = df.columns.str.strip()

    male_col = "Total - Male"
    female_col = "Total - Female"

    df[male_col] = pd.to_numeric(df[male_col], errors="coerce").fillna(0)
    df[female_col] = pd.to_numeric(df[female_col], errors="coerce").fillna(0)

    total_male = int(df[male_col].sum())
    total_female = int(df[female_col].sum())

    # Avoid division by zero
    ratio = round(total_male / total_female, 2) if total_female else 0

    return jsonify({
        "male": total_male,
        "female": total_female,
        "ratio": ratio
    })

@crime_bp.route("/api/city-comparison")
def city_comparison():
    year = request.args.get("year")

    df = crime_data[year].copy()
    df.columns = df.columns.str.strip()

    total_col = find_column(df, ["Total", "Arrested"])
    df[total_col] = pd.to_numeric(df[total_col], errors="coerce").fillna(0)

    result = (
        df.groupby("City")[total_col]
        .sum()
        .sort_values(ascending=False)
        .to_dict()
    )

    return jsonify(result)


@crime_bp.route("/api/age-gender-trend")
def age_gender_trend():
    age = request.args.get("age")
    gender = request.args.get("gender")

    age_map = {
        "18-30": "18 and above and below 30 years",
        "30-45": "30 and above and below 45 years",
        "45-60": "45 and above and below 60 years",
        "60 years and above": "60 years and above",
    }

    col_name = f"{age_map[age]} - {gender.capitalize()}"

    result = {}

    for year, df in crime_data.items():
        df = df.copy()
        df.columns = df.columns.str.strip()

        # find real column (ignore spacing issues)
        real_col = None
        for c in df.columns:
            if c.replace(" ", "") == col_name.replace(" ", ""):
                real_col = c
                break

        if not real_col:
            result[year] = 0
            continue

        df[real_col] = pd.to_numeric(df[real_col], errors="coerce").fillna(0)
        result[year] = int(df[real_col].sum())

    return jsonify(result)

@crime_bp.route("/api/gender-city-comparison")
def gender_city_comparison():

    gender = request.args.get("gender", "male").capitalize()

    dfs = []
    for df in crime_data.values():
        d = df.copy()
        d.columns = d.columns.str.strip()

        # ---- CLEAN CITY COLUMN PROPERLY ----
        d["City"] = (
            d["City"]
            .astype(str)
            .str.strip()
            .str.lower()
            .str.replace(" ", "", regex=False)   # remove spaces
            .str.replace("(", "", regex=False)   # remove brackets
            .str.replace(")", "", regex=False)
        )

        # ❗ Remove invalid / total rows
        d = d[
            d["City"].notna() &
            (~d["City"].str.contains("total")) &
            (d["City"] != "nan") &
            (d["City"] != "")
        ]

        dfs.append(d)

    df = pd.concat(dfs, ignore_index=True)

    col = f"Total - {gender}"
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    result = (
        df.groupby("City")[col]
        .sum()
        .sort_values(ascending=False)
        .to_dict()
    )

    return jsonify(result)

@crime_bp.route("/api/age-trend")
def age_trend():
    age = request.args.get("age")

    age_map = {
        "18-30": "18 and above and below 30 years - Total",
        "30-45": "30 and above and below 45 years - Total",
        "45-60": "45 and above and below 60 years - Total",
        "60 years and above": "60 years and above - Total",
    }

    col_name = age_map[age]
    result = {}

    for year, df in crime_data.items():
        df = df.copy()
        df.columns = df.columns.str.strip()

        real_col = None
        for c in df.columns:
            if c.replace(" ", "") == col_name.replace(" ", ""):
                real_col = c
                break

        if not real_col:
            result[year] = 0
            continue

        df[real_col] = pd.to_numeric(df[real_col], errors="coerce").fillna(0)
        result[year] = int(df[real_col].sum())

    return jsonify(result)

@crime_bp.route("/api/year-gender-city")
def year_gender_city():
    year = request.args.get("year")
    gender = request.args.get("gender").capitalize()

    df = crime_data[year].copy()
    df.columns = df.columns.str.strip()

    col = f"Total - {gender}"

    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # remove total row
    df = df[~df["City"].str.lower().str.contains("total", na=False)]

    result = (
        df.groupby("City")[col]
        .sum()
        .sort_values(ascending=False)
        .to_dict()
    )

    return jsonify(result)


@crime_bp.route("/api/reports-summary")
def reports_summary():

    dfs = []
    for df in crime_data.values():
        d = df.copy()
        d.columns = d.columns.str.strip()
        dfs.append(d)

    df = pd.concat(dfs, ignore_index=True)

    total_col = find_column(df, ["Total", "Arrested"])
    df[total_col] = pd.to_numeric(df[total_col], errors="coerce").fillna(0)

    # ---------- Total arrests ----------
    total_arrests = int(df[total_col].sum())

    # ---------- Top 10 cities concentration ----------
    city_sum = (
        df.groupby("City")[total_col]
        .sum()
        .sort_values(ascending=False)
    )

    top10 = city_sum.head(10).sum()
    concentration = round((top10 / total_arrests) * 100, 2)

    # ---------- Juvenile percentage ----------
    j_col = "Juveniles Apprehended - Total"
    df[j_col] = pd.to_numeric(df[j_col], errors="coerce").fillna(0)
    juvenile_total = int(df[j_col].sum())
    juvenile_pct = round((juvenile_total / total_arrests) * 100, 2)

    # ---------- Gender ratio ----------
    male_col = "Total - Male"
    female_col = "Total - Female"

    df[male_col] = pd.to_numeric(df[male_col], errors="coerce").fillna(0)
    df[female_col] = pd.to_numeric(df[female_col], errors="coerce").fillna(0)

    male = int(df[male_col].sum())
    female = int(df[female_col].sum())
    gender_ratio = round(male / female, 2)

    return jsonify({
        "total_arrests": total_arrests,
        "top10_concentration": concentration,
        "juvenile_pct": juvenile_pct,
        "gender_ratio": gender_ratio
    })


@crime_bp.route("/api/year-city-filter")
def year_city_filter():

    year = request.args.get("year")
    age = request.args.get("age", "all")
    gender = request.args.get("gender", "all")

    df = crime_data[year].copy()
    df.columns = df.columns.str.strip()

    age_map = {
        "18-30": "18 and above and below 30 years",
        "30-45": "30 and above and below 45 years",
        "45-60": "45 and above and below 60 years",
        "60 years and above": "60 years and above",
    }

    # Decide column
    if age != "all" and gender != "all":
        col = f"{age_map[age]} - {gender.capitalize()}"
    elif age != "all":
        col = f"{age_map[age]} - Total"
    elif gender != "all":
        col = f"Total - {gender.capitalize()}"
    else:
        col = find_column(df, ["Total", "Arrested"])

    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # remove total row
    df = df[~df["City"].str.lower().str.contains("total", na=False)]

    result = (
        df.groupby("City")[col]
        .sum()
        .sort_values(ascending=False)
        .to_dict()
    )

    return jsonify(result)


@crime_bp.route("/api/gender-ratio-trend")
def gender_ratio_trend():

    result = {}

    for year, df in crime_data.items():
        df = df.copy()
        df.columns = df.columns.str.strip()

        male_col = "Total - Male"
        female_col = "Total - Female"

        df[male_col] = pd.to_numeric(df[male_col], errors="coerce").fillna(0)
        df[female_col] = pd.to_numeric(df[female_col], errors="coerce").fillna(0)

        male = df[male_col].sum()
        female = df[female_col].sum()

        ratio = round(male / female, 2) if female else 0
        result[year] = ratio

    return jsonify(result)
