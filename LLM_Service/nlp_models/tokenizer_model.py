from typing import List, Text

import regex
from rasa.utils.io import get_emoji_regex
from singleton_decorator import singleton


@singleton
class WhitespaceTokenizer:
    def __init__(self):
        self._emoji_pattern = get_emoji_regex()

    def _remove_emoji(self, text: Text) -> Text:
        """Remove emoji if the full text, aka token, matches the emoji regex."""
        match = self._emoji_pattern.fullmatch(text)

        if match is not None:
            return ""

        return text

    def tokenize(self, text) -> List:
        # we need to use regex instead of re, because of
        # https://stackoverflow.com/questions/12746458/python-unicode-regular-expression-matching-failing-with-some-unicode-characters

        # remove 'not a word character' if
        words = regex.sub(
            # there is a space or an end of a string after it
            r"[^\w#@&]+(?=\s|$)|"
            # there is a space or beginning of a string before it
            # not followed by a number
            r"(\s|^)[^\w#@&]+(?=[^0-9\s])|"
            # not in between numbers and not . or @ or & or - or #
            # e.g. 10'000.00 or blabla@gmail.com
            # and not url characters
            r"(?<=[^0-9\s])[^\w._~:/?#\[\]()@!$&*+,;=-]+(?=[^0-9\s])",
            " ",
            text,
        ).split()

        words = [clean_word for w in words if (clean_word := self._remove_emoji(w))]

        # if we removed everything like smiles `:)`, use the whole text as 1 token
        if not words:
            words = [text]
        return words
