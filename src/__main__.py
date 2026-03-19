"""Entry point for running the backend service."""

import uvicorn


def main():
    """Run the backend service."""
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",  # nosec: B104 - Intentional for Docker deployment
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    main()
