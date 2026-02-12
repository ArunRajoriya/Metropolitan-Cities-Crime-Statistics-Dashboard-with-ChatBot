import pandas as pd

def load_csv(path):
    try:
        df = pd.read_csv(path)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return pd.DataFrame()

# Crime data by year
crime_data = {
    "2016": load_csv("data/crime_data_2016.csv"),
    "2019": load_csv("data/crime_data_2019.csv"),
    "2020": load_csv("data/crime_data_2020.csv"),
}

# Government data by year
gov_data = {
    "2016": load_csv("data/Data by government 2016.csv"),
    "2019": load_csv("data/Data by government 2019.csv"),
    "2020": load_csv("data/Data by government 2020.csv"),
}

# Foreigner crime data by year
foreign_data = {
    "2016": load_csv("data/foreigner_2016.csv"),
    "2019": load_csv("data/foreigner_2019.csv"),
    "2020": load_csv("data/foreigner_2020.csv"),
}
