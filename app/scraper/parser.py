from __future__ import annotations

import re

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement


def parse_preco(texto: str) -> float | None:
    if not texto:
        return None
    m = re.search(r"([\d.]+,\d{2})", texto)
    if not m:
        return None
    return float(m.group(1).replace(".", "").replace(",", "."))


def extrair_preco(driver: WebDriver, container: WebElement) -> dict:
    def texto_ou_none(testid: str) -> str | None:
        els = container.find_elements(By.CSS_SELECTOR, f'[data-testid="{testid}"]')
        return els[0].text.strip() if els else None

    atual_raw = None
    els = container.find_elements(By.CSS_SELECTOR, '[data-testid="price-current"]')
    if els:
        atual_raw = driver.execute_script(
            "return arguments[0].childNodes[0].textContent;", els[0]
        ).strip()

    antigo_raw = texto_ou_none("price-promotion")
    desconto_raw = texto_ou_none("price-discount")
    parcelamento_raw = texto_ou_none("price-installment")
    tem_pix = bool(container.find_elements(By.CSS_SELECTOR, '[data-testid="pix-label"]'))

    return {
        "preco_antigo": parse_preco(antigo_raw),
        "preco_atual": parse_preco(atual_raw),
        "no_pix": tem_pix,
        "desconto_pct": int(re.sub(r"\D", "", desconto_raw)) if desconto_raw else None,
        "parcelamento": parcelamento_raw,
    }
