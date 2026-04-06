# 🇮🇳 Trade Opportunities API

A FastAPI service that analyzes market data and provides trade opportunity insights for specific sectors in India. It uses **Google Gemini AI** for analysis, **DuckDuckGo** for live web search, and **JWT authentication** for security.

---
## 🗂️ Project Structure

```
trade-api/
├── main.py            # FastAPI app, all routes
├── auth.py            # JWT authentication system
├── rate_limiter.py    # Rate limiting (5 req/min)
├── data_collector.py  # DuckDuckGo live web search
├── analyzer.py        # Google Gemini AI integration
├── session_store.py   # In-memory session tracking
├── config.py          # Environment variable config
├── requirements.txt   # All dependencies
├── .env               # Your secret keys (never commit!)
└── README.md
```

---

## ⚙️ How It Works

```
User Request
    ↓
JWT Auth Check
    ↓
Input Validation (valid sector?)
    ↓
Rate Limit Check (under 5/min?)
    ↓
DuckDuckGo Search (live market data)
    ↓
Google Gemini AI (analyze + generate report)
    ↓
Log to Session Store (in-memory)
    ↓
Return Markdown Report
```

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| FastAPI | Web framework |
| Uvicorn | ASGI server |
| Google Gemini AI (`google-genai`) | AI market analysis |
| DuckDuckGo Search | Live data collection |
| JWT (`python-jose`) | Authentication tokens |
| Passlib + bcrypt | Password hashing |
| SlowAPI | Rate limiting |
| Python-dotenv | Environment variables |

---

## 🚀 Setup Instructions

### Step 1: Make Sure Python is Installed
```bash
python --version
# Should show Python 3.10 or higher
```

### Step 2: Create Project Folder
```bash
mkdir trade-api
cd trade-api
```

### Step 3: Create Virtual Environment
```bash
python -m venv venv
```

Activate it:
```bash
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

You should see `(venv)` in your terminal.

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

> ⚠️ If you get a **bcrypt error**, run:
> ```bash
> pip uninstall bcrypt -y
> pip install bcrypt==4.0.1
> ```

> ⚠️ If pip can't connect to internet, switch to **mobile hotspot** and try again.

### Step 5: Get a Google Gemini API Key
1. Go to [aistudio.google.com](https://aistudio.google.com)
2. Sign in with your Google account
3. Click **"Get API Key"** → **"Create API key"**
4. Click **"Create new project"** and name it (e.g. `trade-api`)
5. Copy the generated API key

### Step 6: Generate a Secret Key
Run this command and copy the output:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Step 7: Create `.env` File
Create a file named `.env` in your project root and paste:
```env
GEMINI_API_KEY=your_gemini_api_key_here
SECRET_KEY=your_generated_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Step 8: Run the Server

**Option A — VS Code:**
1. Open VS Code → `File → Open Folder → select trade-api`
2. Open terminal: `Terminal → New Terminal` or press **Ctrl + `**
3. Run:
```bash
venv\Scripts\activate
uvicorn main:app --reload
```

**Option B — Command Prompt / Terminal:**
```bash
cd trade-api
venv\Scripts\activate
uvicorn main:app --reload
```

### Step 9: Confirm Server is Running
You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process using StatReload
INFO:     Application startup complete.
```

---

## 🌐 Open the API

| URL | What it is |
|---|---|
| http://127.0.0.1:8000 | Health check |
| http://127.0.0.1:8000/docs | Swagger UI (test your API) |

---

## 🔐 Authentication

### Default Users
| Username | Password | Role |
|---|---|---|
| admin | admin123 | Admin (full access) |
| guest | guest123 | User (limited access) |

---

## 🧪 How to Test the API (Step by Step)

### 1. Open Swagger UI
Go to: **http://127.0.0.1:8000/docs**

### 2. Get a Token
1. Scroll to **POST /token**
2. Click it → click **"Try it out"**
3. Fill in:
   - `username`: `admin`
   - `password`: `admin123`
4. Click **Execute**
5. Copy the `access_token` value from the response

### 3. Authorize
1. Click the **"Authorize 🔓"** button at the top right
2. Fill in **only**:
   - `username`: `admin`
   - `password`: `admin123`
3. Leave everything else blank
4. Click **Authorize** → **Close**

