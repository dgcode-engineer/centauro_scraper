from __future__ import annotations

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from app.core.logger import logger
from app.models.product import Product
from app.scraper.parser import extrair_preco

BASE_URL = "https://www.centauro.com.br/busca/"


def _check_cookie_alert(driver: WebDriver) -> None:
    alert = driver.find_elements(
        By.XPATH,
        "//*[starts-with(normalize-space(.),'Utilizamos cookies para auxiliar a sua navegação.')]",
    )
    if alert:
        driver.find_element(By.XPATH, "//*[normalize-space()='Aceitar']").click()


def run_scrape(driver: WebDriver, query: str, pages: int = 1) -> list[Product]:
    slug = query.replace(" ", "-")
    products: list[Product] = []

    for page in range(1, pages + 1):
        logger.info("Acessando página", query=query, page=page)
        driver.get(f"{BASE_URL}{slug}?page={page}")
        _check_cookie_alert(driver)
        products.extend(_scrape_page(driver))

    logger.info("Scraping concluído", total=len(products))
    return products


def _scrape_page(driver: WebDriver) -> list[Product]:
    cards = driver.find_elements(
        By.XPATH, "//div[@data-testid='grid-product-card-enhanced']"
    )
    rows: list[Product] = []

    for card in cards:
        try:
            nome_els = card.find_elements(By.XPATH, ".//span[@data-testid='product-name']")
            nome = nome_els[0].text.strip() if nome_els else None

            image_els = card.find_elements(
                By.XPATH, ".//div[@data-testid='product-card-image-area']//img"
            )
            image = image_els[0].get_attribute("src") if image_els else None

            link_els = card.find_elements(By.TAG_NAME, "a")
            link = link_els[0].get_attribute("href") if link_els else None

            tags_els = card.find_elements(
                By.XPATH, ".//div[@data-testid='product-options-tags']"
            )
            tags = tags_els[0].text if tags_els else None

            price_container = card.find_elements(
                By.XPATH, ".//section[@data-testid='price-container']"
            )
            price_info = extrair_preco(driver, price_container[0]) if price_container else {}

            rows.append(
                Product(
                    nome=nome,
                    image=image,
                    link=link,
                    tags=tags,
                    preco_atual=price_info.get("preco_atual"),
                    preco_antigo=price_info.get("preco_antigo"),
                    desconto_pct=price_info.get("desconto_pct"),
                    no_pix=price_info.get("no_pix"),
                    parcelamento=price_info.get("parcelamento"),
                )
            )
        except Exception as ex:
            logger.warning("Erro ao extrair card", error=str(ex))

    return rows
