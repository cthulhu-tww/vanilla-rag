import torch
from FlagEmbedding import FlagAutoModel
from FlagEmbedding import FlagReranker


class FlagEmbeddingModelManager:
    def __init__(self):
        self.embedding_model = None
        self.rerank_model = None

    def load_embedding_model(self, model_path="BAAI/bge-m3", device="cuda" if torch.cuda.is_available() else "cpu"):
        self.embedding_model = FlagAutoModel.from_finetuned(model_path, use_fp16=True, devices=device)

    def load_rerank_model(self, model_path="BAAI/bge-reranker-v2-m3",
                          device="cuda" if torch.cuda.is_available() else "cpu"):
        self.rerank_model = FlagReranker(model_path, devices=device, use_fp16=True)


flag_embedding_model_manager = FlagEmbeddingModelManager()
