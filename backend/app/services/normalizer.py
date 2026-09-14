import json
import re
from datetime import datetime, timezone
from typing import Dict, Any, Tuple
from app.models.event import EventSeverity

# Regex patterns
SSH_FAILED_PAT = re.compile(
    r"Failed password for (?:invalid user )?(?P<user>\S+) from (?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) port (?P<port>\d+)"
)
SSH_ACCEPTED_PAT = re.compile(
    r"Accepted (?:password|publickey) for (?P<user>\S+) from (?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) port (?P<port>\d+)"
)
NGINX_LOG_PAT = re.compile(
    r'^(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) \S+ \S+ \[(?P<time>[^\]]+)\] "(?P<method>\S+) (?P<path>\S+) \S+" (?P<status>\d{3}) (?P<size>\d+)'
)


class LogNormalizer:
    @staticmethod
    def normalize(
        raw_message: str,
        source_type: str = "generic",
        default_timestamp: datetime = None,
        default_hostname: str = None
    ) -> Dict[str, Any]:
        """Normalize a raw log message into structured event fields."""
        if not default_timestamp:
            default_timestamp = datetime.now(timezone.utc)

        result = {
            "source_type": source_type.lower(),
            "event_type": "generic_log",
            "severity": EventSeverity.INFO,
            "timestamp": default_timestamp,
            "hostname": default_hostname,
            "username": None,
            "source_ip": None,
            "destination_ip": None,
            "destination_port": None,
            "message": raw_message.strip(),
            "raw_message": raw_message,
            "extra_metadata": {},
        }

        # Try JSON parsing first if applicable
        if raw_message.strip().startswith("{") and raw_message.strip().endswith("}"):
            try:
                data = json.loads(raw_message.strip())
                result["source_type"] = data.get("source_type", source_type)
                result["event_type"] = data.get("event_type", "json_event")
                result["username"] = data.get("username")
                result["source_ip"] = data.get("source_ip")
                result["destination_ip"] = data.get("destination_ip")
                result["destination_port"] = data.get("destination_port")
                result["message"] = data.get("message", raw_message)
                if "severity" in data:
                    sev_str = str(data["severity"]).upper()
                    if hasattr(EventSeverity, sev_str):
                        result["severity"] = EventSeverity[sev_str]
                return result
            except Exception:
                pass

        # SSH log normalization
        if "sshd" in raw_message.lower() or source_type.lower() == "ssh":
            result["source_type"] = "ssh"
            failed_match = SSH_FAILED_PAT.search(raw_message)
            if failed_match:
                result["event_type"] = "auth_failure"
                result["severity"] = EventSeverity.MEDIUM
                result["username"] = failed_match.group("user")
                result["source_ip"] = failed_match.group("ip")
                result["destination_port"] = int(failed_match.group("port"))
                result["message"] = f"Failed SSH login for user '{result['username']}' from {result['source_ip']}"
                return result

            accepted_match = SSH_ACCEPTED_PAT.search(raw_message)
            if accepted_match:
                result["event_type"] = "auth_success"
                result["severity"] = EventSeverity.INFO
                result["username"] = accepted_match.group("user")
                result["source_ip"] = accepted_match.group("ip")
                result["destination_port"] = int(accepted_match.group("port"))
                result["message"] = f"Successful SSH login for user '{result['username']}' from {result['source_ip']}"
                return result

        # Nginx/Apache log normalization
        nginx_match = NGINX_LOG_PAT.search(raw_message)
        if nginx_match or source_type.lower() in ("nginx", "apache", "web"):
            result["source_type"] = "web"
            if nginx_match:
                result["source_ip"] = nginx_match.group("ip")
                path = nginx_match.group("path")
                status_code = int(nginx_match.group("status"))
                
                result["extra_metadata"] = {
                    "method": nginx_match.group("method"),
                    "path": path,
                    "status_code": status_code,
                }

                if status_code == 404:
                    result["event_type"] = "web_not_found"
                    result["severity"] = EventSeverity.LOW
                elif status_code in (401, 403):
                    result["event_type"] = "web_auth_denied"
                    result["severity"] = EventSeverity.MEDIUM
                elif status_code >= 500:
                    result["event_type"] = "web_server_error"
                    result["severity"] = EventSeverity.MEDIUM
                else:
                    result["event_type"] = "web_access"
                    result["severity"] = EventSeverity.INFO

                result["message"] = f"Web {nginx_match.group('method')} {path} -> Status {status_code}"
                return result

        return result
