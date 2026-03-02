from flask import jsonify
from services.data_loader import crime_data


def handle_juvenile(year, city=None, category="total", ranking=None, top_n=3):

    if year not in crime_data:
        return jsonify({
            "type": "error",
            "summary": "Year not available."
        })

    df = crime_data[year].copy()

    df = df[df["City"].notna()]
    df = df[~df["City"].str.lower().str.contains("total", na=False)]

    # Column selection
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

    # City specific
    if city and not ranking:
        row = df[df["City"].str.contains(city, case=False, na=False)]
        if row.empty:
            return jsonify({
                "type": "error",
                "summary": "City not found."
            })

        return jsonify({
            "type": "city_juvenile",
            "title": f"Juvenile {category.title()} Arrests - {city} ({year})",
            "data": {"Total": int(row.iloc[0][column])},
            "source": "NCRB Dataset (2016–2020)"
        })

    # Ranking
    if ranking in ["top", "highest", "lowest"]:

        ascending = ranking == "lowest"

        df_sorted = df.sort_values(by=column, ascending=ascending)

        if ranking == "top":
            df_sorted = df_sorted.head(top_n)
        else:
            df_sorted = df_sorted.head(1)

        results = dict(zip(df_sorted["City"], df_sorted[column]))

        return jsonify({
            "type": ranking,
            "title": f"{ranking.capitalize()} Juvenile Cities - {year}",
            "data": results,
            "source": "NCRB Dataset (2016–2020)"
        })

    # Total
    total = df[column].sum()

    return jsonify({
        "type": "juvenile_total",
        "title": f"Juvenile Arrest Total - {year}",
        "data": {"Total": int(total)},
        "source": "NCRB Dataset (2016–2020)"
    })