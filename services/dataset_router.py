def detect_dataset(message, structured):
    msg = message.lower()

    if "foreign" in msg or "foreigner" in msg:
        return "foreign"

    if "government" in msg or "national" in msg or "india total" in msg:
        return "government"

    if structured.get("cities"):
        return "city"

    return "city"  # default fallback