import os, sys
from pathlib import Path
from torch import no_grad
from singleton_decorator import singleton
from sentence_transformers import SentenceTransformer
from torch.cuda import is_available as Cuda_Available

sys.path.append(os.path.abspath(Path(__file__).resolve().parents[1]))
from config import Config



@singleton
class LaBSEModel:
    def __init__(self):
        self._device = 'cuda' if Cuda_Available() else 'cpu'
        self._model = self.init_model(Config().NLP_Model)
        self.warmup()

    def init_model(self, model_name):
        return SentenceTransformer(model_name, device=self._device)
    
    def warmup(self):
        sentences = ['hi']
        with no_grad():
            self._model.encode(sentences=sentences, device=self._device, normalize_embeddings=Config().NLP_Normalization)

    def encoding(self, sentences):
        print(f'sentences are {sentences}')
        with no_grad():
            embd = self._model.encode(sentences=sentences, device=self._device, normalize_embeddings=Config().NLP_Normalization)
            return embd
    
    def similarity(self, embeddings_1, embeddings_2):
        if Config().NLP_Normalization:
            if len(embeddings_1) != len(embeddings_2):
                raise ValueError("Vectors must be of the same length")
            return sum(v1 * v2 for v1, v2 in zip(embeddings_1, embeddings_2))
        
        else:
            with no_grad():
                return self._model.similarity(embeddings_1, embeddings_2).tolist()
    