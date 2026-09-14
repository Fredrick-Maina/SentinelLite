# SentinelLite Master Project Plan & Architecture

## Overview
SentinelLite is an affordable, easy-to-use security log monitoring SaaS platform designed for small businesses and small IT service providers (MSPs). It enables organizations to monitor security events across servers, workstations, web servers, and applications without requiring a full Security Operations Center (SOC).

---

## Workspace Summary

### Environment
- **Operating System**: Linux (x86_64)
- **Python Version**: Python 3.14+ (venv at `.venv`)
- **Node.js / NPM Version**: Node.js v22.22.2, NPM 11.16.0
- **Docker**: Docker CLI present

---

## Completed Phased Implementation Roadmap

- [x] **Phase 0: Project Inspection & Planning** (Workspace inspected, roadmap & master prompt integrated)
- [x] **Phase 1: Backend Foundation & Database Schema** (FastAPI app, SQLAlchemy models, Alembic migrations, Pytest setup)
- [x] **Phase 2: Authentication & Multi-Tenant RBAC** (JWT tokens, bcrypt password security, User/Org/Membership schema, Tenant access control dependencies)
- [x] **Phase 3: Log Ingestion & Normalization Engine** (Agent device registration, secret API Keys `sl_ak_...`, Log normalizer for Linux SSH, Syslog, Web Nginx/Apache, JSON)
- [x] **Phase 4: Rule-based Detection Engine & Alert Workspace** (SSH Brute Force, Web Path Scanning detectors, Alert triage states, Investigation notes)
- [x] **Phase 5: React Dashboard & Alert Triage UI** (React + TypeScript + Vite single page app compiled into `dist/`)
- [x] **Phase 6: Lightweight Python Collector Agent** (Daemon log collector with local buffer, retry logic, sample log replay CLI)
- [x] **Phase 7: AI Security Analyst Assistant** (Grounded alert explanation engine, PII/secret redaction, investigation recommendations)
- [x] **Phase 8: Reports, Audit Logging & SaaS Readiness** (Executive report generation, CSV export, audit log recording, plan tier device limit enforcement)
- [x] **Phase 9: Docker Deployment & Production Hardening** (Production docker-compose configuration, frontend Nginx container, deployment & SSL setup guide in `docs/DEPLOYMENT.md`)
- [x] **Phase 10: Pilot Customer Validation & Feedback Guide** (MSP discovery interview framework & pilot onboarding checklist in `docs/PILOT_VALIDATION.md`)

---

## Verification Summary
- **Backend Test Suite**: **19 passed out of 19 Pytest integration tests**.
- **Frontend Build**: React + TypeScript + Vite production build (`dist/`) completed with **0 errors**.
