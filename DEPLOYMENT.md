# 🚀 MFG Agent --- Deployment Guide

Supabase + Firebase + Render + Vercel

------------------------------------------------------------------------

# 🧱 Architecture Overview

    Browser (Vercel)
        │
        ├─ GET / → Static frontend (Firebase Auth)
        │
        └─ POST /api/query → Render (Flask + Gunicorn)
               │
               ├─ Verify Firebase token
               ├─ Run AI agents (Research + Writer)
               ├─ External APIs (Groq / Tavily / Serper)
               ├─ Supabase (Postgres)
               │     ├─ suppliers
               │     ├─ reports
               │     └─ history
               │
               └─ SSE stream back → real-time updates

------------------------------------------------------------------------

# ✅ One-Time Setup

## 1️⃣ Firebase (Google Sign-In)

1.  Go to: https://console.firebase.google.com\
2.  Create a new project\
3.  Authentication → Sign-in method → Enable **Google**
4.  Project Settings → **Your apps** → Add **Web App**
5.  Copy the `firebaseConfig` object
6.  Project Settings → **Service Accounts**
    -   Generate new private key
    -   Download JSON

Paste `firebaseConfig` into:

    static/index.html

Inside:

``` js
const FIREBASE_CONFIG = { ... }
```

------------------------------------------------------------------------

## 2️⃣ Supabase Setup

1.  Go to: https://supabase.com\
2.  Create a new project\
3.  Go to **Settings → API**
4.  Copy:

-   SUPABASE_URL
-   SUPABASE_SERVICE_ROLE_KEY

⚠️ Use service_role key only on backend.

------------------------------------------------------------------------

# 🗄 Database Schema

## reports

-   session_id (PK) -- text\
-   user_id -- text\
-   query -- text\
-   product -- text\
-   location -- text\
-   report_text -- text\
-   suppliers_found -- integer\
-   sources_used -- text\
-   elapsed_seconds -- double precision\
-   created_at -- timestamp (default now())

## suppliers

-   id (PK) -- text\
-   session_id -- text\
-   user_id -- text\
-   query -- text\
-   name -- text\
-   location -- text\
-   products -- text\
-   website -- text\
-   contact -- text\
-   description -- text\
-   certifications -- text\
-   min_order -- text\
-   source -- text\
-   created_at -- timestamp (default now())

## history

-   id (PK) -- text\
-   user_id -- text\
-   query -- text\
-   session_id -- text\
-   created_at -- timestamp (default now())

------------------------------------------------------------------------

# ⚡ Add Database Indexes

Run in Supabase SQL Editor:

``` sql
CREATE INDEX idx_suppliers_user_session
ON suppliers (user_id, session_id);

CREATE INDEX idx_reports_user_id
ON reports (user_id);

CREATE INDEX idx_history_user_id
ON history (user_id);
```

------------------------------------------------------------------------

# 💻 Local Development

## Environment Variables

Copy `.env.example` → `.env`

Fill in:

GROQ_API_KEY=\
FIREBASE_PROJECT_ID=\
FIREBASE_CREDENTIALS_JSON=\
SUPABASE_URL=\
SUPABASE_SERVICE_ROLE_KEY=\
TAVILY_API_KEY= (optional)\
SERPER_API_KEY= (optional)

## Install

``` bash
pip install -e .
```

## Run

``` bash
python -m backend
```

Open:

http://localhost:5000

------------------------------------------------------------------------

# 🚀 Deploy Backend (Render)

Build command:

``` bash
pip install -e .
```

Start command:

``` bash
gunicorn backend.app:app --workers 2 --threads 4 --timeout 120
```

Health check:

    /api/health

Required env vars:

GROQ_API_KEY\
FIREBASE_PROJECT_ID\
FIREBASE_CREDENTIALS_JSON\
SUPABASE_URL\
SUPABASE_SERVICE_ROLE_KEY\
CORS_ORIGINS=https://mfg-agent.vercel.app

------------------------------------------------------------------------

# 🌐 Deploy Frontend (Vercel)

Update `vercel.json`:

    "dest": "https://your-render-backend.onrender.com/api/$1"

Deploy:

``` bash
npm i -g vercel
vercel deploy --prod
```

------------------------------------------------------------------------

# 🏆 Production Stack

-   Firebase (Auth)
-   Groq (LLM)
-   Supabase (Database)
-   Render (Backend)
-   Vercel (Frontend)
-   SSE Streaming