import os
from pydantic import BaseModel


class AgentConfig(BaseModel):
    server_url: str = os.getenv("SENTINELLITE_SERVER_URL", "http://127.0.0.1:8000")
    api_key: str = os.getenv("SENTINELLITE_API_KEY", "")
    hostname: str = os.getenv("SENTINELLITE_HOSTNAME", "local-host")
    batch_size: int = int(os.getenv("SENTINELLITE_BATCH_SIZE", "10"))
    flush_interval_seconds: int = int(os.getenv("SENTINELLITE_FLUSH_INTERVAL", "5"))
    log_files: str = os.getenv("SENTINELLITE_LOG_FILES", "")
