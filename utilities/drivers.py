from axe_selenium_python import Axe
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from typing import Dict, Any


def build_driver(headless: bool = True, implicit_wait: int = 2) -> webdriver.Chrome:
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    # Use Service to pass the ChromeDriver path
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.implicitly_wait(implicit_wait)
    return driver


def run_axe_on_page(driver: webdriver.Chrome, url: str, wait_seconds: int = 5) -> Dict[str, Any]:
    try:
        driver.get(url)
        # Wait until at least the <body> element exists
        WebDriverWait(driver, wait_seconds).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        axe = Axe(driver)
        axe.inject()
        results = axe.run()
        return {"ok": True, "url": url, "results": results}
    except Exception as e:
        return {"ok": False, "url": url, "error": str(e)}
