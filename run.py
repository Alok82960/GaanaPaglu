"""Quick start script for GaanaPaglu."""

import os
import uvicorn
from app.config import get_settings

settings = get_settings()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", settings.port))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info",
    )
