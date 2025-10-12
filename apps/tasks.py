import time

from celery import shared_task
from django.core.mail import send_mail

@shared_task
def add(x, y):
    time.sleep(2)
    return x + y

