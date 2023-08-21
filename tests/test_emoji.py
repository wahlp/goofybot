import pytest

from src.lib import emojilib

@pytest.mark.parametrize(
    "test_input,expected", 
    [
        ("im in it", ["🇮🇲", "🇮🇳", "🇮🇹"]),
        ("us fr", ["🇺🇸", "🇫🇷"]),    
        ("amongus", []),
        ("im not in vc", []),
        ("im up but no one else is", []),
        ("my name is in it", ["🇮🇸", "🇮🇳", "🇮🇹"]),
        ("what is cunny?", ["🦀"]),
        ("i forgor", ["💀"]),
        ("i forgor i was in vc", ["💀", "🇮🇳", "🇻🇨"]),
        ("meowdy", ["🐱"]),
        ("you forgor to say meowdy", ["💀", "🐱"]),
        ("https://tenor.com/view/samgyetang-korean-chicken-broth-soup-gif-10392734", ["🐔"])
    ]
)
def test_get_relevant_emojis(test_input, expected):
    assert emojilib.get_relevant_emojis(test_input) == expected