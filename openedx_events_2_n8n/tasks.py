"""Celery tasks for sending data to n8n or another webhook."""

import logging

from celery import shared_task
from requests import exceptions, post

from openedx_events_2_n8n.utils import flatten_dict

N8N_REQUEST_TIMEOUT = 5
N8N_RETRY_COUNTDOWN = 3
log = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(exceptions.RequestException,),
    retry_backoff=True,
    retry_kwargs={"max_retries": N8N_RETRY_COUNTDOWN},
)
def send_data_to_n8n(self, webhook_url, data):  # pylint: disable=unused-argument
    """
    Send data to n8n using a webhook.

    Arguments:
        self: The task instance.
        webhook_url: The URL of the n8n webhook.
        data: The data to send to the webhook.
    """
    flattened_data = flatten_dict(data)
    try:
        log.info("Sending data to n8n: %s", flattened_data)
        post(webhook_url, json=flattened_data, timeout=N8N_REQUEST_TIMEOUT)
    except exceptions.RequestException as e:
        log.error("Error sending data to n8n: %s", e)
        raise
