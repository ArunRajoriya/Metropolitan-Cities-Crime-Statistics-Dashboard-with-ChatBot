def calculate_city_totals(data, gender=None):

    if gender:
        gender = gender.lower()

    if gender == "male":
        return int(data.get("Total - Male", 0))

    elif gender == "female":
        return int(data.get("Total - Female", 0))

    # default total
    return int(
        data.get("Total - Total Persons Arrested by age and Sex", 0)
    )