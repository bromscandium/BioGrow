import base64
import aiohttp
import openai
from .config import OPENAI_API
import numpy as np
from PIL import Image
# from gemini import gemini_upload_and_chat
from openai import AsyncOpenAI
from io import BytesIO
import cv2
import json
# from pydantic import BaseModel
# from celery import shared_task
from .mylogger import logger

async def call_openai_api(conversation: list[dict], json_schema: str = None, model: str = "gpt-4o-mini") -> str:
    """
    Asynchronously call the OpenAI API and return the parsed response content as a string.
    """
    client = openai.Client()
    client.api_key = OPENAI_API  # Ensure OPENAI_API is defined correctly

    params = {
        "model": model,
        "messages": conversation,
        "temperature": 0.7,
        "max_tokens": 15000,
    }
    if json_schema is not None:
        params["response_format"] = json_schema

    try:
        response = client.beta.chat.completions.parse(**params)
        logger.info("Full response: %s", response)
        
        content = response.choices[0].message.content.strip()
        logger.info("Content: %s", content)
        
        if not content:
            raise ValueError("OpenAI API returned an empty response")

        return content
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        raise e


def load_image(image_bytes):
    # Ensure the image file is opened correctly
    print("Type of image_bytes:", type(image_bytes))

    image = Image.open(BytesIO(image_bytes))
    image = image.convert('RGB')  # Ensure image is in RGB format
    image_array = np.array(image)
    return image_array

async def fetch_image_text(session, api_key, base64_image):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "What is on the image?"
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                    }
                ]
            }
        ],
        "max_tokens": 300
    }

    async with session.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload) as response:
        result = await response.json()
        return result['choices'][0]['message']['content']


async def getWhatOnImage(image_bytes):
    # OpenAI API Key
    api_key = OPENAI_API

    image = load_image(image_bytes)
    _, buffer = cv2.imencode('.jpg', image)
    base64_image = base64.b64encode(buffer.tobytes()).decode('utf-8')

    # async with aiohttp.ClientSession() as session:
    #     tasks = fetch_image_text(session, api_key, base64_image)
    #     results = await asyncio.gather(*tasks)
    async with aiohttp.ClientSession() as session:
        results = await fetch_image_text(session, api_key, base64_image)
    return results



async def get_openai_embeddings(
    texts: list[str],
    model: str = "text-embedding-3-small",
    base_url: str = None,
) -> np.ndarray:
    openai.api_key = OPENAI_API
    openai_async_client = (
        AsyncOpenAI() if base_url is None else AsyncOpenAI(base_url=base_url)
    )
    response = await openai_async_client.embeddings.create(
        model=model, input=texts, encoding_format="float"
    )
  
    return np.array([dp.embedding for dp in response.data])
