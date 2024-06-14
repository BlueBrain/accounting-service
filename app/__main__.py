"""Main entry point."""

import uvicorn

from app.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.application:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        proxy_headers=True,
        log_config=settings.LOGGING_CONFIG,
        reload=settings.APP_RELOAD,
    )
