import asyncio
import base64
import io
import multiprocessing
import os
from asyncio import Queue
from concurrent.futures import ProcessPoolExecutor

import torch
import uvicorn
from fastapi import FastAPI, UploadFile, File
from fastapi import Request
from marker.output import text_from_rendered

from models.FlagEmbeddingModels import flag_embedding_model_manager
from models.SuryaModel import suryaModel
from config import config

app = FastAPI(
    title="inference",
    description="RAG推理测",
)


def init_worker(device_queue: Queue):
    pid = os.getpid()
    suryaModel.load_model(
        dtype=torch.float16,
        device=device_queue.get(),
        pid=pid)


def dummy_task():
    return None


@app.on_event("startup")
async def startup_event():
    totalGPU = torch.cuda.device_count()

    manager = multiprocessing.Manager()
    device_queue = manager.Queue()

    cuda_available = True
    if totalGPU == 0 or not torch.cuda.is_available():
        cuda_available = False

    if totalGPU != 0 and config.ocr['device'] > totalGPU:
        raise ValueError(f"{config.ocr['device']} is larger than total GPU {totalGPU}")

    for i in range(config.ocr['device']):
        if cuda_available:
            for _ in range(config.ocr['works']):
                device_queue.put(f"cuda:{i}")
        else:
            for _ in range(config.ocr['works']):
                device_queue.put("cpu")

    app.state.executor = ProcessPoolExecutor(
        max_workers=config.ocr['works'] * config.ocr['device'],
        initializer=init_worker,
        initargs=(device_queue,)
    )
    futures = [app.state.executor.submit(dummy_task) for _ in range(config.ocr['works'] * config.ocr['device'])]
    for future in futures:
        future.result()  # 等待完成

    flag_embedding_model_manager.load_embedding_model()
    flag_embedding_model_manager.load_rerank_model()


@app.on_event("shutdown")
async def shutdown_event():
    app.state.executor.shutdown()


def _ocr(_bytes):
    pid = os.getpid()
    model = suryaModel.models[pid]
    rendered = model(_bytes)
    _text, _, _images = text_from_rendered(rendered)
    for key in _images.keys():
        image = _images[key]
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG")
        _images[key] = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return _text, _images


@app.post("/ocr")
async def ocr(file: UploadFile = File(...), request: Request = None):
    data = await file.read()
    loop = asyncio.get_event_loop()
    executor = request.app.state.executor

    text, images = await loop.run_in_executor(executor, _ocr, io.BytesIO(data))

    return {
        "text": text,
        "images": images
    }


def _embedding(embedding_model, texts):
    embeddings = embedding_model.encode(texts, return_sparse=True)
    dense = embeddings['dense_vecs']
    sparse = embeddings['lexical_weights']
    result = []
    for t, d, s in zip(texts, dense, sparse):
        result.append({
            "text": t,
            "dense": d.tolist(),
            "sparse": {k: float(v) for k, v in s.items()}
        })
    return result


def _rerank(reranker_model, p):
    return reranker_model.compute_score(p, normalize=True)


from concurrent.futures import ThreadPoolExecutor

thread_executor = ThreadPoolExecutor(max_workers=24)


@app.post("/embedding")
async def embedding(texts: list[str]):
    if texts is None or len(texts) == 0:
        return None

    return await asyncio.get_event_loop().run_in_executor(thread_executor, _embedding,
                                                          flag_embedding_model_manager.embedding_model,
                                                          texts)


@app.post("/rerank")
async def rerank(pairs: list[list]):
    return await asyncio.get_event_loop().run_in_executor(thread_executor, _rerank,
                                                          flag_embedding_model_manager.rerank_model,
                                                          pairs)


if __name__ == '__main__':
    uvicorn.run(app, host=config.server['host'], port=config.server['port'])
