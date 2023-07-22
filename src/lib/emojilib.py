import re

flag_mapping = {
    "AD": "🇦🇩", 
    "AE": "🇦🇪", 
    "AF": "🇦🇫", 
    "AG": "🇦🇬", 
    "AI": "🇦🇮", 
    "AL": "🇦🇱", 
    "AM": "🇦🇲", 
    "AO": "🇦🇴", 
    "AQ": "🇦🇶", 
    "AR": "🇦🇷", 
    "AS": "🇦🇸", 
    "AT": "🇦🇹", 
    "AU": "🇦🇺", 
    "AW": "🇦🇼", 
    "AX": "🇦🇽", 
    "AZ": "🇦🇿", 
    "BA": "🇧🇦", 
    "BB": "🇧🇧", 
    "BD": "🇧🇩", 
    "BE": "🇧🇪", 
    "BF": "🇧🇫", 
    "BG": "🇧🇬", 
    "BH": "🇧🇭", 
    "BI": "🇧🇮", 
    "BJ": "🇧🇯", 
    "BL": "🇧🇱", 
    "BM": "🇧🇲", 
    "BN": "🇧🇳", 
    "BO": "🇧🇴", 
    "BQ": "🇧🇶", 
    "BR": "🇧🇷", 
    "BS": "🇧🇸", 
    "BT": "🇧🇹", 
    "BV": "🇧🇻", 
    "BW": "🇧🇼", 
    "BY": "🇧🇾", 
    "BZ": "🇧🇿", 
    "CA": "🇨🇦", 
    "CC": "🇨🇨", 
    "CD": "🇨🇩", 
    "CF": "🇨🇫", 
    "CG": "🇨🇬", 
    "CH": "🇨🇭", 
    "CI": "🇨🇮", 
    "CK": "🇨🇰", 
    "CL": "🇨🇱", 
    "CM": "🇨🇲", 
    "CN": "🇨🇳", 
    "CO": "🇨🇴", 
    "CR": "🇨🇷", 
    "CU": "🇨🇺", 
    "CV": "🇨🇻", 
    "CW": "🇨🇼", 
    "CX": "🇨🇽", 
    "CY": "🇨🇾", 
    "CZ": "🇨🇿", 
    "DE": "🇩🇪", 
    "DJ": "🇩🇯", 
    "DK": "🇩🇰", 
    "DM": "🇩🇲", 
    "DO": "🇩🇴", 
    "DZ": "🇩🇿", 
    "EC": "🇪🇨", 
    "EE": "🇪🇪", 
    "EG": "🇪🇬", 
    "EH": "🇪🇭", 
    "ER": "🇪🇷", 
    "ES": "🇪🇸", 
    "ET": "🇪🇹", 
    "FI": "🇫🇮", 
    "FJ": "🇫🇯", 
    "FK": "🇫🇰", 
    "FM": "🇫🇲", 
    "FO": "🇫🇴", 
    "FR": "🇫🇷", 
    "GA": "🇬🇦", 
    "GB": "🇬🇧", 
    "GD": "🇬🇩", 
    "GE": "🇬🇪", 
    "GF": "🇬🇫", 
    "GG": "🇬🇬", 
    "GH": "🇬🇭", 
    "GI": "🇬🇮", 
    "GL": "🇬🇱", 
    "GM": "🇬🇲", 
    "GN": "🇬🇳", 
    "GP": "🇬🇵", 
    "GQ": "🇬🇶", 
    "GR": "🇬🇷", 
    "GS": "🇬🇸", 
    "GT": "🇬🇹", 
    "GU": "🇬🇺", 
    "GW": "🇬🇼", 
    "GY": "🇬🇾", 
    "HK": "🇭🇰", 
    "HM": "🇭🇲", 
    "HN": "🇭🇳", 
    "HR": "🇭🇷", 
    "HT": "🇭🇹", 
    "HU": "🇭🇺", 
    "ID": "🇮🇩", 
    "IE": "🇮🇪", 
    "IL": "🇮🇱", 
    "IM": "🇮🇲", 
    "IN": "🇮🇳", 
    "IO": "🇮🇴", 
    "IQ": "🇮🇶", 
    "IR": "🇮🇷", 
    "IS": "🇮🇸", 
    "IT": "🇮🇹", 
    "JE": "🇯🇪", 
    "JM": "🇯🇲", 
    "JO": "🇯🇴", 
    "JP": "🇯🇵", 
    "KE": "🇰🇪", 
    "KG": "🇰🇬", 
    "KH": "🇰🇭", 
    "KI": "🇰🇮", 
    "KM": "🇰🇲", 
    "KN": "🇰🇳", 
    "KP": "🇰🇵", 
    "KR": "🇰🇷", 
    "KW": "🇰🇼", 
    "KY": "🇰🇾", 
    "KZ": "🇰🇿", 
    "LA": "🇱🇦", 
    "LB": "🇱🇧", 
    "LC": "🇱🇨", 
    "LI": "🇱🇮", 
    "LK": "🇱🇰", 
    "LR": "🇱🇷", 
    "LS": "🇱🇸", 
    "LT": "🇱🇹", 
    "LU": "🇱🇺", 
    "LV": "🇱🇻", 
    "LY": "🇱🇾", 
    "MA": "🇲🇦", 
    "MC": "🇲🇨", 
    "MD": "🇲🇩", 
    "ME": "🇲🇪", 
    "MF": "🇲🇫", 
    "MG": "🇲🇬", 
    "MH": "🇲🇭", 
    "MK": "🇲🇰", 
    "ML": "🇲🇱", 
    "MM": "🇲🇲", 
    "MN": "🇲🇳", 
    "MO": "🇲🇴", 
    "MP": "🇲🇵", 
    "MQ": "🇲🇶", 
    "MR": "🇲🇷", 
    "MS": "🇲🇸", 
    "MT": "🇲🇹", 
    "MU": "🇲🇺", 
    "MV": "🇲🇻", 
    "MW": "🇲🇼", 
    "MX": "🇲🇽", 
    "MY": "🇲🇾", 
    "MZ": "🇲🇿", 
    "NA": "🇳🇦", 
    "NC": "🇳🇨", 
    "NE": "🇳🇪", 
    "NF": "🇳🇫", 
    "NG": "🇳🇬", 
    "NI": "🇳🇮", 
    "NL": "🇳🇱", 
    "NO": "🇳🇴", 
    "NP": "🇳🇵", 
    "NR": "🇳🇷", 
    "NU": "🇳🇺", 
    "NZ": "🇳🇿", 
    "OM": "🇴🇲", 
    "PA": "🇵🇦", 
    "PE": "🇵🇪", 
    "PF": "🇵🇫", 
    "PG": "🇵🇬", 
    "PH": "🇵🇭", 
    "PK": "🇵🇰", 
    "PL": "🇵🇱", 
    "PM": "🇵🇲", 
    "PN": "🇵🇳", 
    "PR": "🇵🇷", 
    "PS": "🇵🇸", 
    "PT": "🇵🇹", 
    "PW": "🇵🇼", 
    "PY": "🇵🇾", 
    "QA": "🇶🇦", 
    "RE": "🇷🇪", 
    "RO": "🇷🇴", 
    "RS": "🇷🇸", 
    "RU": "🇷🇺", 
    "RW": "🇷🇼", 
    "SA": "🇸🇦", 
    "SB": "🇸🇧", 
    "SC": "🇸🇨", 
    "SD": "🇸🇩", 
    "SE": "🇸🇪", 
    "SG": "🇸🇬", 
    "SH": "🇸🇭", 
    "SI": "🇸🇮", 
    "SJ": "🇸🇯", 
    "SK": "🇸🇰", 
    "SL": "🇸🇱", 
    "SM": "🇸🇲", 
    "SN": "🇸🇳", 
    "SO": "🇸🇴", 
    "SR": "🇸🇷", 
    "SS": "🇸🇸", 
    "ST": "🇸🇹", 
    "SV": "🇸🇻", 
    "SX": "🇸🇽", 
    "SY": "🇸🇾", 
    "SZ": "🇸🇿", 
    "TC": "🇹🇨", 
    "TD": "🇹🇩", 
    "TF": "🇹🇫", 
    "TG": "🇹🇬", 
    "TH": "🇹🇭", 
    "TJ": "🇹🇯", 
    "TK": "🇹🇰", 
    "TL": "🇹🇱", 
    "TM": "🇹🇲", 
    "TN": "🇹🇳", 
    "TO": "🇹🇴", 
    "TR": "🇹🇷", 
    "TT": "🇹🇹", 
    "TV": "🇹🇻", 
    "TW": "🇹🇼", 
    "TZ": "🇹🇿", 
    "UA": "🇺🇦", 
    "UG": "🇺🇬", 
    "UM": "🇺🇲", 
    "US": "🇺🇸", 
    "UY": "🇺🇾", 
    "UZ": "🇺🇿", 
    "VA": "🇻🇦", 
    "VC": "🇻🇨", 
    "VE": "🇻🇪", 
    "VG": "🇻🇬", 
    "VI": "🇻🇮", 
    "VN": "🇻🇳", 
    "VU": "🇻🇺", 
    "WF": "🇼🇫", 
    "WS": "🇼🇸", 
    "YE": "🇾🇪", 
    "YT": "🇾🇹", 
    "ZA": "🇿🇦", 
    "ZM": "🇿🇲", 
    "ZW": "🇿🇼"
}

