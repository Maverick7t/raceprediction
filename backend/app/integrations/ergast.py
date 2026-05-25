"""
Ergast / Jolpica REST client.
 
Ergast is the authoritative source for:
  - Race results (final classification)
  - Qualifying results (positions, Q1/Q2/Q3 times)
  - Driver and constructor standings
 
Rate limiting: Ergast enforces ~200 requests per hour.
This client uses exponential backoff on 429 responses and
a conservative per-request timeout of 10 seconds.
 
Base URL is configurable via ERGAST_BASE_URL env var.
Jolpica (https://api.jolpi.ca/ergast) is the recommended host —
it is a maintained fork of the original Ergast service.
"""
 
import time
from typing import Optional
 
import pandas as pd
import requests
 
from app.core.config import config
from app.core.exceptions import IngestionError
from app.core.logging import get_logger
 
logger = get_logger(__name__)
 
_TIMEOUT = 10        # seconds per request
_MAX_RETRIES = 3
_BACKOFF_BASE = 2.0  # seconds; doubles per retry: 2s, 4s, 8s
 
 
class ErgastClient:
 
    def __init__(self, base_url: str = None):
        self.base_url = (base_url or config.ERGAST_BASE_URL).rstrip("/")
        self._session = requests.Session()
        self._session.headers.update({"Accept": "application/json"})