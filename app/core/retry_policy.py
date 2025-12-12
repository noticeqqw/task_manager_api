RETRY_TOPICS = [
    ("webhooks.retry.10s", 10),
    ("webhooks.retry.30s", 30),
    ("webhooks.retry.2m", 120),
    ("webhooks.retry.10m", 600),
]

MAX_RETRIES = len(RETRY_TOPICS)
