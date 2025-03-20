import numpy as np
# from google import genai
# from rag_app.config import get_google_api_key
from .openai_tools import get_openai_embeddings
import asyncio
from celery import shared_task, group
import re

# client = genai.Client(api_key=get_google_api_key())

def merge_fragments(sentences: list[str], min_length: int = 20) -> list[str]:
    merged = []
    buffer = ""
    for fragment in sentences:
        if len(fragment) < min_length or not re.search(r'[.?!]$', fragment):
            buffer += fragment + " "
        else:
            if buffer:
                merged.append(buffer.strip() + " " + fragment)
                buffer = ""
            else:
                merged.append(fragment)
    if buffer:
        merged.append(buffer.strip())
    return merged

def clean_text(text: str) -> str:
    # Replace multiple whitespace with a single space
    text = re.sub(r'\s+', ' ', text)
    # Remove spaces between letters (use with caution)
    text = re.sub(r'(?<=\w) (?=\w)', '', text)
    return text.strip()

def split_sentences(text: str) -> list[str]:
    cleaned_text = clean_text(text)
    # If punctuation is unreliable, split on newlines instead
    sentences = re.split(r'\n+', cleaned_text)
    return sentences

def merge_fragments(sentences: list[str], min_length: int = 20) -> list[str]:
    merged = []
    buffer = ""
    for fragment in sentences:
        if len(fragment) < min_length or not re.search(r'[.?!]$', fragment):
            buffer += fragment + " "
        else:
            if buffer:
                merged.append(buffer.strip() + " " + fragment)
                buffer = ""
            else:
                merged.append(fragment)
    if buffer:
        merged.append(buffer.strip())
    return merged

@shared_task
def cosine_distance(a: np.ndarray, b: np.ndarray) -> float:
    """Calculate cosine distance between two vectors."""
    a = a.flatten()
    b = b.flatten()
    return 1 - (np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

# 
# def generate_embeddings(sentences: list[str]) -> list[np.ndarray]:
#     tasks = [
#         group(
#             get_openai_embeddings.s([sentence])

#         for sentence in sentences
#         )
#     ]
#     # responses = await asyncio.gather(*tasks)
#     # # Filter out any None responses (if any)
#     # responses = [await resp for resp in responses if resp is not None]
#     # if len(responses) != len(sentences):
#     #     raise ValueError("Mismatch between number of embeddings and sentences.")
#     # print('responses:', responses)      
#     # # Extract the actual embedding vectors
#     return [task.delay().get() for task in tasks]

@shared_task(name="generate_embeddings")
def generate_embeddings(sentences: list[str]) -> list[list[float]]:
    """
    Generate embeddings using OpenAI API inside a Celery task.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    embeddings = loop.run_until_complete(get_openai_embeddings(sentences))
    loop.close()

    return [embedding.flatten().tolist() for embedding in embeddings]  # ✅ Returns all embeddings

def escape_markdown_v2(text: str) -> str:
    """
    Escapes reserved characters for MarkdownV2.
    Reserved characters are: _ * [ ] ( ) ~ ` > # + - = | { } . !
    """
    escape_chars = r'_*\[\]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)


@shared_task    
def average_embeddings(embeddings: list[np.ndarray]) -> list[float]:
    # Stack the embeddings into a 2D array and compute the mean along the first axis.
    return np.mean(np.stack(embeddings), axis=0).flatten().tolist()
