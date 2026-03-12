from flask import jsonify
from services.data_loader import crime_data


def handle_juvenile(year, city=None, category="total", ranking=None, top_n=3):

    # Validate year
    if year not in crime_data:
        return jsonify({
            "type": "error",
            "summary": "Year not available."
        })

    df = crime_data[year].copy()

    # Clean dataset
    df = df[df["City"].notna()]
    df = df[~df["City"].str.lower().str.contains("total", na=False)]

    # ================= COLUMN SELECTION =================
    if category == "boys":
        column = "Juveniles Apprehended - Boys"
    elif category == "girls":
        column = "Juveniles Apprehended - Girls"
    else:
        column = "Juveniles Apprehended - Total"

    if column not in df.columns:
        return jsonify({
            "type": "error",
            "summary": "Juvenile column not found."
        })

    df[column] = df[column].fillna(0).astype(int)

    # ================= CITY QUERY =================
    if city and not ranking:
        
        import re
        # Escape regex special characters
        city_escaped = re.escape(city)
        row = df[df["City"].str.contains(city_escaped, case=False, na=False, regex=True)]

        if row.empty:
            return jsonify({
                "type": "error",
                "summary": "City not found."
            })

        value = int(row.iloc[0][column])

        return jsonify({
            "type": "city_juvenile",
            "title": f"Juvenile {category.title()} Arrests - {city} ({year})",
            "data": {"Total": value},
            "source": "NCRB Dataset (2016–2020)"
        })

    # ================= RANKING =================
    if ranking in ["top", "highest", "lowest"]:

        ascending = ranking == "lowest"

        df_sorted = df.sort_values(by=column, ascending=ascending)

        if ranking == "top":
            df_sorted = df_sorted.head(top_n)
        else:
            df_sorted = df_sorted.head(1)

        results = dict(zip(df_sorted["City"], df_sorted[column]))

        return jsonify({
            "type": "juvenile_ranking",
            "title": f"{ranking.capitalize()} Juvenile Cities - {year}",
            "data": results,
            "source": "NCRB Dataset (2016–2020)"
        })

    # ================= TOTAL =================
    total = int(df[column].sum())
    
    # Map category to display name
    category_display = {
        "boys": "Boys",
        "girls": "Girls",
        "total": "Total"
    }

    return jsonify({
        "type": "juvenile_total",
        "title": f"Juvenile {category_display.get(category, category.title())} Arrest Total - {year}",
        "data": {"Total": total},
        "source": "NCRB Dataset (2016–2020)"
    })