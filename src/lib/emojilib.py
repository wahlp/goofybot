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
    "cunny": "🦀"
})

class WordMatch(NamedTuple):
    emoji: str 
    word_index: int
    filterable: bool

class SubstringMatch(NamedTuple):
    emoji: str
    index: int
    filterable: bool

def get_relevant_emojis(text: str, contiguous_mode = True):
    text = remove_symbols(text.upper())

    emoji_sequence_filterable = find_word_matches(text, combined_mapping, True)
    emoji_sequence_unfilterable = find_word_matches(text, always_appear_mapping, False)

    emoji_sequence = sorted(
        (*emoji_sequence_filterable, *emoji_sequence_unfilterable),
        key=lambda x: x[1]
    )

    if contiguous_mode:
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
                    # not the last element, compare to next element
                    # keep if the next word was also a match
                    if i < len(emoji_sequence) - 1:
                        if tup.word_index == emoji_sequence[i + 1].word_index - 1:
                            relevant.append(tup)
                            continue
                    # not the first element, compare to previous element
                    # keep if the previous word was also a match
                    if i > 0:
                        if tup.word_index == emoji_sequence[i - 1].word_index + 1:
                            relevant.append(tup)
                            continue
    else:
        relevant = emoji_sequence
    
    if (
        len(relevant) >= 3
        or len(relevant) == len(text.split(' '))
    ):
        return [x.emoji for x in relevant]
    else:
        return [x.emoji for x in relevant if not x.filterable]

def find_word_matches(text: str, mapping: dict[str, str], filterable: bool):
    emoji_sequence: list[WordMatch] = []
    words = text.split(' ')
    for word_index, word in enumerate(words):
        if word in mapping.keys():
            emoji = mapping[word]
            emoji_sequence.append(WordMatch(emoji, word_index, filterable))

    return emoji_sequence

def remove_symbols(text: str):
    symbols = ["`", "~", "!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "_", "-", "+",
           "=", "{", "[", "]", "}", "|", "\\", ":", ";", "\"", "<", ",", ">", ".", "?", "/"]
    translation_table = str.maketrans({k: ' ' for k in symbols})
    text = text.translate(translation_table)
    return text

def is_custom_emoji(name: str):
    return re.match('^[a-zA-Z0-9_]+$', name)