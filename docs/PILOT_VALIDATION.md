# SentinelLite Pilot Customer Discovery & Validation Guide

## Target Customer Persona
- **Primary Customer**: Small IT Service Providers / Managed Service Providers (MSPs) managing security for 5–20 small businesses.
- **Secondary Customer**: Small offices, law firms, accounting practices without in-house SOC teams.

---

## 1. Customer Interview Discovery Questions

When demonstrating SentinelLite to 5–10 prospective pilot clients, ask:

1. **Current Workflow**: "How do you currently monitor failed logins, SSH brute-force attempts, or suspicious web requests across client servers?"
2. **Pain Point**: "What is the biggest frustration with current tools (e.g. enterprise SIEM complexity, noisy false positives, high cost)?"
3. **Value Proposition**: "Would receiving instant alerts with AI-generated incident explanations and recommended remediation steps save your team investigation time?"
4. **Willingness to Pay**: "If SentinelLite monitors 5 servers with automated AI alert summaries for \$49/month, would you participate in a 30-day trial?"

---

## 2. 30-Day Pilot Onboarding Checklist

1. **Organization Registration**: Create organization account on SentinelLite dashboard.
2. **Device Onboarding**:
   - Register server in SentinelLite UI -> Copy generated `sl_ak_...` API Key.
   - Run Python Agent replayer or daemon on target Linux server:
     ```bash
     python3 agent/sentinellite_agent/main.py --server-url https://monitor.yourdomain.com --api-key sl_ak_xxx
     ```
3. **Alert Review & AI Analysis**:
   - Verify attack simulation events generate real alerts.
   - Click **Generate AI Explanation** button to view grounded incident summary and investigation recommendations.
4. **Feedback Collection**: Record pilot customer feedback on UI clarity, false positive rates, and reporting usefulness.
