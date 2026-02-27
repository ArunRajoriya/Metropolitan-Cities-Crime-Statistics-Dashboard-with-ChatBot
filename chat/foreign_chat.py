from flask import jsonify
from services.data_loader import foreign_data

def handle_foreign_chat(intent, years, structured):

    year = str(years[0]) if years else list(foreign_data.keys())[0]

    if year not in foreign_data:
        return jsonify({"type": "error", "summary": "Year not available"})

    df = foreign_data[year]
    total = df.sum(numeric_only=True).sum()

    return jsonify({
        "type": "foreign",
        "title": f"Foreign Crime Summary - {year}",
        "data": {"Total Foreign Arrests": int(total)},
        "source": "Foreign Crime Dataset"
    })