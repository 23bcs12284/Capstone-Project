# Production Deployment Guide - LoanAI Decision Platform

This repository is pre-configured and deployment-ready for **Railway**, **Render**, **Fly.io**, **AWS App Runner**, or **Self-Hosted Docker Containers**.

---

## 1. Quick Local Docker Deployment

### Build the Production Image
```bash
docker build -t loanai-platform:latest .
```

### Run the Container
```bash
docker run -d -p 8000:8000 --name loanai-app loanai-platform:latest
```
Access the application at: `http://localhost:8000`

### Multi-Container Stack (FastAPI + PostgreSQL DB)
```bash
docker-compose -f deployment/docker-compose.yml up -d
```

---

## 2. Deploying to Railway (Step-by-Step)

Railway provides one-click Docker deployments with automatic HTTPS and dynamic port management.

### Method A: One-Click Deploy via GitHub (Recommended)

1. **Push your project to GitHub**:
   ```bash
   git add .
   git commit -m "Configure production Docker and Railway deployment"
   git push origin main
   ```

2. **Connect to Railway**:
   - Go to [Railway.app](https://railway.app) and sign in.
   - Click **+ New Project**.
   - Select **Deploy from GitHub repo**.
   - Choose your repository (`Capstone_project`).

3. **Automatic Detection**:
   - Railway automatically detects the root [`Dockerfile`](file:///Users/prabhakarkumarjha/Desktop/Capstone_project/Dockerfile) and [`railway.json`](file:///Users/prabhakarkumarjha/Desktop/Capstone_project/railway.json).
   - Railway dynamically sets the `$PORT` environment variable and routes traffic to the container.

4. **Generate Public Domain**:
   - In Railway dashboard, go to **Settings** -> **Networking** -> **Generate Domain**.
   - Your web application will be live at `https://<your-project>.up.railway.app`.

---

### Method B: Deploy via Railway CLI

1. **Install Railway CLI**:
   ```bash
   npm i -g @railway/cli
   ```

2. **Login & Initialize**:
   ```bash
   railway login
   railway init
   ```

3. **Deploy Container**:
   ```bash
   railway up
   ```

---

## 3. Environment Variables Reference

| Variable Name | Default Value | Description |
|---|---|---|
| `PORT` | `8000` | Dynamic port injected by cloud platform (Railway/Render) |
| `ENVIRONMENT` | `production` | Deployment stage (`development` or `production`) |
| `LOG_LEVEL` | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `DATABASE_URL` | `sqlite:///./loan_approval.db` | Database connection string (SQLite by default, or PostgreSQL) |
| `JWT_SECRET` | `production-secret-key-change-in-prod` | Secret key for JWT authentication tokens |

---

## 4. Health Check & API Verification

Once deployed, verify container status using:
- **Health Check**: `GET /health`
- **Web Dashboard**: `GET /`
- **Interactive OpenAPI Specs**: `GET /docs`
- **Prediction Endpoint**: `POST /api/predict`
