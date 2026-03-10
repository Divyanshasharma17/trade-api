import logging
from datetime import timedelta

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from config import ACCESS_TOKEN_EXPIRE_MINUTES, VALID_SECTORS
from auth import authenticate_user, create_access_token, get_current_user, Token, User
from rate_limiter import limiter, rate_limit_exceeded_handler
from data_collector import collect_market_data, format_data_for_prompt
from analyzer import analyze_sector
from session_store import log_request, get_session, get_all_sessions


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="🇮🇳 Trade Opportunities API",
    description="""
## India Trade Opportunities Analysis API

Analyze market data and discover trade opportunities for specific sectors in India.

### How to Use
1. **Get a token**: `POST /token` with username/password
2. **Analyze a sector**: `GET /analyze/{sector}` with Bearer token

### Default Credentials
- `admin` / `admin123`
- `guest` / `guest123`

### Valid Sectors
pharmaceuticals, technology, agriculture, textiles, automobiles,
energy, finance, healthcare, manufacturing, retail, telecommunications, chemicals
    """,
    version="1.0.0",
)


app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {
        "status": "✅ API is running",
        "message": "Welcome to India Trade Opportunities API",
        "docs": "/docs",
        "valid_sectors": VALID_SECTORS,
    }


@app.post("/token", response_model=Token, tags=["Authentication"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login to get a JWT access token.

    - **username**: your username
    - **password**: your password

    Default users: `admin/admin123` or `guest/guest123`
    """
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    logger.info(f"🔑 Token issued for user: {user['username']}")
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/analyze/{sector}", tags=["Analysis"])
@limiter.limit("5/minute")  
async def analyze_trade_opportunities(
    sector: str,
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """
    **Main endpoint** — Analyze trade opportunities for a sector in India.

    Returns a detailed markdown report with:
    - Market overview
    - Export/import opportunities
    - Risks and challenges
    - Strategic recommendations

    **Rate limit**: 5 requests per minute per IP

    **Valid sectors**: pharmaceuticals, technology, agriculture, textiles,
    automobiles, energy, finance, healthcare, manufacturing, retail,
    telecommunications, chemicals
    """
    
    sector_clean = sector.lower().strip()

    if sector_clean not in VALID_SECTORS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Invalid sector",
                "message": f"'{sector}' is not a supported sector.",
                "valid_sectors": VALID_SECTORS,
                "example": "/analyze/pharmaceuticals",
            },
        )

    logger.info(f"📊 Analysis requested | sector={sector_clean} | user={current_user.username}")

    
    try:
        raw_data = collect_market_data(sector_clean)
        formatted_data = format_data_for_prompt(raw_data)
        logger.info(f"✅ Data collected for {sector_clean}")
    except Exception as e:
        logger.error(f"❌ Data collection failed: {e}")
        formatted_data = f"SECTOR: {sector_clean.upper()}\nNo live data available. Use general knowledge."

   
    try:
        report = analyze_sector(sector_clean, formatted_data)
        success = True
        logger.info(f"✅ Report generated for {sector_clean}")
    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")
        report = f"# Analysis Failed\n\nError: {str(e)}\n\nPlease try again later."
        success = False

    
    log_request(
        username=current_user.username,
        sector=sector_clean,
        success=success,
    )

    
    return PlainTextResponse(
        content=report,
        media_type="text/markdown",
        headers={
            "X-Sector": sector_clean,
            "X-User": current_user.username,
            "X-Report-Type": "trade-analysis",
        },
    )


@app.get("/my-session", tags=["Session"])
async def my_session(current_user: User = Depends(get_current_user)):
    """View your own API usage session."""
    session = get_session(current_user.username)
    if not session:
        return {"message": "No requests made yet.", "username": current_user.username}
    return session


@app.get("/admin/sessions", tags=["Admin"])
async def all_sessions(current_user: User = Depends(get_current_user)):
    """View all user sessions. Admin only."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )
    return get_all_sessions()
