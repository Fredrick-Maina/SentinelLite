import time
import logging
import httpx
from typing import List, Dict, Any

logger = logging.getLogger("sentinellite_agent")


class IngestionClient:
    def __init__(self, server_url: str, api_key: str):
        self.endpoint = f"{server_url.rstrip('/')}/api/v1/ingest/events"
        self.api_key = api_key
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
        }

    def send_events(self, events: List[Dict[str, Any]], retries: int = 3) -> bool:
        """Send a batch of normalized log events to the SentinelLite backend with retry logic."""
        if not events:
            return True

        payload = {"events": events}
        backoff = 1.0

        for attempt in range(1, retries + 1):
            try:
                with httpx.Client(timeout=10.0) as client:
                    response = client.post(self.endpoint, json=payload, headers=self.headers)
                    if response.status_code == 200:
                        data = response.json()
                        logger.info(f"Successfully ingested {data.get('ingested_count', 0)} events.")
                        return True
                    else:
                        logger.warning(f"Ingestion attempt {attempt} failed (HTTP {response.status_code}): {response.text}")
            except Exception as e:
                logger.error(f"Ingestion attempt {attempt} error: {str(e)}")

            if attempt < retries:
                time.sleep(backoff)
                backoff *= 2.0

        return False
