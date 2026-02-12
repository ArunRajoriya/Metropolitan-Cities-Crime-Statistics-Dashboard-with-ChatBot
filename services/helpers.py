from flask import request

def get_year(data_dict):
    year = request.args.get("year", "2020")
    return year if year in data_dict else "2020"


def find_column(df, keywords):
    for col in df.columns:
        if all(k.lower() in col.lower() for k in keywords):
            return col
    return None

POP_COLUMNS = {
    "total": "Total Population",
    "male": "Male Population",
    "female": "Female Population"
}
