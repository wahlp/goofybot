import re
from typing import NamedTuple

from .countryflags import flag_mapping


def uppercase_dict_keys(d: dict):
    return {key.upper(): value for key, value in d.items()}

custom_mapping = {
    "frfr": "🇫🇷",
    "hungry": "🇭🇺",
    "hungy": "🇭🇺",
}

combined_mapping = {
    **flag_mapping, 
    **uppercase_dict_keys(custom_mapping)
}

# will always appear as reaction even if no other checks pass (like number of relevant emojis found)
# should be checked as substrings and not individual words
always_appear_mapping = uppercase_dict_keys({
    "forgor": "💀",
    "meow": "🐱",
    "cunny": "🦀",
    "chicken": "🐔"
})


class Match(NamedTuple):
    emoji: str
    filterable: bool
    char_index: int
    word_index: int = -1

def get_relevant_emojis(text: str):
    text = remove_symbols(text.upper())

    emoji_sequence_filterable = find_word_matches(text, combined_mapping, True)
    emoji_sequence_unfilterable = find_substring_matches(text, always_appear_mapping, False)

    emoji_sequence = sorted(
        (*emoji_sequence_filterable, *emoji_sequence_unfilterable),
        key=lambda x: x.char_index
    )

    relevant = check_contiguousness(emoji_sequence)
    
    if (
        len(relevant) >= 3
        or len(relevant) == len(text.split())
    ):
        return [x.emoji for x in relevant]
    else:
        return [x.emoji for x in relevant if not x.filterable]


def check_contiguousness(emoji_sequence: list[Match]):
    """Infer whether the matched reactions deserved to be acted upon.
    Based on the adjacency of the words that triggered matches
    """
    if len(emoji_sequence) == 1:
        relevant = [emoji_sequence[0]]
    else:
        # only include if there is a neighbouring reactable word
        # or it came from an unfilterable match
        relevant = []
        for i, tup in enumerate(emoji_sequence):
            if not tup.filterable:
                relevant.append(tup)
            else:
                # keep if the next word was also a match
                if i < len(emoji_sequence) - 1:
                    next_tup = emoji_sequence[i + 1]
                    if tup.word_index == next_tup.word_index - 1:
                        relevant.append(tup)
                        continue
                # keep if the previous word was also a match
                if i > 0:
                    prev_tup = emoji_sequence[i - 1]
                    if tup.word_index == prev_tup.word_index + 1:
                        relevant.append(tup)
                        continue
    return relevant

def find_word_matches(text: str, mapping: dict[str, str], filterable: bool):
    emoji_sequence: list[Match] = []
    words = text.split()
    
    char_index = 0
    for word_index, word in enumerate(words):
        emoji = mapping.get(word)
        if emoji is not None:
            emoji_sequence.append(Match(emoji, filterable, char_index, word_index))
        char_index += len(word) + 1

    return emoji_sequence

def find_substring_matches(text: str, mapping: dict[str, str], filterable: bool):
    emoji_sequence: list[Match] = []
    words = text.split()

    for trigger, emoji in mapping.items():
        index = text.find(trigger)
        if index != -1:
            word_index = -1
            for i, word in enumerate(words):
                if index >= text.find(word) and index < text.find(word) + len(word):
                    word_index = i
                    break
            emoji_sequence.append(Match(emoji, filterable, index, word_index))

    return emoji_sequence

def remove_symbols(text: str):
    symbols = ["`", "~", "!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "_", "-", "+",
           "=", "{", "[", "]", "}", "|", "\\", ":", ";", "\"", "<", ",", ">", ".", "?", "/"]
    translation_table = str.maketrans({k: ' ' for k in symbols})
    text = text.translate(translation_table)
    return text

def is_custom_emoji(name: str):
    return re.match('^[a-zA-Z0-9_]+$', name)