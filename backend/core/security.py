BLOCKED_PATHS = [

    "C:/Windows",
    "C:/Program Files",
    "C:/Users"
]

BLOCKED_DOMAINS = [

    "malware",
    "phishing",
    "tor"
]

MAX_AUTONOMOUS_STEPS = 20


def validate_action(
    action,
    params
):

    # =========================
    # BLOCK DELETE
    # =========================
    if action == "delete_files":

        return False, "delete_files blocked"

    # =========================
    # VALIDATE PATHS
    # =========================
    path = (
        params.get("path")
        or params.get("to")
        or ""
    )

    for blocked in BLOCKED_PATHS:

        if blocked.lower() in path.lower():

            return False, (
                f"Blocked path: {blocked}"
            )

    # =========================
    # VALIDATE URLS
    # =========================
    url = params.get(
        "url",
        ""
    )

    for domain in BLOCKED_DOMAINS:

        if domain in url.lower():

            return False, (
                f"Blocked domain: {domain}"
            )

    return True, "safe"