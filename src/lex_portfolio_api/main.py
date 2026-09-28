from fastapi import FastAPI

from lex_portfolio_api.routers.auth import router as auth_router
from lex_portfolio_api.routers.profile import router as profile_router

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from lex_portfolio_api.core.limiter import limiter

app = FastAPI(title="Lex Portfolio API")

app.include_router(auth_router)
app.include_router(profile_router)

app.state.limiter = limiter

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get("/")
def health_check():
    return {"status": "Ok"}
