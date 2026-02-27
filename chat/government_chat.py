from flask import jsonify
from services.data_loader import gov_data

def handle_government_chat(intent, years, structured):

    year = str(years[0]) if years else list(gov_data.keys())[0]

    if year not in gov_data:
        return jsonify({"type": "error", "summary": "Year not available"})

    crime_name = structured.get("crime", "").strip().lower()

    df = gov_data[year].copy()
    df.columns = df.columns.str.strip()

    crime_row = df[df["Crime Head"].str.lower() == crime_name]

    if crime_row.empty:
        return jsonify({"type": "error", "summary": "Crime not found"})

    data = crime_row.fillna("").to_dict(orient="records")[0]

    return jsonify({
        "type": "government",
        "title": f"{crime_name.title()} - {year}",
        "data": data,
        "source": "Government Dataset"
    })