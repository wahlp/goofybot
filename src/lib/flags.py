import json
import os

def flagify(code: list[str]) -> str:
    """Convert letters to regional indicators"""

    offset = 127397
    return "".join([chr(ord(c.upper()) + offset) for c in code])

def load_flag_mapping():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, "..", "data", "country-codes.json")

    with open(file_path) as f:
        country_codes = json.load(f)

    return {x: flagify(x) for x in country_codes}
