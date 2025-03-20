from celery import Celery
import os

celery = Celery('farmer_celery',
                broker=os.getenv('CELERY_BROKER_URL',),
                backend=os.getenv('CELERY_RESULT_BACKEND'))

import handle_file
celery.autodiscover_tasks(['farmer_backend'])
