import google.generativeai as genai
from io import BytesIO
from celery import shared_task
from .config import GOOGLE_API_KEY, GEMINI_PROMPT

@shared_task
def gemini_upload_and_chat(bytes: bytes, mime: str, prompt: str = GEMINI_PROMPT, model: str = "gemini-1.5-flash") -> str:
    genai.configure(api_key=GOOGLE_API_KEY)
    gemini = genai.GenerativeModel(model)
    myfile = genai.upload_file(BytesIO(bytes), mime_type=mime)
    response = gemini.generate_content([prompt, myfile])
    print (response)
    return response._result.candidates[0].content.parts[0].text
