import sys
import os
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# Load .env configuration
load_dotenv()

# Logging setup
LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# Directory for saving screenshots and HTML artifacts
ARTIFACTS_DIR = Path(os.getenv("ARTIFACTS_DIR", "artifacts"))
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

def _save_artifacts(page, prefix="failure"):
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    base = ARTIFACTS_DIR / f"{prefix}-{ts}"
    artifacts = {}

    try:
        screenshot_path = str(base.with_suffix(".png"))
        page.screenshot(path=screenshot_path, full_page=True)
        artifacts["screenshot"] = screenshot_path
    except Exception as e:
        LOG.exception("Failed to take screenshot: %s", e)

    try:
        html_path = str(base.with_suffix(".html"))
        html = page.content()
        with open(html_path, "w", encoding="utf-8") as fh:
            fh.write(html)
        artifacts["html"] = html_path
    except Exception as e:
        LOG.exception("Failed to save page HTML: %s", e)

    return artifacts

def run_automation() -> dict:
    """
    Automates login to SauceDemo and retrieves the price of a product.

    Configurable via:
      - SAUCE_USER, SAUCE_PASS
      - ITEM_TO_LOOKUP
      - HEADLESS (true/false)
    """
    username = os.getenv("SAUCE_USER", "standard_user")
    password = os.getenv("SAUCE_PASS", "secret_sauce")
    item_to_lookup = os.getenv("ITEM_TO_LOOKUP", "Sauce Labs Backpack")
    headless = os.getenv("HEADLESS", "true").lower() == "true"

    LOG.info("=== Starting SauceDemo automation ===")
    LOG.info(f"Using credentials: {username}/********")
    LOG.info(f"Item to lookup: {item_to_lookup}")
    LOG.info(f"Headless mode: {headless}")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)
            context = browser.new_context()
            page = context.new_page()

            LOG.info("Navigating to saucedemo.com ...")
            page.goto("https://www.saucedemo.com/", timeout=15000)

            # Login
            page.fill("#user-name", username)
            page.fill("#password", password)
            page.click("#login-button")

            try:
                page.wait_for_selector(".inventory_list", timeout=7000)
            except PlaywrightTimeoutError:
                err_el = page.query_selector('[data-test="error"]')
                if err_el:
                    msg = err_el.inner_text().strip()
                    LOG.error("Login error detected: %s", msg)
                    art = _save_artifacts(page, prefix="login-error")
                    return {"status": "error", "message": f"Login failed: {msg}", "artifacts": art}

                LOG.error("Timed out waiting for inventory list.")
                art = _save_artifacts(page, prefix="timeout")
                return {"status": "error", "message": "Login timed out or page failed to load", "artifacts": art}

            # Modular product lookup
            LOG.info(f"Searching for item: {item_to_lookup}")
            item_locator = page.locator(".inventory_item", has_text=item_to_lookup)

            try:
                item_locator.first.wait_for(state="visible", timeout=5000)
            except PlaywrightTimeoutError:
                LOG.error("Item not found: %s", item_to_lookup)
                art = _save_artifacts(page, prefix="item-not-found")
                return {"status": "error", "message": f"Product not found: {item_to_lookup}", "artifacts": art}

            # Extract price
            price_locator = item_locator.locator(".inventory_item_price").first
            price_text = price_locator.inner_text().strip()

            LOG.info("Found price for %s: %s", item_to_lookup, price_text)
            return {"status": "success", "product": item_to_lookup, "price": price_text}

    except PlaywrightTimeoutError:
        LOG.exception("Playwright timeout")
        return {"status": "error", "message": "Page took too long to load"}

    except Exception as e:
        LOG.exception("Unhandled exception in automation: %s", e)
        try:
            if "page" in locals():
                art = _save_artifacts(page, prefix="exception")
                return {"status": "error", "message": str(e), "artifacts": art}
        except Exception:
            LOG.exception("Failed to save artifacts after exception")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    result = run_automation()
    print(json.dumps(result))
    sys.exit(0 if result.get("status") == "success" else 1)
