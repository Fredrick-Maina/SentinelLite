# SentinelLite 🛡️

> **Affordable, Easy-to-Use Cybersecurity Log Monitoring Platform for Small Businesses and Small IT Service Providers (MSPs)**

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.2-61DAFB.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2-3178C6.svg)](https://www.typescriptlang.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📌 Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Core Features](#core-features)
- [Tech Stack](#tech-stack)
- [Project Directory Structure](#project-directory-structure)
- [Quick Start Guide](#quick-start-guide)
  - [Option A: Local Development (FastAPI + Vite)](#option-a-local-development-fastapi--vite)
  - [Option B: Containerized Production (Docker Compose)](#option-b-containerized-production-docker-compose)
- [Running Automated Tests](#running-automated-tests)
- [Lightweight Python Agent](#lightweight-python-agent)
- [AI Security Analyst Assistant](#ai-security-analyst-assistant)
- [Documentation & Deployment](#documentation--deployment)

---

## Overview

**SentinelLite** is a multi-tenant cybersecurity log monitoring SaaS designed specifically for small businesses and Managed Service Providers (MSPs). It allows organizations to monitor security events across servers, Linux/Windows workstations, web servers (Nginx/Apache), and custom applications without requiring an enterprise Security Operations Center (SOC).

SentinelLite ingests raw log sources, normalizes events into a unified schema, runs a real-time rule-based detection engine, generates actionable security alerts, provides AI-assisted alert explanations with PII redaction, and delivers a sleek cybersecurity dashboard.

---

## Architecture

SentinelLite uses a **Modular Monolith** architecture optimized for performance, scalability, and ease of deployment.

```
                   +-----------------------------------+
                   |     React + TypeScript SPA        |
                   |      (SentinelLite Dashboard)     |
                   +-----------------+-----------------+
                                     | (REST API / JWT)
                                     v
+-----------------+        +-------------------+        +-------------------+
|  Python Agent   |------->|   FastAPI App     |<------>|  PostgreSQL / DB  |
| (Log Collector) | Ingest | (Backend Service) |        | (Tenant Isolated) |
+-----------------+        +---------+---------+        +-------------------+
                                     |
                                     v
                           +-------------------+
                           |  Detection Engine |
                           |  & AI Analyst     |
                           +-------------------+
```

---

## Core Features

- 🔑 **Authentication & RBAC**: JWT access tokens, bcrypt password salting/hashing, and role-based permissions (`OWNER`, `ANALYST`, `VIEWER`).
- 🏢 **Multi-Tenant Data Isolation**: Organization-level isolation (`organization_id`) strictly enforced at backend database query layers.
- 📥 **Log Ingestion Pipeline**: Ingestion API (`POST /api/v1/ingest/events`) authenticated via secret agent API keys (`sl_ak_...`).
- 🔄 **Log Normalizer**: Normalizes Linux SSH authentication, Syslog, Web Nginx/Apache 404/error logs, and raw JSON logs into a standardized event model.
- ⚡ **Rule-Based Detection Engine**: Real-time detection of SSH Brute-Force attacks, Web Path Traversal Scanning, and authentication anomalies with automatic deduplication.
- 🚨 **Alert Management Workspace**: Complete alert triage lifecycle (`NEW`, `ACKNOWLEDGED`, `INVESTIGATING`, `RESOLVED`, `FALSE_POSITIVE`) with analyst investigation notes.
- 🤖 **AI Security Analyst**: Grounded LLM alert explanation engine with automatic PII/credential redaction, producing incident summaries and technical remediation steps.
- 📊 **Executive Security Reports & CSV Export**: Generate summary reports covering event totals, alert severity distributions, and top offending source IPs.
- 📜 **Immutable Audit Logs**: Records administrative actions (`DEVICE_REGISTERED`, `DEVICE_REVOKED`, `REPORT_GENERATED`).
- 💎 **Subscription-Ready Architecture**: Built-in plan tier limits (`FREE_TRIAL`, `STARTER`, `PRO`, `ENTERPRISE`) for active devices and event retention.
- 🖥️ **React Dashboard UI**: Modern dark-theme dashboard built with React 18, TypeScript, Vite, and Tailwind CSS styling.

---

## Tech Stack

- **Backend**: Python 3.11+, FastAPI, Pydantic v2, SQLAlchemy 2.0, Alembic, Pytest
- **Database**: PostgreSQL (Production), SQLite (Local Dev / Tests)
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons
- **Agent**: Python daemon with HTTP retry logic & local buffering
- **Containerization**: Docker, Docker Compose, Nginx

---

## Project Directory Structure

```text
SentineLite/
├── backend/                  # FastAPI Backend Service
│   ├── app/                  # Application source code
│   │   ├── api/v1/           # API Endpoints (auth, orgs, devices, ingest, alerts, ai, reports, audit)
│   │   ├── auth/             # Security, JWT tokens, RBAC dependencies
│   │   ├── detection/        # Rule-based detection engine
│   │   ├── ai/               # AI Security Analyst service with redaction
│   │   ├── models/           # SQLAlchemy DB domain models
│   │   ├── schemas/          # Pydantic v2 validation schemas
│   │   └── services/         # Normalizer, report generator, audit logger, plan tier engine
│   ├── migrations/           # Alembic database migrations
│   ├── tests/                # Comprehensive Pytest suite (19 integration tests)
│   ├── Dockerfile            # Backend production container
│   └── requirements.txt      # Python dependencies
├── frontend/                 # React + TypeScript + Vite Dashboard
│   ├── src/                  # Components, Pages, Services, Styles, Types
│   ├── dist/                 # Production compiled static bundle
│   ├── Dockerfile            # Nginx production container
│   └── package.json          # Node dependencies
├── agent/                    # Standalone Python Log Collector Agent
│   ├── sentinellite_agent/   # Collector daemon & CLI sample attack replayer
│   └── requirements.txt
├── docs/                     # Production & Pilot Documentation
│   ├── DEPLOYMENT.md         # Docker Compose, Nginx reverse proxy, HTTPS, Postgres backup guide
│   └── PILOT_VALIDATION.md   # MSP pilot discovery questions & onboarding checklist
├── docker-compose.yml        # Multi-container production orchestration
├── PROJECT_PLAN.md           # Master roadmap & completed milestones
├── prompt.txt                # Unified master instructions
└── README.md                 # Project documentation
```

---

## Quick Start Guide

### Option A: Local Development (FastAPI + Vite)

1. **Clone & Setup Python Virtual Environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r backend/requirements.txt -r agent/requirements.txt
   ```

2. **Run Database Migrations**:
   ```bash
   cd backend
   alembic upgrade head
   ```

3. **Start FastAPI Backend Server**:
   ```bash
   PYTHONPATH=. uvicorn app.main:app --reload --port 8000
   ```
   *Open API Docs*: `http://127.0.0.1:8000/docs`

4. **Start React Frontend Dev Server**:
   ```bash
   cd ../frontend
   npm install
   npm run dev
   ```
   *Open Dashboard*: `http://localhost:5173`

---

### Option B: Containerized Production (Docker Compose)

Run the full 3-tier production stack (`postgres`, `backend`, `frontend` Nginx server):

```bash
docker-compose up --build -d
```

Check health status:
```bash
docker-compose ps
```
- **Frontend Dashboard**: `http://localhost:80`
- **Backend REST API**: `http://localhost:8000`

---

## Running Automated Tests

The backend test suite contains **19 comprehensive integration tests** covering health, auth, multi-tenant isolation, devices, ingestion, detection, alerts, agent E2E replay, AI analyst, reports, audit logs, and subscription limits.

```bash
source .venv/bin/activate
cd backend
PYTHONPATH=.:../agent pytest -v
```

---

## Lightweight Python Agent

SentinelLite includes a standalone Python agent located in `agent/sentinellite_agent/`.

### Replaying Attack Logs for Testing
To simulate an attack scenario (SSH Brute Force + Web Scanning) against your server:

1. Register a device in the SentinelLite UI under **Devices** -> Copy the generated API Key (`sl_ak_...`).
2. Run the agent attack replayer:
   ```bash
   source .venv/bin/activate
   python3 agent/sentinellite_agent/main.py --server-url http://127.0.0.1:8000 --api-key <YOUR_DEVICE_API_KEY> --replay-sample
   ```
3. Refresh the SentinelLite Dashboard to view real-time security alerts!

---

## AI Security Analyst Assistant

SentinelLite incorporates an **AI Security Analyst Assistant** (`app/ai/service.py`).
- **Data Privacy**: Automatically redacts sensitive passwords, API keys, and secret tokens before sending payloads to LLMs.
- **Evidence Grounding**: Analyzes real alert evidence and log metadata without inventing false IPs or timestamps.
- **Output**: Generates executive summaries, technical narratives, and actionable remediation steps.

---

## Documentation & Deployment

- 📘 **[PROJECT_PLAN.md](PROJECT_PLAN.md)**: Full project vision, architectural choices, and milestone history.
- 🚀 **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)**: Production deployment instructions, Nginx SSL/TLS setup, PostgreSQL backup/restore procedures, and security checklist.
- 🎯 **[docs/PILOT_VALIDATION.md](docs/PILOT_VALIDATION.md)**: Target MSP customer discovery questions, value propositions, and 30-day pilot onboarding checklist.

---

## License

This project is open-source under the [MIT License](LICENSE).
