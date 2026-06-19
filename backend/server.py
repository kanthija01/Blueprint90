"""Uvicorn entrypoint. The real app construction lives in `app_factory`.
"""
from __future__ import annotations

import logging

from dotenv import load_dotenv

load_dotenv()

from app_factory import create_app  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

app = create_app()
