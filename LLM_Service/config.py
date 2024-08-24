from singleton_decorator import singleton


@singleton
class Config:
    def __init__(self):
        self._NLP_Normalization = False
        self._NLP_Tokenizer = "token_embeddings"
        self._NLP_Model = "sentence-transformers/LaBSE"

    @property
    def NLP_Model(self):
        return self._NLP_Model
    
    @property
    def NLP_Tokenizer(self):
        return self._NLP_Tokenizer

    @property
    def NLP_Normalization(self):
        return self._NLP_Normalization