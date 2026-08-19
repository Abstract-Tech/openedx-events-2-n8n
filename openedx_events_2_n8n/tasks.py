"""Celery tasks for sending data to n8n or another webhook."""

import logging
import time

import jwt
from celery import shared_task
from django.core.cache import cache
from django.db import IntegrityError
from requests import exceptions, post
from requests.auth import HTTPBasicAuth

from openedx_events_2_n8n.models import WebhookEvent
from openedx_events_2_n8n.utils import flatten_dict, make_json_serializable

N8N_REQUEST_TIMEOUT = 5
N8N_RETRY_COUNTDOWN = 3
JWT_TOKEN_TTL = 60
EVENT_DEDUPE_LOCK_TTL = 60
EVENT_DEDUPE_LOCK_KEY_TEMPLATE = "openedx_events_2_n8n:sending:{event_id}"
log = logging.getLogger(__name__)


def _build_request_auth(webhook_config):
    """Turn a webhook config dict into `requests.post` auth/headers kwargs."""
    auth_type = webhook_config.get("auth_type", "none")
    if auth_type == "basic":
        return {
            "auth": HTTPBasicAuth(
                webhook_config.get("basic_auth_username", ""),
                webhook_config.get("basic_auth_password", ""),
            )
        }
    if auth_type == "header":
        header_name = webhook_config.get("header_auth_name", "")
        if not header_name:
            return {}
        return {"headers": {header_name: webhook_config.get("header_auth_value", "")}}
    if auth_type == "jwt":
        token = jwt.encode(
            {"iat": int(time.time()), "exp": int(time.time()) + JWT_TOKEN_TTL},
            webhook_config.get("jwt_auth_secret", ""),
            algorithm="HS256",
        )
        return {"headers": {"Authorization": f"Bearer {token}"}}
    return {}


@shared_task(
    bind=True,
    autoretry_for=(exceptions.RequestException,),
    retry_backoff=True,
    retry_kwargs={"max_retries": N8N_RETRY_COUNTDOWN},
)
def send_data_to_n8n(self, webhook_config, data):  # pylint: disable=unused-argument
    """
    Send data to n8n using a webhook.

    Arguments:
        self: The task instance.
        webhook_config: dict with `url` and auth settings (see utils.get_webhook_config).
        data: The data to send to the webhook.
    """
    event_metadata = data.get("event_metadata", {})
    event_type = event_metadata.get("event_type", "")
    event_id = str(event_metadata.get("id", ""))

    lock_key = EVENT_DEDUPE_LOCK_KEY_TEMPLATE.format(event_id=event_id)
    if event_id:
        if WebhookEvent.objects.filter(event_id=event_id, is_success=True).exists():
            log.info("Skipping already-sent event %s (%s)", event_id, event_type)
            return
        if not cache.add(lock_key, 1, EVENT_DEDUPE_LOCK_TTL):
            log.info("Event %s (%s) is already being sent, skipping duplicate", event_id, event_type)
            return

    flattened_data = make_json_serializable(flatten_dict(data))
    request_kwargs = _build_request_auth(webhook_config)
    try:
        try:
            log.info("Sending data to n8n: %s", flattened_data)
            response = post(
                webhook_config["url"],
                json=flattened_data,
                timeout=N8N_REQUEST_TIMEOUT,
                **request_kwargs,
            )
            try:
                WebhookEvent.objects.create(
                    event_type=event_type,
                    event_id=event_id,
                    url=webhook_config["url"],
                    payload=flattened_data,
                    is_success=response.ok,
                    status_code=response.status_code,
                    response_body=response.text,
                )
            except IntegrityError:
                log.info("Event %s (%s) already recorded as sent, skipping duplicate", event_id, event_type)
        except exceptions.RequestException as e:
            log.error("Error sending data to n8n: %s", e)
            WebhookEvent.objects.create(
                event_type=event_type,
                event_id=event_id,
                url=webhook_config["url"],
                payload=flattened_data,
                is_success=False,
                error_message=str(e),
            )
            raise
    finally:
        if event_id:
            cache.delete(lock_key)
