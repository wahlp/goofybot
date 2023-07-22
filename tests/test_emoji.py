import pytest

from src.lib import emojilib

@pytest.mark.parametrize(
    "test_input,expected", 
    [
        ("im in it", ["🇮🇲", "🇮🇳", "🇮🇹"]),
        ("us fr", ["🇺🇸", "🇫🇷"]),
        ("amongus", []),
        ("im not in vc", ["🇮🇳", "🇻🇨"]),
        ("im up but no one else is", [])
    ]
)
def test_get_relevant_emojis(test_input, expected):
    assert emojilib.get_relevant_emojis(test_input) == expected