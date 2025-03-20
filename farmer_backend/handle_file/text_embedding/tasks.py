from celery import shared_task
# from ..celery import app
from tools import async_to_sync, split_sentences, generate_embeddings, cosine_distance, logger, average_embeddings, merge_fragments
import numpy as np
from .qdrant_models import create_or_get_collection, upsert_task
from celery import shared_task, chord, chain
# from ..celery import app

@shared_task(name="create_chunks")
def create_chunks(embeddings: list[list[float]], distances: list[float], sentences: list[str], threshold_percentile=95) -> dict[str, list[float]]:
    merged_sentences = merge_fragments(sentences)
    breakpoint_threshold = round(np.percentile(distances, threshold_percentile), 2)
    breakpoints = [i for i, dist in enumerate(distances) if dist > breakpoint_threshold]

    chunks = {}
    start = 0
    for end in breakpoints + [len(merged_sentences)]:
        # Join with a space to preserve word boundaries
        chunk_text = ' '.join(merged_sentences[start:end+1])
        chunk_embedding = average_embeddings([np.array(embed) for embed in embeddings[start:end+1]])
        chunks[chunk_text] = chunk_embedding
        start = end + 1
    return chunks

    # for end in breakpoints + [len(sentences)]:
    #     chunk = ' '.join(sentences[start:end+1])
    #     chunks.append(chunk)
    #     start = end + 1
    

@shared_task(name="add_to_qdrant")
def add_to_qdrant(text: str, source: str, collection_name: str):
    """Splits text into sentences and processes embeddings."""
    logger.info(f"Adding text to Qdrant: {text}")

    sentences = split_sentences(text)  # Step 1: Split text
    # combined_sentences = combine_context(sentences)  # Add context

    # ✅ Create a Celery task chain (does NOT block the worker)
    task_chain = chain(
        generate_embeddings.s(sentences),  # Step 2: Generate embeddings
        process_embeddings.s(sentences, text),  # Step 3: Process embeddings
        upsert_task.s(source, collection_name)  # Step 4: Store in Qdrant
    )

    return task_chain.apply_async()  # ✅ Returns AsyncResult (keeps tasks async)



@shared_task(name="process_embeddings")
def process_embeddings(embeddings, text, combined_sentences):
    """Processes embeddings and creates chunks."""
    if len(embeddings) < 2:
        # ✅ Convert `text` to a string using `.join()` if it’s a list
        text_key = " ".join(text) if isinstance(text, list) else str(text)
        return {text_key: embeddings[0] if embeddings else []}

    # Compute cosine distances
    distances = [
        cosine_distance(np.array(embeddings[i]), np.array(embeddings[i + 1]))
        for i in range(len(embeddings) - 1)
    ]
    
    print('Creating final chunks...')
    chunks = create_chunks(embeddings, distances, combined_sentences)
    return chunks  # ✅ No dictionary key issue
