# SentinelLite Production Deployment & Hardening Guide

## Overview
This document covers production deployment, container orchestration, reverse proxy configuration, database backup strategy, and security hardening for SentinelLite on a VPS instance.

---

## Architecture Diagram

```
Internet (HTTPS) ---> Nginx Reverse Proxy (SSL Certbot)
                           |
            +--------------+--------------+
            |                             |
    Frontend (React SPA)          Backend (FastAPI)
       Port 80/443                   Port 8000
                                          |
                                   PostgreSQL DB
                                     Port 5432
```

---

## 1. Local & Production Container Orchestration

### Starting the Production Stack
```bash
docker-compose up --build -d
```

### Checking Container Health
```bash
docker-compose ps
docker-compose logs -f backend
```

---

## 2. Nginx Reverse Proxy & SSL Configuration

### Sample Nginx Configuration (`/etc/nginx/sites-available/sentinellite`)
```nginx
server {
    server_name monitor.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        client_max_body_size 10M;
    }
}
```

### Obtaining Free Let's Encrypt SSL Certificate
```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d monitor.yourdomain.com
```

---

## 3. Database Backup & Disaster Recovery

### Manual PostgreSQL Database Dump
```bash
docker exec -t sentinellite_postgres pg_dump -U sentinellite -d sentinellite_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Database Restore Command
```bash
cat backup_20260914.sql | docker exec -i sentinellite_postgres psql -U sentinellite -d sentinellite_db
```

---

## 4. Security Hardening Checklist
- [x] Passwords stored securely using `bcrypt` salting/hashing.
- [x] Multi-tenancy backend query validation (`organization_id`).
- [x] Per-device API keys hashed in database with prefixes (`sl_ak_...`).
- [x] PII & credentials redacted from log evidence prior to AI analysis.
- [x] Secure CORS origin restrictions configured in `config.py`.
- [x] Input rate limiting & payload validation via Pydantic v2.
