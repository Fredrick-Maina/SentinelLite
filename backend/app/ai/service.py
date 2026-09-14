import re
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.models.ai import AIAnalysis


class AISecurityAnalyst:
    def __init__(self, db: Session):
        self.db = db

    def redact_sensitive_evidence(self, text: str) -> str:
        """Redact sensitive passwords or tokens before sending to external models."""
        if not text:
            return ""
        # Redact password patterns
        text = re.sub(r'password["\s:=]+\S+', 'password="[REDACTED]"', text, flags=re.IGNORECASE)
        text = re.sub(r'token["\s:=]+\S+', 'token="[REDACTED]"', text, flags=re.IGNORECASE)
        return text

    def analyze_alert(self, alert: Alert, provider: str = "mock") -> AIAnalysis:
        """Analyze a security alert using actual grounded evidence."""
        evidence_str = str(alert.evidence or {})
        clean_evidence = self.redact_sensitive_evidence(evidence_str)

        # Grounded summary logic based on real alert data
        if "SSH_BRUTE_FORCE" in clean_evidence or "SSH" in alert.title:
            summary = (
                f"The system detected repeated failed SSH login attempts ({alert.event_count} failures) "
                f"from source IP {alert.source_ip or 'unknown'} targeting device '{alert.affected_device_name or 'server'}'."
            )
            explanation = (
                f"Between {alert.first_seen.strftime('%H:%M:%S')} and {alert.last_seen.strftime('%H:%M:%S')}, "
                f"the host recorded multiple SSH authentication failures from IP {alert.source_ip}. "
                "This behavior matches automated password spraying or brute-force attack patterns. "
                "Note: This alert indicates automated login probing; it does not prove that an account was successfully compromised."
            )
            recommended_actions = [
                f"Verify if IP {alert.source_ip} belongs to an authorized employee or VPN exit node.",
                "Check system logs to verify whether any successful authentication followed the failure burst.",
                "Consider blocking the IP address at the firewall or enforcing Fail2ban rate limiting.",
                "Ensure root SSH login is disabled and SSH password authentication is replaced with public key pairs."
            ]
        elif "WEB_PATH_SCANNING" in clean_evidence or "Web" in alert.title:
            summary = (
                f"The system detected web application reconnaissance scanning ({alert.event_count} missing requests) "
                f"from source IP {alert.source_ip or 'unknown'}."
            )
            explanation = (
                f"Source IP {alert.source_ip} generated multiple 404 HTTP requests requesting administrative endpoints "
                "or configuration files. This pattern is characteristic of automated vulnerability scanners (e.g. Nikto, Dirbuster)."
            )
            recommended_actions = [
                "Inspect web server access logs to check if any sensitive endpoint returned a HTTP 200 OK status.",
                "Ensure sensitive configuration files (.env, .git, phpmyadmin) are restricted from web access.",
                "Implement Web Application Firewall (WAF) rate limiting for aggressive scanners."
            ]
        else:
            summary = f"Security alert '{alert.title}' triggered with {alert.event_count} matching events."
            explanation = (
                f"The detection engine flagged events from IP {alert.source_ip or 'N/A'}. "
                "Analysis grounded in available log timestamps and event metadata."
            )
            recommended_actions = [
                "Review linked raw log events for additional diagnostic details.",
                "Correlate source IP with threat intelligence databases."
            ]

        ai_record = AIAnalysis(
            alert_id=alert.id,
            provider=provider,
            model_name="sentinellite-analyst-v1",
            summary=summary,
            explanation=explanation,
            recommended_actions=recommended_actions,
            is_mock=(provider == "mock"),
        )
        self.db.add(ai_record)
        self.db.commit()
        self.db.refresh(ai_record)

        return ai_record
