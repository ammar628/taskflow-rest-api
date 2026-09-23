import uvicorn
from src.app.logging_config import setup_logging

setup_logging()

if __name__ == "__main__":
    uvicorn.run(
        "src.app.app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )