# Deployment Guide - Render.com & Cloud Platforms

This project is pre-configured with a `render.yaml` Blueprint and Dockerfile for **Render.com**, **Railway**, and **Docker**.

---

## 🚀 How to Deploy on Render.com (Step-by-Step)

### Option 1: Render Blueprint (Easiest - 1 Click)

1. **Push code to GitHub**:
   ```bash
   git add .
   git commit -m "Configure Render.com deployment"
   git push origin main
   ```

2. **Connect to Render**:
   - Go to **[dashboard.render.com](https://dashboard.render.com)**.
   - Click **New +** $\rightarrow$ **Blueprints**.
   - Connect your GitHub account and select your repository (`Capstone_project`).

3. **Deploy**:
   - Render automatically reads [`render.yaml`](file:///Users/prabhakarkumarjha/Desktop/Capstone_project/render.yaml) and configures the Docker Web Service.
   - Click **Approve**.
   - Render will build your Docker image and assign a public URL (e.g. `https://loanai-decision-platform.onrender.com`).

---

### Option 2: Manual Web Service Setup on Render

If you prefer setting up manually without Blueprints:

1. Click **New +** $\rightarrow$ **Web Service** on Render.
2. Select your GitHub repository (`Capstone_project`).
3. Select **Language**: `Docker`.
4. **Dockerfile Path**: `Dockerfile` (default).
5. **Health Check Path**: `/health`.
6. Click **Create Web Service**.

---

## 🛠️ Local Docker Testing

```bash
# Build Docker Image
docker build -t loanai-app:latest .

# Test Container Locally on Port 8000
docker run -d -p 8000:8000 --name loanai-container loanai-app:latest

# Check Logs
docker logs -f loanai-container
```

---

## 📋 Environment Variables Configured on Render

| Key | Default Value | Description |
|---|---|---|
| `PORT` | `10000` | Render injects this automatically |
| `ENVIRONMENT` | `production` | Production mode |
| `LOG_LEVEL` | `INFO` | Logging level |
| `JWT_SECRET` | *(Auto-generated)* | Render generates a secure random secret |