custom_mapping = {
    "frfr": "🇫🇷",
    "hungry": "🇭🇺",
    "hungy": "🇭🇺",
}

# todo: implement
# # will always appear as reaction even if no other checks pass (like number of relevant emojis found)
# always_appear_mapping = {
#     "forgor": "💀",
#     "meow": "🐱",
# }

def uppercase_dict_keys(d: dict):
    return {key.upper(): value for key, value in d.items()}

combined_mapping = {
    **flag_mapping, 
    **uppercase_dict_keys(custom_mapping)
}


def get_relevant_emojis(text: str, contiguous_mode = True):
    emoji_sequence = find_matches(text, combined_mapping)

    if contiguous_mode:
        relevant = []
        if len(emoji_sequence) == 1:
            relevant = [emoji_sequence[0][0]]
        else:
            for i, (emoji, match_index) in enumerate(emoji_sequence):
                # not the last element, compare to next element
                if i < len(emoji_sequence) - 1:
                    if match_index == emoji_sequence[i + 1][1] - 1:
                        relevant.append(emoji)
                        continue

                # not the first element, compare to previous element
                if i > 0:
                    if match_index == emoji_sequence[i - 1][1] + 1:
                        relevant.append(emoji)
                        continue
                
    else:
        relevant = [x[0] for x in emoji_sequence]
    
    if (
        len(relevant) >= 3
        or len(relevant) == len(text.split(' '))
    ):
        return relevant
    else:
        return []

def find_matches(text: str, mapping: dict[str, str]):
    text = text.upper()

    emoji_sequence = []
    words = text.split(' ')
    for word_index, word in enumerate(words):
        word = word.upper()
        if word in mapping.keys():
            emoji = mapping[word]
            emoji_sequence.append((emoji, word_index))

    return emoji_sequence


def is_custom_emoji(name: str):
    return re.match('^[a-zA-Z0-9_]+$', name)