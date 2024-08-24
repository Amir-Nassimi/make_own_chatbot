from typing import Any, Dict, List, Text

import rasa.shared.utils.io
import rasa.utils.io
import requests
from rasa.engine.recipes.default_recipe import DefaultV1Recipe
from rasa.nlu.tokenizers.tokenizer import Token
from rasa.nlu.tokenizers.whitespace_tokenizer import WhitespaceTokenizer
from rasa.shared.constants import DOCS_URL_COMPONENTS
from rasa.shared.nlu.training_data.message import Message


@DefaultV1Recipe.register(
    DefaultV1Recipe.ComponentType.MESSAGE_TOKENIZER, is_trainable=False
)
class CustumWhitespaceTokenizer(WhitespaceTokenizer):
    api_url = ""

    @classmethod
    def get_default_config(cls) -> Dict[Text, Any]:
        """Returns the component's default config."""
        return {
            # Flag to check whether to split intents
            "intent_tokenization_flag": False,
            # Symbol on which intent should be split
            "intent_split_symbol": "_",
            # Regular expression to detect tokens
            "token_pattern": None,
            # Symbol on which prefix should be split
            "prefix_separator_symbol": None,
            "api_url": cls.api_url,
        }

    def __init__(self, config: Dict[Text, Any]) -> None:
        super().__init__(config)
        self.api_url = config.get("api_url", None)

        if "case_sensitive" in self._config:
            rasa.shared.utils.io.raise_warning(
                "The option 'case_sensitive' was moved from the tokenizers to the "
                "featurizers.",
                docs=DOCS_URL_COMPONENTS,
            )

    def tokenize(self, message: Message, attribute: Text) -> List[Token]:
        text = message.get(attribute)

        response = requests.post(self.api_url, json={"text": text})
        if response.status_code == 200:
            words = response.json()["tokens"]
            tokens = self._convert_words_to_tokens(words, text)
            return self._apply_token_pattern(tokens)
        else:
            raise ValueError(f"Error from Tokenizer API: {response.text}")
