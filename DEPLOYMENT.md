# 🚀 Deployment Guide: WikiQuiz Generator

This guide covers deploying the **Backend (PostgreSQL + FastAPI)** on **Render** and the **Frontend (React)** on **Vercel**.

---

## 🏗️ Part 1: Backend Deployment (Render)

We will use Render because it offers free hosting for both the Web Service (Python) and the Database (PostgreSQL).

### **Step 1: Create the Database**
1.  Go to [dashboard.render.com](https://dashboard.render.com/).
2.  Click **New +** -> **PostgreSQL**.
3.  Name: `wikiquiz-db` (or anything).
4.  User: (Leave default).
5.  Region: Choose the one closest to you (e.g., Singapore, Frankfurt).
6.  Version: 15 or 14 (Default is fine).
7.  **Instance Type**: Select **Free**.
8.  Click **Create Database**.
9.  **WAIT**: It takes 1-2 minutes to initialize.
10. Once ready, copy the **Internal Database URL** (for backend dashboard) and the **External Database URL** (if you want to connect from your PC, but usually Internal is safer for the app).

### **Step 2: Deploy the Web Service**
1.  Push your latest code to **GitHub**.
2.  In Render Dashboard, click **New +** -> **Web Service**.
3.  Connect your GitHub repository.
4.  **Settings**:
    *   **Name**: `wikiquiz-backend`
    *   **Runtime**: **Python 3**
    *   **Build Command**: `pip install -r backend/requirements.txt`
        *   *Note: Since your 'backend' is in a folder, you might need to adjust the Root Directory below.*
    *   **Start Command**: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
        *   *Alternatively, set "Root Directory" to `backend` in the settings below, then just use: `pip install -r requirements.txt` and `uvicorn main:app --host 0.0.0.0 --port $PORT`*
5.  **Environment Variables** (Click "Advanced" or "Environment"):
    *   `PYTHON_VERSION`: `3.11.0` (Recommended)
    *   `DATABASE_URL`: Paste the **Internal Database URL** from Step 1.
    *   `GOOGLE_API_KEY`: Your Gemini API Key.
    *   `JWT_SECRET_KEY`: A random long string (e.g., `supersecretkey123`).
    *   `ALLOWED_ORIGINS`: `*` (or your frontend URL later, e.g., `https://your-frontend.vercel.app`).
6.  **Instance Type**: Free.
7.  Click **Create Web Service**.

> **Wait**: Render takes a few minutes. Watch the logs. If it says `Application startup complete`, it is live!
> **Copy URL**: Use the URL provided (e.g., `https://wikiquiz-backend.onrender.com`).

---

## 🎨 Part 2: Frontend Deployment (Vercel)

Vercel is the best place to host React/Vite apps for free.

1.  Go to [vercel.com](https://vercel.com/) and Login with GitHub.
2.  Click **Add New...** -> **Project**.
3.  Import your GitHub repository.
4.  **Configure Project**:
    *   **Framework Preset**: Vite (should auto-detect).
    *   **Root Directory**: Click "Edit" and select `frontend`.
5.  **Environment Variables**:
    *   `VITE_API_URL`: `https://wikiquiz-backend.onrender.com/api`
        *   *Replace the URL with your actual database Render Backend URL*.
6.  Click **Deploy**.

---

## 🔗 Part 3: Connecting Everything

1.  **Frontend -> Backend**:
    *   By setting `VITE_API_URL` in Vercel, your frontend `api.js` automatically points to the live backend.
2.  **Backend -> Database**:
    *   By setting `DATABASE_URL` in Render, your FastAPI app connects to the Render Postgres instance.

### **Troubleshooting**
*   **Database Error?**: If the backend logs say "auth failed" or "connection failed", ensure you used the **Internal Database URL** in Render env vars.
*   **CORS Error?**: If frontend says "Network Error" or "CORS", go to Render -> Environment -> `ALLOWED_ORIGINS` and set it to `*` or your Vercel URL.
*   **Build Fail?**: Check `backend/requirements.txt`. Ensure `uvicorn` and `gunicorn` are not conflicting. `uvicorn` is sufficient for free tier.
