"""
Helper functions for routes
"""
from flask import request


def get_year(data_dict):
    """Get year from request args, default to 2020"""
    year = request.args.get("year", "2020")
    return year if year in data_dict else "2020"


def find_column(df, keywords):
    """Find column in dataframe that matches all keywords"""
    for col in df.columns:
        if all(k.lower() in col.lower() for k in keywords):
            return col
    return None


# Population column mappings
POP_COLUMNS = {
    "total": "Total Population",
    "male": "Male Population",
    "female": "Female Population"
}
