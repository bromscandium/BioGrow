from .openai_tools import getWhatOnImage
from .asyncio_tools import async_to_sync
from celery import shared_task


@shared_task
def getWhatonImage_celery(image_bytes):
    return async_to_sync(getWhatOnImage, image_bytes)