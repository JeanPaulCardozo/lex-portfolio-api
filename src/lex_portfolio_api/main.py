from fastapi import FastAPI

from lex_portfolio_api.routers.auth import router as auth_router
from lex_portfolio_api.routers.profile import router as profile_router
from lex_portfolio_api.routers.practice_area import router as practice_area_router
from lex_portfolio_api.routers.case import router as case_router
from lex_portfolio_api.routers.experience import router as experience_router
from lex_portfolio_api.routers.publication import router as publication_router

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from lex_portfolio_api.core.limiter import limiter

app = FastAPI(title="Lex Portfolio API")

for router in (
    auth_router,
    profile_router,
    practice_area_router,
    case_router,
    experience_router,
    publication_router,
):
    app.include_router(router)

app.state.limiter = limiter

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get("/")
def health_check():
    return {"status": "Ok"}
