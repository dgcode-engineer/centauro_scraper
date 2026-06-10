from __future__ import annotations

import os

import undetected_chromedriver as uc


def create_driver(version_main: int = 147) -> uc.Chrome:
    options = uc.ChromeOptions()
    if os.getenv("HEADLESS", "").lower() in ("1", "true", "yes"):
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
    return uc.Chrome(options=options, version_main=version_main)
