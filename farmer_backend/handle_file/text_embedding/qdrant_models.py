from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct, Filter, FieldCondition, MatchValue
from tools import get_openai_embeddings, QDRANT_CLIENT_HOST
import uuid
from celery import shared_task
from qdrant_client.http.exceptions import ApiException

import logging

logger = logging.getLogger(__name__)

def get_client():
    return QdrantClient(QDRANT_CLIENT_HOST)

def create_or_get_collection(collection_name: str, vector_size: int):
    """Ensures the Qdrant collection exists, creating it if necessary."""
    client = get_client()
    try:
        # First, check if the collection exists
        collections = client.get_collections()
        existing_collections = {col.name for col in collections.collections}

        if collection_name in existing_collections:
            logger.info(f"✅ Collection '{collection_name}' already exists.")
        else:
            logger.info(f"🚀 Creating new collection: {collection_name}")
            try:
                client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
                )
            except ApiException as e:
                if "already exists" in str(e):
                    logger.info(f"✅ Collection '{collection_name}' already exists (detected during creation).")
                else:
                    logger.error(f"❌ Error creating collection: {e}")
                    raise e
    except Exception as e:
        logger.error(f"❌ Error checking/creating collection: {e}")
        raise e

    return client

@shared_task(name="upsert_task")
def upsert_task(chunks, source: str, collection_name: str):
    # Recursively unwrap nested lists until we get a non-list (hopefully a dict)
    while isinstance(chunks, list) and len(chunks) == 1:
        chunks = chunks[0]

    if not isinstance(chunks, dict):
        logger.error("Expected a dictionary from the chord callback, but got: %s", chunks)
        return

    points = []
    for sentence, embedding in chunks.items():
        point = PointStruct(
            id=uuid.uuid4().hex,
            vector=embedding,
            payload={"chunk": sentence, "source": source},
        )
        points.append(point)

    client = create_or_get_collection(collection_name, 1536)  # Ensure collection exists

    try:
        client.upsert(collection_name=collection_name, points=points)
    except Exception as e:
        logger.error(f"Error upserting vectors: {e}")


async def query(query: str, collection_name: str, top_k=5, source: str=None):
    client = get_client()
    # Generate the embedding for the query
    embedding = await get_openai_embeddings([query])

    # # Define a filter
    # my_filter = Filter(
    #     must=[
    #         FieldCondition(
    #             key="source",  # Field name
    #             match=MatchValue(value=source),  # Condition: match this value
    #         )
    #     ]
    # )
    # Perform the search with filtering
    results = client.search(
        collection_name=collection_name,
        query_vector=embedding[0].tolist(),
        limit=top_k,
        with_payload=True,
        
        # filter=my_filter,
    )
    return results

def delete_collection(collection_name: str):
    client = get_client()
    try:
        client.delete_collection(collection_name=collection_name)
    except Exception as e:
        print(f"Error deleting collection: {e}")

def delete_document_from_collection(collection_name, document_source):
    client = get_client()
    # Create a filter for the deletion request

    filter_query = Filter(
            must=[
                FieldCondition(
                    key="source",  # Field name
                    match=MatchValue(value=document_source),  # Condition: match this value
                )
            ]
        )
    
    # Call the Qdrant upsert/delete API
    result = client.delete(
        collection_name=collection_name,
        points_selector=filter_query

    )
    return result