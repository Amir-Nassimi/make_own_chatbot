from typing import Any, Dict, List, Text

import numpy as np
import requests
from rasa.engine.graph import ExecutionContext, GraphComponent
from rasa.engine.recipes.default_recipe import DefaultV1Recipe
from rasa.engine.storage.resource import Resource
from rasa.engine.storage.storage import ModelStorage
from rasa.shared.nlu.constants import TEXT
from rasa.shared.nlu.training_data.features import Features
from rasa.shared.nlu.training_data.message import Message
from rasa.shared.nlu.training_data.training_data import TrainingData



@DefaultV1Recipe.register(
    DefaultV1Recipe.ComponentType.MESSAGE_FEATURIZER, is_trainable=False
)
class LaBSEEmbedder(GraphComponent):
    api_url = ""

    def __init__(self, config: Dict[Text, Any]) -> None:
        self.api_url = config.get("api_url", None)

    @classmethod
    def get_default_config(cls) -> Dict[Text, Any]:
        return {"api_url": cls.api_url}

    def process(self, messages: List[Message]) -> List[Message]:
        for message in messages:
            text = message.get(TEXT)

            embeddings = self._get_embeddings(text)
            feature = Features(
                features=embeddings,
                feature_type="sequence",
                origin="LaBSEEmbedder",
                attribute=TEXT,
            )
            message.add_features(feature)
        return messages

    def process_training_data(self, training_data: TrainingData) -> TrainingData:
        for message in training_data.training_examples:
            text = message.get(TEXT)

            embeddings = self._get_embeddings(text)
            feature = Features(
                features=embeddings,
                feature_type="sequence",
                origin="LaBSEEmbedder",
                attribute=TEXT,
            )
            message.add_features(feature)

        return training_data

    def _get_embeddings(self, text: str) -> List[float]:
        response = requests.post(self.api_url, json={"text": [text]})
        if response.status_code == 200:
            embeddings = response.json()["embeddings"]
            embeddings_array = np.array(embeddings).squeeze()
            return embeddings_array[1:-1] #Avoid [CLS] Token and [SEP] Token
        else:
            raise ValueError(f"Error from LaBSE API: {response.text}")

    @classmethod
    def create(
        cls,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
    ) -> "LaBSEEmbedder":
        return cls(config)