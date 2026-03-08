import re


def normalize_query(message):

    msg = message.lower()

    # remove punctuation
    msg = re.sub(r"[^\w\s]", "", msg)

    # normalize arrest questions
    arrest_patterns = [
        "how many arrests",
        "arrests happened",
        "arrests recorded",
        "arrest count",
        "number of arrests"
    ]

    for pattern in arrest_patterns:
        if pattern in msg:
            msg = msg.replace(pattern, "total arrests")

    # normalize comparison
    msg = msg.replace("vs", "compare")

    # normalize top queries
    msg = msg.replace("most", "highest")

    return msg