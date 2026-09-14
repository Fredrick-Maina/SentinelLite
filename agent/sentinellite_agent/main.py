import sys
import time
import argparse
import logging
from sentinellite_agent.config import AgentConfig
from sentinellite_agent.client import IngestionClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("sentinellite_agent")

SAMPLE_LOGS = [
    {"raw_message": "Failed password for invalid user admin from 198.51.100.50 port 49152 ssh2", "source_type": "ssh"},
    {"raw_message": "Failed password for invalid user admin from 198.51.100.50 port 49153 ssh2", "source_type": "ssh"},
    {"raw_message": "Failed password for root from 198.51.100.50 port 49154 ssh2", "source_type": "ssh"},
    {"raw_message": "Failed password for root from 198.51.100.50 port 49155 ssh2", "source_type": "ssh"},
    {"raw_message": '198.51.100.50 - - [14/Sep/2026:15:30:00 +0000] "GET /wp-admin/setup-config.php HTTP/1.1" 404 162', "source_type": "nginx"},
    {"raw_message": '198.51.100.50 - - [14/Sep/2026:15:30:01 +0000] "GET /.env HTTP/1.1" 404 162', "source_type": "nginx"},
    {"raw_message": '198.51.100.50 - - [14/Sep/2026:15:30:02 +0000] "GET /phpmyadmin HTTP/1.1" 404 162', "source_type": "nginx"},
    {"raw_message": '198.51.100.50 - - [14/Sep/2026:15:30:03 +0000] "GET /config.json HTTP/1.1" 404 162', "source_type": "nginx"},
]


def run_sample_replay(config: AgentConfig):
    """Replay sample attack log events for local demonstration and testing."""
    logger.info("Starting sample log replay mode...")
    client = IngestionClient(config.server_url, config.api_key)

    if not config.api_key:
        logger.error("Error: SENTINELLITE_API_KEY environment variable or --api-key argument is required.")
        sys.exit(1)

    success = client.send_events(SAMPLE_LOGS)
    if success:
        logger.info("Sample log replay completed successfully!")
    else:
        logger.error("Failed to replay sample logs to server.")


def main():
    parser = argparse.ArgumentParser(description="SentinelLite Python Log Collector Agent")
    parser.add_argument("--server-url", type=str, help="SentinelLite backend URL")
    parser.add_argument("--api-key", type=str, help="Device API key (sl_ak_...)")
    parser.add_argument("--replay-sample", action="store_true", help="Replay sample security log dataset")

    args = parser.parse_args()
    config = AgentConfig()

    if args.server_url:
        config.server_url = args.server_url
    if args.api_key:
        config.api_key = args.api_key

    if args.replay_sample:
        run_sample_replay(config)
    else:
        logger.info("Agent started in daemon mode. Use --replay-sample to replay test security logs.")


if __name__ == "__main__":
    main()