### 4. Analyze a Sector
1. Scroll to **GET /analyze/{sector}**
2. Click it → click **"Try it out"**
3. In the `sector` field type: `pharmaceuticals`
4. Click **Execute**
5. Scroll down to see your full **markdown report** ✅

### 5. Check Your Session
1. Click **GET /my-session** → **Try it out** → **Execute**
2. See your request history

### 6. Admin — View All Sessions
1. Login as `admin`
2. Click **GET /admin/sessions** → **Try it out** → **Execute**
3. See all users and their requests

---

## 📊 Main Endpoint

### `GET /analyze/{sector}`

**Requires:** Bearer token in Authorization header

**Valid Sectors:**
| | | |
|---|---|---|
| pharmaceuticals | technology | agriculture |
| textiles | automobiles | energy |
| finance | healthcare | manufacturing |
| retail | telecommunications | chemicals |

**Example Request:**
```bash
curl -X GET http://localhost:8000/analyze/pharmaceuticals \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Invalid Sector Response (400):**
```json
{
  "error": "Invalid sector",
  "message": "'cricket' is not a supported sector.",
  "valid_sectors": ["pharmaceuticals", "technology", "..."]
}
```

---

## 📋 All Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/` | No | Health check |
| POST | `/token` | No | Get JWT token |
| GET | `/analyze/{sector}` | Yes | Main analysis endpoint |
| GET | `/my-session` | Yes | View your request history |
| GET | `/admin/sessions` | Admin only | View all users sessions |
| GET | `/docs` | No | Swagger UI |

---

## ⚡ Rate Limiting

- **5 requests per minute** per IP address
- Exceeding returns `429 Too Many Requests`:

```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Please wait and try again.",
  "retry_after": "60 seconds"
}
```

---

## 🔒 Security Features

| Feature | Implementation |
|---|---|
| Authentication | JWT Bearer tokens |
| Password Storage | Bcrypt hashed (never plain text) |
| Rate Limiting | 5 requests/minute per IP |
| Input Validation | Whitelisted sectors only |
| Token Expiry | 30 minutes |
| CORS | Enabled for all origins |

---

## 📝 Sample Report Output

```markdown
# 🇮🇳 India Trade Opportunities Report: Pharmaceuticals Sector

## 📊 Executive Summary
India's pharmaceutical sector is a global powerhouse, renowned as the
"pharmacy of the world" due to its robust generic drug manufacturing
capabilities and cost-effective production.

## 📈 Current Market Overview
The Indian pharmaceutical market is currently estimated to be one of the
largest globally by volume, experiencing consistent double-digit growth...

## 🚀 Top Trade Opportunities
1. Generic Drug Manufacturing & Export
2. Active Pharmaceutical Ingredients (APIs)
3. Biosimilars & Complex Generics
4. Contract Research and Manufacturing (CRAMS)
5. Vaccine Production and Global Supply

## 🌍 Export Opportunities
- Key Markets: USA, EU, Africa, ASEAN, Latin America
- Products in Demand: Generic formulations, biosimilars, vaccines
- Competitive Advantages: Cost, scale, regulatory compliance

## 📥 Import Opportunities
- Advanced R&D equipment
- AI/ML platforms for drug discovery
- High-value patented APIs

## ⚠️ Risks & Challenges
1. Increasing Regulatory Scrutiny
2. Dependency on China for Key APIs
3. Intense Price Competition
4. Limited Novel Drug Discovery Investment

## 💡 Strategic Recommendations
1. Strengthen Backward Integration
2. Focus on High-Value Segments
3. Enhance R&D and Innovation
4. Adopt Industry 4.0 Technologies

## 📅 Report Generated
- Sector: Pharmaceuticals
- Market: India
- Data Sources: Live web search + AI analysis
```

---

## 🛑 Stopping the Server

Press **Ctrl + C** in the terminal.

---

## ❓ Common Errors & Fixes

| Error | Fix |
|---|---|
| `pip install` fails | Switch to mobile hotspot |
| `bcrypt` error on startup | `pip uninstall bcrypt -y && pip install bcrypt==4.0.1` |
| `GEMINI_API_KEY missing` | Check your `.env` file has the key |
| `429 Rate limit` from Gemini | Wait 1 minute and try again |
| `ImportError` on startup | Make sure `venv` is activated |
| Server not starting | Make sure you're inside the `trade-api` folder |

---

