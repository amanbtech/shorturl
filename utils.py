import random
import string
import re


def short_coder():
    return "".join(
        random.choices(
            string.ascii_letters + string.digits,
            k=6
        )
    )


def validate_custom_code(custom_code: str):
    if custom_code.strip() == "":
        return False, "short code cannot be empty"

    if len(custom_code) > 20:
        return False, "short code too long"

    if not re.match(r"^[a-zA-Z0-9_-]+$", custom_code):
        return False, "not valid"

    return True, None